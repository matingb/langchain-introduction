from typing import List

from pydantic import BaseModel, Field

from domain.gym_leaders import GymLeader
from domain.pokemon import PokemonName


class TeamRequest(BaseModel):
    available_pokemon: List[PokemonName] = Field(
        description="List of Pokémon the player currently has available."
    )
    leader_to_beat: GymLeader = Field(
        description="The Gym Leader the player wants to defeat."
    )


class TeamMember(BaseModel):
    name: PokemonName = Field(description="Name of the Pokémon.")
    reason: str = Field(
        description="Explanation of why this Pokémon is useful against the Gym Leader. When relevant, include a specific matchup (e.g. which move to use against a particular rival Pokémon and why). Keep it concise, 4–5 sentences max."
    )
    held_item: str = Field(
        description="Recommended held item from context."
    )
    moves: List[str] = Field(
        description="All recommended moves available from context. Max 4 moves. Select the moves that are most effective against the Gym Leader id there are more than 4 moves.",
    )
    evs: str = Field(
        description="Recommended EV spread (e.g. '252 Atk / 4 Def / 252 Spe').",
    )


class PokemonDraftSelection(BaseModel):
    team: List[PokemonName] = Field(
        description="Preliminary list of up to 6 Pokémon names selected from the available ones. Always select as many as possible.",
        max_length=6,
    )


class TeamRecommendation(BaseModel):
    team: List[TeamMember] = Field(
        description="Recommended team of up to 6 Pokémon selected from the available ones.",
        max_length=6,
    )
    strategy: str = Field(
        description="Short overall strategy tip for defeating the Gym Leader."
    )
    rival_team: List[PokemonName] = Field(
        description="Pokémon used by the selected Gym Leader in Pokémon FireRed."
    )
