# 2026 World Cup Predictor

About
- Web app (FastAPI backend in `backend/`, React frontend in `frontend/`) that predicts matches and simulates the 2026 World Cup.
- Elo ratings trained on ~49,000 men's international matches (1872 to 10 June 2026, the day before kickoff), weighted by competition (World Cup > continental finals > qualifiers > friendlies) and margin of victory.
- Win/draw/loss probabilities come from an ordered-logit model fitted to competitive matches since 2010.
- Tournament simulator uses the real 2026 format: the 12 official groups, top two plus the 8 best third-placed teams, and the official Round of 32 bracket. Hosts get home advantage.
- Backtest on the 104 actual 2026 World Cup matches: picks the correct result 68% of the time (log loss 0.85), up from 52% (1.05) for the original World-Cup-only model. Pre-tournament favourites were Spain (22%) and Argentina (17%), the two finalists.

Run the app
- Backend: `cd backend && ../venv/bin/python -m uvicorn main:app --port 8000`
- Frontend: `cd frontend && npm install && npm run dev`, then open http://localhost:5173

Data
- `backend/data/results.csv`: international results from https://github.com/martj42/international_results (used by the app).
- `Data/matches_1930_2022.csv`: historical World Cup match results.
- `Data/fifa_ranking_2022-10-06.csv`: FIFA points used for fallback ratings and 2026 qualifying pool.
- `Data/world_cup.csv`: tournament metadata (not required for the core model).

Notebook
- Open `World-Cup-T.ipynb` and run all cells in order.
- Key functions: `predict_match(team_a, team_b, host=...)`, `project_group([...], host=...)`, `simulate_tournament(team_pool_2026, n_iter=...)`.
- Adjust `HOST_BOOST` (host advantage) or `n_iter` (simulations) inside the notebook to explore different scenarios.

Notes
- Hosts assumed for 2026: USA, Mexico, Canada. Change `HOSTS_2026` in the notebook if needed.
- Results are probabilistic and depend on the rating assumptions; increase simulations for smoother title odds.
