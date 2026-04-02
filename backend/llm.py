import os
from functools import lru_cache
from typing import List, TypedDict

from langchain_core.messages import BaseMessage
from langchain_groq import ChatGroq
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langsmith import traceable

from prompts.prompt import (
    build_context_message,
    build_draft_team_message,
    build_final_recommendation_message,
    build_initial_recommendation_messages,
)
from schemas.team import PokemonTeamSelection, TeamRecommendation, TeamRequest
from rag import retrieve_from_source
from tools.gym_leaders import TOOLS


class RecommendationState(TypedDict):
    messages: List[BaseMessage]
    available_pokemons: str
    leader: str
    rival_team: List[str]
    leader_context: str
    pokemon_context: str
    pokemon_selection: PokemonTeamSelection | None
    recommendation: TeamRecommendation | None

def build_llm() -> ChatGroq:
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
    )
    # return ChatGoogleGenerativeAI(model="gemini-3.1-pro-preview", google_api_key=os.getenv("GOOGLE_API_KEY"))


@traceable(run_type="retriever", name="retrieve_context")
def _retrieve_context(query: str, source: str, k: int) -> str:
    return retrieve_from_source(query=query, source=source, k=k)


async def retrieve_leader_node(state: RecommendationState) -> RecommendationState:
    context = _retrieve_context(
        query=state["leader"],
        source="get_strategies.txt",
        k=1,
    )
    return {"leader_context": context}


async def draft_team_node(state: RecommendationState) -> RecommendationState:
    messages = list(state["messages"])
    leader_context_message = build_context_message(
        "Gym Leader strategy context",
        state["leader_context"],
    )
    if leader_context_message is not None:
        messages.append(leader_context_message)
    messages.append(build_draft_team_message(state["rival_team"]))
    pokemon_selection = await build_llm().with_structured_output(
        PokemonTeamSelection
    ).ainvoke(messages)
    return {"pokemon_selection": pokemon_selection}


async def retrieve_pokemon_node(state: RecommendationState) -> RecommendationState:
    pokemon_selection = state["pokemon_selection"]
    if pokemon_selection is None or not pokemon_selection.team:
        return {"pokemon_context": ""}

    query = ", ".join(member.name.value for member in pokemon_selection.team)
    context = _retrieve_context(
        query=query,
        source="pokemon_roles.txt",
        k=6,
    )
    return {"pokemon_context": context}


async def structured_output_node(state: RecommendationState) -> RecommendationState:
    messages = list(state["messages"])
    leader_context_message = build_context_message(
        "Gym Leader strategy context",
        state["leader_context"],
    )
    pokemon_context_message = build_context_message(
        "Pokémon role context for the preliminary team",
        state["pokemon_context"],
    )
    if leader_context_message is not None:
        messages.append(leader_context_message)
    if pokemon_context_message is not None:
        messages.append(pokemon_context_message)
    messages.append(
        build_final_recommendation_message(
            state["rival_team"],
            state["pokemon_selection"].model_dump_json()
            if state["pokemon_selection"]
            else "None",
        )
    )
    recommendation = await build_llm().with_structured_output(TeamRecommendation).ainvoke(messages)
    return {"recommendation": recommendation}


@lru_cache(maxsize=1)
def build_recommendation_graph():
    graph_builder = StateGraph(RecommendationState)
    graph_builder.add_node("retrieve_leader", retrieve_leader_node)
    graph_builder.add_node("draft_team", draft_team_node)
    graph_builder.add_node("tools", ToolNode(TOOLS))
    graph_builder.add_node("retrieve_pokemon", retrieve_pokemon_node)
    graph_builder.add_node("structured_output", structured_output_node)
    graph_builder.add_edge(START, "retrieve_leader")
    graph_builder.add_edge("retrieve_leader", "draft_team")
    graph_builder.add_conditional_edges("draft_team", tools_condition, {"tools": "tools", END: "retrieve_pokemon"})
    graph_builder.add_edge("tools", "draft_team")
    graph_builder.add_edge("retrieve_pokemon", "structured_output")
    graph_builder.add_edge("structured_output", END)
    return graph_builder.compile()


async def get_team_recommendation(request: TeamRequest) -> TeamRecommendation:
    available = ", ".join(p.value for p in request.available_pokemon)
    leader = request.leader_to_beat.value

    messages = build_initial_recommendation_messages(available, leader)

    graph_response = await build_recommendation_graph().ainvoke(
        {
            "messages": messages,
            "available": available,
            "leader": leader,
            "rival_team": [],
            "leader_context": "",
            "pokemon_context": "",
            "pokemon_selection": None,
            "recommendation": None,
        }
    )
    return graph_response["recommendation"]
