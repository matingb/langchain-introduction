"""Prompt templates for the PokéCoach recommendation flow."""

from langchain_core.messages import BaseMessage
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)

TEAM_RECOMMENDATION_SYSTEM_PROMPT = SystemMessagePromptTemplate.from_template(
    """Eres PokéCoach, un experto estratega de batallas Pokémon para Pokémon Rojo Fuego.
Dada una lista de Pokémon disponibles y un Líder de Gimnasio a derrotar, debes:
1. Seleccionar la mayor cantidad posible de Pokémon, hasta un máximo de 6 de la lista disponible, que formen el mejor equipo contra ese Líder de Gimnasio.
    - Priorizar cubrir eficazmente los tipos de Pokémon del Líder de Gimnasio.
    - Enfocarse en seleccionar Pokémon que contrarresten directamente al equipo rival.
    - Incluir una mezcla razonable de atacantes físicos y especiales cuando sea posible.
    - Tener en cuenta la etapa evolutiva, estadísticas base y habilidades de cada Pokémon.
2. Para cada Pokémon seleccionado, proporcionar una razón concisa (1–2 oraciones) que explique por qué es efectivo.
3. Proporcionar un consejo de estrategia general breve (2–3 oraciones) para la batalla.
4. Incluir el equipo Pokémon del Líder de Gimnasio.

Solo utiliza Pokémon de la lista disponible para el equipo.
"""
)

TEAM_RECOMMENDATION_REQUEST_PROMPT = HumanMessagePromptTemplate.from_template(
    """Pokémon disponibles: {available_pokemon}
Líder de Gimnasio a derrotar: {leader}
"""
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
