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
    held_item: str = Field(
        description="Recommended held item. Only populate if the information is available from context.",
    )
    moves: List[str] = Field(
        description="Recommended moves. Only populate if the information is available from context.",
    )
    evs: str = Field(
        description="Recommended EV spread (e.g. '252 Atk / 4 Def / 252 Spe'). Only populate if the information is available from context.",
    )


class PokemonTeamSelection(BaseModel):
    team: List[TeamMember] = Field(
        description="Preliminary team of up to 6 Pokémon selected from the available ones.",
        max_length=6,
    )
    notes: str = Field(
        description="Very brief note explaining the overall preliminary selection."
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
