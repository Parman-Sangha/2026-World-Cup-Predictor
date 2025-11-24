# 2026 World Cup Predictor

About
- Builds an Elo-style rating model from all World Cup matches (1930–2022) plus October 2022 FIFA rankings as a fallback for teams with sparse history.
- Provides match win/draw/loss probabilities, group-stage expected points, and a Monte Carlo knockout simulator for projected 2026 winners.
- Lightweight, local-only: just Python with pandas/numpy (see `World-Cup-T.ipynb`).

Data
- `Data/matches_1930_2022.csv`: historical World Cup match results.
- `Data/fifa_ranking_2022-10-06.csv`: FIFA points used for fallback ratings and 2026 qualifying pool.
- `Data/world_cup.csv`: tournament metadata (not required for the core model).

Run it
- Open `World-Cup-T.ipynb` and run all cells in order.
- Key functions: `predict_match(team_a, team_b, host=...)`, `project_group([...], host=...)`, `simulate_tournament(team_pool_2026, n_iter=...)`.
- Adjust `HOST_BOOST` (host advantage) or `n_iter` (simulations) inside the notebook to explore different scenarios.

Notes
- Hosts assumed for 2026: USA, Mexico, Canada. Change `HOSTS_2026` in the notebook if needed.
- Results are probabilistic and depend on the rating assumptions; increase simulations for smoother title odds.
