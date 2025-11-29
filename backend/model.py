import math
import os
import numpy as np
import pandas as pd
from datetime import datetime

# Constants
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
MATCH_PATH = os.path.join(DATA_DIR, "matches_1930_2022.csv")
RANK_PATH = os.path.join(DATA_DIR, "fifa_ranking_2022-10-06.csv")
HOSTS_2026 = {"United States", "Mexico", "Canada"}
HOST_BOOST = 70.0

class WorldCupModel:
    def __init__(self):
        self.matches = None
        self.fifa_rank = None
        self.elo_ratings = {}
        self.rank_points = {}
        self.rank_min = 0
        self.rank_max = 0
        self.draw_rate = 0.25
        self.load_data()
        self.train_elo()

    def load_data(self):
        self.matches = pd.read_csv(MATCH_PATH)
        self.fifa_rank = pd.read_csv(RANK_PATH)

        self.matches["Date"] = pd.to_datetime(self.matches["Date"])
        self.matches = self.matches.sort_values("Date").reset_index(drop=True)
        self.matches["result"] = np.where(
            self.matches["home_score"] > self.matches["away_score"],
            1.0,
            np.where(self.matches["home_score"] < self.matches["away_score"], 0.0, 0.5),
        )

        self.draw_rate = float((self.matches["result"] == 0.5).mean())
        self.rank_points = self.fifa_rank.set_index("team")["points"].to_dict()
        if self.rank_points:
            self.rank_min, self.rank_max = min(self.rank_points.values()), max(self.rank_points.values())

    def fallback_rating(self, team: str, base: float = 1500.0) -> float:
        pts = self.rank_points.get(team)
        if pts is None:
            return base
        return float(np.interp(pts, (self.rank_min, self.rank_max), (1400.0, 1900.0)))

    def train_elo(
        self,
        base_rating: float = 1500.0,
        k_base: float = 40.0,
        decay_years: float = 20.0,
        home_adv: float = 60.0,
    ):
        ratings: dict[str, float] = {}
        current_year = int(self.matches["Date"].dt.year.max())
        
        for row in self.matches.itertuples():
            ht, at = row.home_team, row.away_team
            ratings.setdefault(ht, base_rating)
            ratings.setdefault(at, base_rating)

            ra, rb = ratings[ht], ratings[at]
            year = row.Date.year
            k = k_base * math.exp(-(current_year - year) / decay_years) + 10.0
            margin = max(1.0, math.log1p(abs(row.home_score - row.away_score)))

            exp_home = 1.0 / (1.0 + 10 ** (-(ra + home_adv - rb) / 400.0))
            result_home = 1.0 if row.home_score > row.away_score else 0.5 if row.home_score == row.away_score else 0.0

            delta = k * margin
            ratings[ht] += delta * (result_home - exp_home)
            ratings[at] += delta * ((1.0 - result_home) - (1.0 - exp_home))

        mean_rating = float(np.mean(list(ratings.values())))
        shift = base_rating - mean_rating
        self.elo_ratings = {team: rating + shift for team, rating in ratings.items()}

    def rating_for(self, team: str) -> float:
        return float(self.elo_ratings.get(team, self.fallback_rating(team)))

    def draw_probability(self, rating_diff: float, draw_scale: float = 450.0) -> float:
        return float(self.draw_rate * math.exp(-abs(rating_diff) / draw_scale))

    def predict_match(self, team_a: str, team_b: str, host: str | None = None) -> dict:
        ra, rb = self.rating_for(team_a), self.rating_for(team_b)
        boost_a = HOST_BOOST if host == team_a else 0.0
        boost_b = HOST_BOOST if host == team_b else 0.0

        rating_diff = (ra + boost_a) - (rb + boost_b)
        expected_a = 1.0 / (1.0 + 10 ** (-rating_diff / 400.0))

        p_draw = self.draw_probability(rating_diff)
        p_a = expected_a * (1.0 - p_draw)
        p_b = (1.0 - expected_a) * (1.0 - p_draw)

        return {
            "team_a": team_a,
            "team_b": team_b,
            "team_a_win": p_a,
            "draw": p_draw,
            "team_b_win": p_b,
            "rating_a": ra,
            "rating_b": rb,
            "rating_diff": rating_diff,
            "host": host or "neutral",
        }

    def simulate_match(self, team_a: str, team_b: str, rng: np.random.Generator) -> str:
        host = team_a if team_a in HOSTS_2026 else team_b if team_b in HOSTS_2026 else None
        pred = self.predict_match(team_a, team_b, host=host)
        roll = rng.random()
        if roll < pred["team_a_win"]:
            return team_a
        if roll < pred["team_a_win"] + pred["draw"]:
            strength_a = pred["team_a_win"]
            strength_b = pred["team_b_win"]
            total = max(1e-9, strength_a + strength_b)
            return team_a if rng.random() < strength_a / total else team_b
        return team_b

    def pair_and_play(self, teams: list[str], rng: np.random.Generator) -> list[str]:
        rng.shuffle(teams)
        winners = []
        for i in range(0, len(teams), 2):
            if i + 1 < len(teams):
                winners.append(self.simulate_match(teams[i], teams[i + 1], rng))
            else:
                winners.append(teams[i]) # Odd number of teams, bye
        return winners

    def simulate_tournament(self, n_iter: int = 1000, random_state: int = 7) -> list[dict]:
        # Get top 48 teams
        team_pool = self.fifa_rank.sort_values("points", ascending=False).head(48)["team"].tolist()
        
        seeded = (
            pd.DataFrame(
                [{"team": t, "rating": self.rating_for(t)} for t in team_pool]
            )
            .sort_values("rating", ascending=False)
            .reset_index(drop=True)
        )
        top16 = seeded.head(16)["team"].tolist()
        prelim_field = seeded["team"].tolist()[16:]

        rng = np.random.default_rng(random_state)
        counts: dict[str, int] = {}
        
        for _ in range(n_iter):
            prelim_winners = self.pair_and_play(prelim_field.copy(), rng)
            round_of_32 = top16 + prelim_winners
            rng.shuffle(round_of_32)

            current = round_of_32
            while len(current) > 1:
                current = self.pair_and_play(current, rng)
            champion = current[0]
            counts[champion] = counts.get(champion, 0) + 1

        results = [
            {"team": t, "title_prob": wins / n_iter} for t, wins in counts.items()
        ]
        results.sort(key=lambda x: x["title_prob"], reverse=True)
        return results

    def get_all_teams(self) -> list[str]:
        # Return all teams that have a rating or ranking
        teams = set(self.elo_ratings.keys()) | set(self.rank_points.keys())
        return sorted(list(teams))

# Singleton instance
model = WorldCupModel()
