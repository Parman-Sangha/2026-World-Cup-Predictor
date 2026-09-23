import math
import os
import numpy as np
import pandas as pd

# Constants
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
RESULTS_PATH = os.path.join(DATA_DIR, "results.csv")

# Only train on matches played before the tournament kicked off, so the
# predictions are genuine pre-tournament forecasts.
CUTOFF = "2026-06-11"

HOSTS_2026 = {"United States", "Mexico", "Canada"}
HOME_ADV = 100.0

# K-factor by competition (World Football Elo convention).
K_WORLD_CUP = 60.0
K_CONTINENTAL = 50.0
K_QUALIFIER = 40.0
K_OTHER = 30.0
K_FRIENDLY = 20.0
CONTINENTAL_FINALS = {
    "UEFA Euro", "Copa América", "African Cup of Nations", "AFC Asian Cup",
    "Gold Cup", "CONCACAF Championship", "Oceania Nations Cup", "Confederations Cup",
}

# Official 2026 draw.
GROUPS_2026 = {
    "A": ["Mexico", "South Africa", "South Korea", "Czech Republic"],
    "B": ["Canada", "Bosnia and Herzegovina", "Qatar", "Switzerland"],
    "C": ["Brazil", "Morocco", "Haiti", "Scotland"],
    "D": ["United States", "Paraguay", "Australia", "Turkey"],
    "E": ["Germany", "Curaçao", "Ivory Coast", "Ecuador"],
    "F": ["Netherlands", "Japan", "Sweden", "Tunisia"],
    "G": ["Belgium", "Egypt", "Iran", "New Zealand"],
    "H": ["Spain", "Cape Verde", "Saudi Arabia", "Uruguay"],
    "I": ["France", "Senegal", "Iraq", "Norway"],
    "J": ["Argentina", "Algeria", "Austria", "Jordan"],
    "K": ["Portugal", "DR Congo", "Uzbekistan", "Colombia"],
    "L": ["England", "Croatia", "Ghana", "Panama"],
}

# Round of 32 (matches 73-88). "1A" = winner of group A, "2A" = runner-up,
# "3:ABCDF" = one of the best third-placed teams from those groups.
ROUND_OF_32 = [
    ("2A", "2B"), ("1E", "3:ABCDF"), ("1F", "2C"), ("1C", "2F"),
    ("1I", "3:CDFGH"), ("2E", "2I"), ("1A", "3:CEFHI"), ("1L", "3:EHIJK"),
    ("1D", "3:BEFIJ"), ("1G", "3:AEHIJ"), ("2K", "2L"), ("1H", "2J"),
    ("1B", "3:EFGIJ"), ("1J", "2H"), ("1K", "3:DEIJL"), ("2D", "2G"),
]
# Later rounds as pairs of indexes into the previous round's winners.
ROUND_OF_16 = [(1, 4), (0, 2), (3, 5), (6, 7), (10, 11), (8, 9), (13, 15), (12, 14)]
QUARTERS = [(0, 1), (4, 5), (2, 3), (6, 7)]
SEMIS = [(0, 1), (2, 3)]

STAGES = ["round_of_32", "round_of_16", "quarterfinal", "semifinal", "final", "champion"]


def k_factor(tournament: str) -> float:
    if tournament == "FIFA World Cup":
        return K_WORLD_CUP
    if tournament in CONTINENTAL_FINALS:
        return K_CONTINENTAL
    if "qualification" in tournament or tournament == "UEFA Nations League":
        return K_QUALIFIER
    if tournament == "Friendly":
        return K_FRIENDLY
    return K_OTHER


def goal_multiplier(goal_diff: int) -> float:
    n = abs(goal_diff)
    if n <= 1:
        return 1.0
    if n == 2:
        return 1.5
    return (11.0 + n) / 8.0


