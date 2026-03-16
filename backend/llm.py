import os
import re
from functools import lru_cache
from typing import Annotated, List, TypedDict

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from enums import GymLeader
from gym_leaders import GYM_LEADER_TEAMS
from models import TeamRecommendation, TeamRequest
from prompts.prompt import TEAM_RECOMMENDATION_PROMPT


class RecommendationState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    recommendation: TeamRecommendation | None

@tool
def get_gym_leader_team(leader: str) -> List[str]:
    """Returns the Pokémon team used by a Gym Leader in Pokémon FireRed.
    Use this to know which Pokémon you will face before recommending a counter-team.
    leader: Gym leader name, e.g. Brock, Misty, Lt. Surge, Erika, Koga, Sabrina, Blaine, Giovanni.
    """
    try:
        leader_enum = GymLeader(leader.strip())
    except ValueError:
        raise ValueError(
            f"Unknown gym leader: {leader}. Use one of: {', '.join(g.value for g in GymLeader)}."
        )
    return GYM_LEADER_TEAMS[leader_enum]

TOOLS = [get_gym_leader_team]


def build_llm() -> ChatGoogleGenerativeAI:
    return ChatGroq(model="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))
    # return ChatGoogleGenerativeAI(model="gemini-3.1-pro-preview", google_api_key=os.getenv("GOOGLE_API_KEY"))

async def agent_node(state: RecommendationState) -> RecommendationState:
    response = await build_llm().bind_tools(TOOLS).ainvoke(state["messages"])
    return {"messages": [response]}


async def structured_output_node(state: RecommendationState) -> RecommendationState:
    messages = list(state["messages"]) + [
        HumanMessage(
            content=(
                "Return the final answer as a structured team recommendation. "
                "Only choose Pokemon from the provided available list."
            )
        )
    ]
    recommendation = await build_llm().with_structured_output(TeamRecommendation).ainvoke(messages)
    return {"recommendation": recommendation}


@lru_cache(maxsize=1)
def build_recommendation_graph():
    graph_builder = StateGraph(RecommendationState)
    graph_builder.add_node("agent", agent_node)
    graph_builder.add_node("tools", ToolNode(TOOLS))
    graph_builder.add_node("structured_output", structured_output_node)
    graph_builder.add_edge(START, "agent")
    graph_builder.add_conditional_edges("agent", tools_condition, {"tools": "tools", END: "structured_output"})
    graph_builder.add_edge("tools", "agent")
    graph_builder.add_edge("structured_output", END)
    return graph_builder.compile()


async def get_team_recommendation(request: TeamRequest) -> TeamRecommendation:
    available = ", ".join(p.value for p in request.available_pokemon)
    leader = request.leader_to_beat.value

    messages = [
        SystemMessage(content=TEAM_RECOMMENDATION_PROMPT),
        HumanMessage(
            content=(
                f"Available Pokémon: {available}\n"
                f"Gym Leader to beat: {leader}\n\n"
                "Select the best counter-team of up to 6 Pokémon from the available list and "
                "explain why each one is useful. "
                "Evaluate the effectiveness of the team against the Gym Leader's team and the Gym Leader's team against the team."
                "Evaluate based statistics of the Pokémon and the moves of the Pokémon."
                "Evaluate based on the weaknesses and strengths of the Pokémon."
            )
        ),
    ]

    graph_response = await build_recommendation_graph().ainvoke({"messages": messages})
    return graph_response["recommendation"]
