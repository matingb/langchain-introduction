from typing import List

from pydantic import BaseModel, Field

from enums import GymLeader, PokemonName


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
        description="Brief explanation of why this Pokémon is useful against the chosen Gym Leader."
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
