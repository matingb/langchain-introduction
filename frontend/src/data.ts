export const POKEMON_LIST = [
  "Bulbasaur", "Ivysaur", "Venusaur", "Charmander", "Charmeleon", "Charizard",
  "Squirtle", "Wartortle", "Blastoise", "Caterpie", "Metapod", "Butterfree",
  "Weedle", "Kakuna", "Beedrill", "Pidgey", "Pidgeotto", "Pidgeot", "Rattata",
  "Raticate", "Spearow", "Fearow", "Ekans", "Arbok", "Pikachu", "Raichu",
  "Sandshrew", "Sandslash", "Nidoran♀", "Nidorina", "Nidoqueen", "Nidoran♂",
  "Nidorino", "Nidoking", "Clefairy", "Clefable", "Vulpix", "Ninetales",
  "Jigglypuff", "Wigglytuff", "Zubat", "Golbat", "Oddish", "Gloom", "Vileplume",
  "Paras", "Parasect", "Venonat", "Venomoth", "Diglett", "Dugtrio", "Meowth",
  "Persian", "Psyduck", "Golduck", "Mankey", "Primeape", "Growlithe", "Arcanine",
  "Poliwag", "Poliwhirl", "Poliwrath", "Abra", "Kadabra", "Alakazam", "Machop",
  "Machoke", "Machamp", "Bellsprout", "Weepinbell", "Victreebel", "Tentacool",
  "Tentacruel", "Geodude", "Graveler", "Golem", "Ponyta", "Rapidash", "Slowpoke",
  "Slowbro", "Magnemite", "Magneton", "Farfetch'd", "Doduo", "Dodrio", "Seel",
  "Dewgong", "Grimer", "Muk", "Shellder", "Cloyster", "Gastly", "Haunter",
  "Gengar", "Onix", "Drowzee", "Hypno", "Krabby", "Kingler", "Voltorb",
  "Electrode", "Exeggcute", "Exeggutor", "Cubone", "Marowak", "Hitmonlee",
  "Hitmonchan", "Lickitung", "Koffing", "Weezing", "Rhyhorn", "Rhydon", "Chansey",
  "Tangela", "Kangaskhan", "Horsea", "Seadra", "Goldeen", "Seaking", "Staryu",
  "Starmie", "Mr. Mime", "Scyther", "Jynx", "Electabuzz", "Magmar", "Pinsir",
  "Tauros", "Magikarp", "Gyarados", "Lapras", "Ditto", "Eevee", "Vaporeon",
  "Jolteon", "Flareon", "Porygon", "Omanyte", "Omastar", "Kabuto", "Kabutops",
  "Aerodactyl", "Snorlax", "Articuno", "Zapdos", "Moltres", "Dratini", "Dragonair",
  "Dragonite", "Mewtwo", "Mew"
];

export const GYM_LEADERS = [
  { name: "Brock", type: "Rock", sprite: "brock-gen3" },
  { name: "Misty", type: "Water", sprite: "misty-gen3" },
  { name: "Lt. Surge", type: "Electric", sprite: "ltsurge-gen3" },
  { name: "Erika", type: "Grass", sprite: "erika-gen3" },
  { name: "Koga", type: "Poison", sprite: "koga-gen3" },
  { name: "Sabrina", type: "Psychic", sprite: "sabrina-gen3" },
  { name: "Blaine", type: "Fire", sprite: "blaine-gen3" },
  { name: "Giovanni", type: "Ground", sprite: "giovanni-gen3" }
];

export const getPokemonSpriteUrl = (id: number) => 
  `https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/${id}.png`;

export const getLeaderSpriteUrl = (spriteName: string) =>
  `https://play.pokemonshowdown.com/sprites/trainers/${spriteName}.png`;
