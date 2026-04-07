import os
from functools import lru_cache
from typing import Annotated, List, TypedDict

from langchain_core.messages import BaseMessage
from langchain_groq import ChatGroq
from langgraph.graph import add_messages

from prompts.prompt import (
    build_initial_recommendation_messages,
)
from schemas.team import TeamRecommendation, TeamRequest


class RecommendationState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    leader: str
    recommendation: TeamRecommendation | None

@lru_cache(maxsize=1)
def build_llm() -> ChatGroq:
    return ChatGroq(
        model="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))


async def get_team_recommendation(request: TeamRequest) -> TeamRecommendation:
    available = ", ".join(p.value for p in request.available_pokemon)
    leader = request.leader_to_beat.value

    messages = build_initial_recommendation_messages(available, leader)

    return build_llm().with_structured_output(TeamRecommendation).invoke(messages)