class WorldCupModel:
    def __init__(self, cutoff: str = CUTOFF):
        self.cutoff = cutoff
        self.matches = None
        self.elo_ratings = {}
        self.recent_teams = set()
        # Ordered-logit outcome model, fitted in fit_outcome_model().
        self.draw_margin = 60.0
        self.scale = 400.0
        self.load_data()
        self.train_elo()
        self.fit_outcome_model()

    def load_data(self):
        df = pd.read_csv(RESULTS_PATH, parse_dates=["date"])
        df = df.dropna(subset=["home_score", "away_score"])
        df = df[df["date"] < self.cutoff].sort_values("date").reset_index(drop=True)
        df["home_score"] = df["home_score"].astype(int)
        df["away_score"] = df["away_score"].astype(int)
        self.matches = df

        # Teams active in the last 8 years; keeps defunct and non-FIFA sides out of the picker.
        recent = df[df["date"] >= pd.Timestamp(self.cutoff) - pd.DateOffset(years=8)]
        counts = pd.concat([recent["home_team"], recent["away_team"]]).value_counts()
        self.recent_teams = set(counts[counts >= 10].index)

    def train_elo(self, base_rating: float = 1500.0):
        ratings: dict[str, float] = {}
        pre_diffs = np.empty(len(self.matches))

        for i, row in enumerate(self.matches.itertuples()):
            ht, at = row.home_team, row.away_team
            ra = ratings.setdefault(ht, base_rating)
            rb = ratings.setdefault(at, base_rating)

            diff = ra - rb + (0.0 if row.neutral else HOME_ADV)
            pre_diffs[i] = diff
            exp_home = 1.0 / (1.0 + 10 ** (-diff / 400.0))
            result_home = 1.0 if row.home_score > row.away_score else 0.5 if row.home_score == row.away_score else 0.0

            delta = k_factor(row.tournament) * goal_multiplier(row.home_score - row.away_score) * (result_home - exp_home)
            ratings[ht] += delta
            ratings[at] -= delta

        self.elo_ratings = ratings
        self.matches["elo_diff"] = pre_diffs

    def fit_outcome_model(self):
        """Fit draw margin and scale by minimising log loss on competitive matches since 2010."""
        m = self.matches
        m = m[(m["date"] >= "2010-01-01") & (m["tournament"] != "Friendly")]
        d = m["elo_diff"].to_numpy()
        outcome = np.sign(m["home_score"].to_numpy() - m["away_score"].to_numpy())

        best = None
        for scale in np.arange(300.0, 601.0, 10.0):
            for margin in np.arange(20.0, 151.0, 5.0):
                pa, pd_, pb = self._outcome_probs(d, margin, scale)
                p = np.where(outcome > 0, pa, np.where(outcome < 0, pb, pd_))
                loss = -np.mean(np.log(np.clip(p, 1e-12, None)))
                if best is None or loss < best[0]:
                    best = (loss, margin, scale)
        _, self.draw_margin, self.scale = best

    @staticmethod
    def _outcome_probs(diff, margin, scale):
        pa = 1.0 / (1.0 + 10 ** (-(diff - margin) / scale))
        pb = 1.0 / (1.0 + 10 ** ((diff + margin) / scale))
        return pa, 1.0 - pa - pb, pb

    def rating_for(self, team: str) -> float:
        if team not in self.elo_ratings:
            raise ValueError(f"Unknown team: {team}")
        return float(self.elo_ratings[team])

    def predict_match(self, team_a: str, team_b: str, host: str | None = None) -> dict:
        ra, rb = self.rating_for(team_a), self.rating_for(team_b)
        boost_a = HOME_ADV if host == team_a else 0.0
        boost_b = HOME_ADV if host == team_b else 0.0

        rating_diff = (ra + boost_a) - (rb + boost_b)
        p_a, p_draw, p_b = self._outcome_probs(rating_diff, self.draw_margin, self.scale)

        return {
            "team_a": team_a,
            "team_b": team_b,
            "team_a_win": float(p_a),
            "draw": float(p_draw),
            "team_b_win": float(p_b),
            "rating_a": ra,
            "rating_b": rb,
            "rating_diff": rating_diff,
            "host": host or "neutral",
        }

    def _host_for(self, team_a: str, team_b: str) -> str | None:
        # Hosts play all their matches at home; a host-vs-host tie is treated as neutral.
        if team_a in HOSTS_2026 and team_b not in HOSTS_2026:
            return team_a
        if team_b in HOSTS_2026 and team_a not in HOSTS_2026:
            return team_b
        return None

    @staticmethod
    def _assign_thirds(slots: list[str], groups: list[str]) -> dict[str, str] | None:
        """Match each third-place slot to a qualifying group it allows (backtracking)."""
        if not slots:
            return {}
        slot, rest = slots[0], slots[1:]
        for g in groups:
            if g in slot:
                sub = WorldCupModel._assign_thirds(rest, [x for x in groups if x != g])
                if sub is not None:
                    return {slot: g, **sub}
        return None

    def simulate_tournament(self, n_iter: int = 10000, random_state: int = 7) -> list[dict]:
        teams = [t for group in GROUPS_2026.values() for t in group]
        idx = {t: i for i, t in enumerate(teams)}

        # Precompute (win, draw) probabilities for every pairing.
        n = len(teams)
        p_win = np.zeros((n, n))
        p_draw = np.zeros((n, n))
        for a in teams:
            for b in teams:
                if a != b:
                    pred = self.predict_match(a, b, host=self._host_for(a, b))
                    p_win[idx[a], idx[b]] = pred["team_a_win"]
                    p_draw[idx[a], idx[b]] = pred["draw"]

        rng = np.random.default_rng(random_state)
        reached = np.zeros((n, len(STAGES)))

        def knockout(a: int, b: int) -> int:
            roll = rng.random()
            if roll < p_win[a, b]:
                return a
            if roll < p_win[a, b] + p_draw[a, b]:
                return a if rng.random() < 0.5 else b  # extra time / penalties
            return b

        for _ in range(n_iter):
            placed = {}
            thirds = []
            for letter, group in GROUPS_2026.items():
                ids = [idx[t] for t in group]
                pts = {i: 0.0 for i in ids}
                for x in range(4):
                    for y in range(x + 1, 4):
                        a, b = ids[x], ids[y]
                        roll = rng.random()
                        if roll < p_win[a, b]:
                            pts[a] += 3
                        elif roll < p_win[a, b] + p_draw[a, b]:
                            pts[a] += 1
                            pts[b] += 1
                        else:
                            pts[b] += 3
                # Random jitter stands in for goal-difference tiebreakers.
                order = sorted(ids, key=lambda i: pts[i] + rng.random() * 0.5, reverse=True)
                placed[f"1{letter}"], placed[f"2{letter}"] = order[0], order[1]
                thirds.append((pts[order[2]] + rng.random() * 0.5, letter, order[2]))

            thirds.sort(reverse=True)
            best_thirds = {letter: team for _, letter, team in thirds[:8]}
            third_slots = [b for _, b in ROUND_OF_32 if b.startswith("3:")]
            assignment = self._assign_thirds(third_slots, sorted(best_thirds))
            for slot, letter in assignment.items():
                placed[slot] = best_thirds[letter]

            current = [(placed[a], placed[b]) for a, b in ROUND_OF_32]
            for a, b in current:
                reached[[a, b], 0] += 1
            winners = [knockout(a, b) for a, b in current]
            for stage, bracket in enumerate([ROUND_OF_16, QUARTERS, SEMIS, [(0, 1)]], start=1):
                reached[winners, stage] += 1
                winners = [knockout(winners[i], winners[j]) for i, j in bracket]
            reached[winners[0], 5] += 1

        results = []
        for t in teams:
            row = {"team": t, "group": next(g for g, ts in GROUPS_2026.items() if t in ts)}
            for s, stage in enumerate(STAGES):
                row[stage] = float(reached[idx[t], s] / n_iter)
            row["title_prob"] = row["champion"]
            results.append(row)
        results.sort(key=lambda x: x["title_prob"], reverse=True)
        return results

    def get_all_teams(self) -> list[str]:
        return sorted(self.recent_teams & set(self.elo_ratings))


# Singleton instance
model = WorldCupModel()
