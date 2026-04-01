from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from llm import get_team_recommendation
from models import TeamRecommendation, TeamRequest
from rag import init_vectorstore

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_vectorstore()
    yield


app = FastAPI(title="PokéCoach API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)


@app.post("/recommend-team", response_model=TeamRecommendation)
async def recommend_team(request: TeamRequest) -> TeamRecommendation:
    try:
        return await get_team_recommendation(request)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
