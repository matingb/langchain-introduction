from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from llm import agent
from prompts.prompt import build_initial_recommendation_messages
from schemas.team import TeamRecommendation, TeamRequest

load_dotenv()

app = FastAPI(title="PokéCoach API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)


@app.post("/recommend-team", response_model=TeamRecommendation)
async def recommend_team(request: TeamRequest) -> TeamRecommendation:
    try:
        return await agent.invoke(build_initial_recommendation_messages(request.available_pokemon, request.leader_to_beat))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
