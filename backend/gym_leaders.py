from typing import Dict, List

from enums import GymLeader, PokemonName

GYM_LEADER_TEAMS: Dict[GymLeader, List[str]] = {
    GymLeader.BROCK: [
        PokemonName.GEODUDE.value,
        PokemonName.ONIX.value,
    ],
    GymLeader.MISTY: [
        PokemonName.STARYU.value,
        PokemonName.STARMIE.value,
    ],
    GymLeader.LT_SURGE: [
        PokemonName.VOLTORB.value,
        PokemonName.PIKACHU.value,
        PokemonName.RAICHU.value,
    ],
    GymLeader.ERIKA: [
        PokemonName.VICTREEBEL.value,
        PokemonName.TANGELA.value,
        PokemonName.VILEPLUME.value,
    ],
    GymLeader.KOGA: [
        PokemonName.KOFFING.value,
        PokemonName.MUK.value,
        PokemonName.KOFFING.value,
        PokemonName.WEEZING.value,
    ],
    GymLeader.SABRINA: [
        PokemonName.KADABRA.value,
        PokemonName.MR_MIME.value,
        PokemonName.VENOMOTH.value,
        PokemonName.ALAKAZAM.value,
    ],
    GymLeader.BLAINE: [
        PokemonName.GROWLITHE.value,
        PokemonName.PONYTA.value,
        PokemonName.RAPIDASH.value,
        PokemonName.ARCANINE.value,
    ],
    GymLeader.GIOVANNI: [
        PokemonName.RHYHORN.value,
        PokemonName.DUGTRIO.value,
        PokemonName.NIDOQUEEN.value,
        PokemonName.NIDOKING.value,
        PokemonName.RHYDON.value,
    ],
}
