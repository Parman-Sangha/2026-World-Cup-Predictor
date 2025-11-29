from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from model import model

app = FastAPI(title="2026 World Cup Predictor")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MatchRequest(BaseModel):
    team_a: str
    team_b: str
    host: Optional[str] = None

class MatchResponse(BaseModel):
    team_a: str
    team_b: str
    team_a_win: float
    draw: float
    team_b_win: float
    rating_a: float
    rating_b: float
    rating_diff: float
    host: str

class SimulationResponse(BaseModel):
    team: str
    title_prob: float

@app.get("/teams", response_model=List[str])
def get_teams():
    return model.get_all_teams()

@app.post("/predict", response_model=MatchResponse)
def predict_match(request: MatchRequest):
    try:
        result = model.predict_match(request.team_a, request.team_b, request.host)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/simulate", response_model=List[SimulationResponse])
def simulate_tournament(n_iter: int = 1000):
    try:
        return model.simulate_tournament(n_iter=n_iter)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"message": "Welcome to the 2026 World Cup Predictor API"}
