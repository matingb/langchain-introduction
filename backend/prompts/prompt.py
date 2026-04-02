"""Prompt templates for the PokéCoach recommendation flow."""

from langchain_core.messages import BaseMessage
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)

TEAM_RECOMMENDATION_SYSTEM_PROMPT = SystemMessagePromptTemplate.from_template(
    """You are PokéCoach, an expert Pokémon battle strategist for Pokémon FireRed.
Given a list of available Pokémon and a Gym Leader to defeat, you must:
1. Select the maximum number of Pokémon possible, up to a limit of 6 from the available list that form the best team against that Gym Leader.
    - Prioritize covering the Gym Leader’s Pokémon types effectively.
    - Focus on selecting Pokémon that directly counter the opponent’s team
    - Include a reasonable mix of physical and special attackers when possible.
    - Take into account each Pokémon’s evolutionary stage, base stats and abilities.
2. For each selected Pokémon, provide a concise reason (1–2 sentences) explaining why it is effective.
3. Provide a short overall strategy tip (2–3 sentences) for the battle.
4. Include the Gym Leader's Pokémon team.

Only use Pokémon from the provided available list for team.
"""
)

TEAM_RECOMMENDATION_REQUEST_PROMPT = HumanMessagePromptTemplate.from_template(
    """Available Pokémon: {available_pokemon}
Gym Leader to beat: {leader}
"""
)

CONTEXT_MESSAGE_PROMPT = SystemMessagePromptTemplate.from_template(
    """{title}:

{context}"""
)

DRAFT_TEAM_PROMPT = HumanMessagePromptTemplate.from_template(
    """Select a preliminary list of Pokémon names from the available list. Always select as many as possible, up to a maximum of 6. Use the gym leader strategy context and the rival team to decide.{rival_info}"""
)

FINAL_RECOMMENDATION_PROMPT = HumanMessagePromptTemplate.from_template(
    """Return the final structured team recommendation. Always select as many Pokémon as possible, up to 6. Use the Pokémon role context to populate moves for each Pokémon. Only choose Pokémon from the provided available list."""
)


def build_initial_recommendation_messages(
    available_pokemon: str, leader: str
) -> list[BaseMessage]:
    return ChatPromptTemplate.from_messages(
        [
            TEAM_RECOMMENDATION_SYSTEM_PROMPT,
            TEAM_RECOMMENDATION_REQUEST_PROMPT,
        ]
    ).format_messages(available_pokemon=available_pokemon, leader=leader)


def build_context_message(title: str, context: str) -> BaseMessage | None:
    if not context:
        return None
    return CONTEXT_MESSAGE_PROMPT.format(title=title, context=context)


def build_draft_team_messages(rival_team: list[str]) -> list[BaseMessage]:
    rival_info = f" Rival team: {', '.join(rival_team)}." if rival_team else ""
    return [DRAFT_TEAM_PROMPT.format(rival_info=rival_info)]


def build_final_recommendation_messages() -> list[BaseMessage]:
    return [FINAL_RECOMMENDATION_PROMPT.format()]
