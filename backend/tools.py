from typing import List

from langchain_core.tools import tool

from domain.gym_leaders import GYM_LEADER_TEAMS, GymLeader


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
