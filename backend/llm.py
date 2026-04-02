import os
from functools import lru_cache
from typing import Annotated, List, TypedDict

from langchain_core.messages import BaseMessage
from langchain_groq import ChatGroq
from langgraph.graph import END, START, StateGraph, add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from prompts.prompt import (
    build_final_recommendation_messages,
    build_initial_recommendation_messages,
)
from schemas.team import TeamRecommendation, TeamRequest
from tools import TOOLS


class RecommendationState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    leader: str
    recommendation: TeamRecommendation | None

@lru_cache(maxsize=1)
def build_llm() -> ChatGroq:
    return ChatGroq(
        model="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))

async def draft_team_node(state: RecommendationState) -> RecommendationState:
    response = await build_llm().bind_tools(TOOLS).ainvoke(state["messages"])
    return {"messages": [response]}


async def structured_output_node(state: RecommendationState) -> RecommendationState:
    messages = list(state["messages"])
    messages.extend(build_final_recommendation_messages())
    recommendation = await build_llm().with_structured_output(TeamRecommendation).ainvoke(messages)
    return {"recommendation": recommendation}


@lru_cache(maxsize=1)
def build_recommendation_graph():
    graph_builder = StateGraph(RecommendationState)
    graph_builder.add_node("draft_team", draft_team_node)
    graph_builder.add_node("tools", ToolNode(TOOLS))
    graph_builder.add_node("structured_output", structured_output_node)

    graph_builder.add_edge(START, "draft_team")
    graph_builder.add_conditional_edges("draft_team", tools_condition, {"tools": "tools", END: "structured_output"})
    graph_builder.add_edge("tools", "draft_team")
    graph_builder.add_edge("structured_output", END)
    return graph_builder.compile()


async def get_team_recommendation(request: TeamRequest) -> TeamRecommendation:
    available = ", ".join(p.value for p in request.available_pokemon)
    leader = request.leader_to_beat.value

    messages = build_initial_recommendation_messages(available, leader)

    graph_response = await build_recommendation_graph().ainvoke(
        {
            "messages": messages,
            "leader": leader,
            "recommendation": None,
        }
    )
    return graph_response["recommendation"]
