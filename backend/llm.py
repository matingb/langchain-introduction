import os
from functools import lru_cache
from typing import List, TypedDict

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langsmith import traceable

from enums import GymLeader
from gym_leaders import GYM_LEADER_TEAMS
from models import PokemonTeamSelection, TeamRecommendation, TeamRequest
from prompts.prompt import TEAM_RECOMMENDATION_PROMPT
from rag import retrieve_from_source


class RecommendationState(TypedDict):
    messages: List[BaseMessage]
    available_pokemons: str
    leader: str
    rival_team: List[str]
    leader_context: str
    pokemon_context: str
    pokemon_selection: PokemonTeamSelection | None
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


def build_llm() -> ChatGroq:
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
    )
    # return ChatGoogleGenerativeAI(model="gemini-3.1-pro-preview", google_api_key=os.getenv("GOOGLE_API_KEY"))


def _build_context_message(title: str, context: str) -> SystemMessage | None:
    if not context:
        return None
    return SystemMessage(content=f"{title}:\n\n{context}")


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
    leader_context_message = _build_context_message(
        "Gym Leader strategy context",
        state["leader_context"],
    )
    if leader_context_message is not None:
        messages.append(leader_context_message)
    rival_team = state["rival_team"]
    rival_info = f" Rival team: {', '.join(rival_team)}." if rival_team else ""
    messages.append(
        HumanMessage(
            content=(
                "Select a preliminary team of up to 6 Pokémon from the available list. "
                "Use the gym leader strategy context and the rival team. "
                "Keep each reason brief for debugging."
                + rival_info
            )
        )
    )
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
    leader_context_message = _build_context_message(
        "Gym Leader strategy context",
        state["leader_context"],
    )
    pokemon_context_message = _build_context_message(
        "Pokémon role context for the preliminary team",
        state["pokemon_context"],
    )
    if leader_context_message is not None:
        messages.append(leader_context_message)
    if pokemon_context_message is not None:
        messages.append(pokemon_context_message)
    messages.append(
        HumanMessage(
            content=(
                f"Rival team: {', '.join(state['rival_team'])}\n"
                f"Pokemon selection: {state['pokemon_selection'].model_dump_json() if state['pokemon_selection'] else 'None'}\n\n"
                "Return the final answer as a structured team recommendation. "
                "Only choose Pokemon from the provided available list for team."
            )
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

    messages = [
        SystemMessage(content=TEAM_RECOMMENDATION_PROMPT),
        HumanMessage(
            content=(
                f"Available Pokémon: {available}\n"
                f"Gym Leader to beat: {leader}\n\n"
            )
        ),
    ]

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
