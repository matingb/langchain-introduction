import React, { useState } from 'react';
import { POKEMON_LIST, GYM_LEADERS, getPokemonSpriteUrl, getLeaderSpriteUrl } from './data';
import { Loader2, Swords, RefreshCcw, X } from 'lucide-react';

type TeamMember = {
  name: string;
  reason: string;
  held_item?: string | null;
  moves?: string[] | null;
  evs?: string | null;
};

type RecommendationResult = {
  team: TeamMember[];
  rival_team: string[];
  strategy: string;
};

export default function App() {
  const [selectedLeader, setSelectedLeader] = useState<string | null>(null);
  const [selectedPokemon, setSelectedPokemon] = useState<string[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [result, setResult] = useState<RecommendationResult | null>(null);
  const [activeTeamMember, setActiveTeamMember] = useState<string | null>(null);
  const [detailMember, setDetailMember] = useState<TeamMember | null>(null);

  const togglePokemon = (pokemon: string) => {
    setSelectedPokemon(prev => 
      prev.includes(pokemon) 
        ? prev.filter(p => p !== pokemon)
        : [...prev, pokemon]
    );
  };

  const handleSubmit = async () => {
    if (!selectedLeader || selectedPokemon.length === 0) return;

    setIsSubmitting(true);
    
    const payload = {
      available_pokemon: selectedPokemon,
      leader_to_beat: selectedLeader
    };

    try {
      const response = await fetch("http://localhost:8000/recommend-team", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const data: RecommendationResult = await response.json();
      setResult(data);
      setActiveTeamMember(null);
      setDetailMember(null);
    } catch (error) {
      console.error("Error fetching ideal team:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const resetSelection = () => {
    setResult(null);
    setActiveTeamMember(null);
    setDetailMember(null);
  };

  return (
    <div className="min-h-screen pb-32 p-4 md:p-8 max-w-6xl mx-auto">
      <header className="text-center mb-10 mt-4">
        <h1 className="retro-title text-3xl md:text-5xl font-bold uppercase mb-4">
          FireRed Strategy
        </h1>
        <p className="text-xs md:text-sm text-gray-700 bg-white inline-block px-4 py-2 border-2 border-black rounded shadow-[2px_2px_0px_#000]">
          Select your available Pokémon and the Gym Leader to battle.
        </p>
      </header>

      {result ? (
        <div className="border-4 border-black bg-white p-4 md:p-8 shadow-[8px_8px_0px_#222] animate-in fade-in zoom-in duration-300">
          <h2 className="text-2xl text-red-600 mb-8 uppercase tracking-widest text-center">Ideal Team Found!</h2>

          <div className="flex items-center justify-between mb-8 bg-gray-100 p-4 border-4 border-black rounded-lg relative overflow-hidden shadow-inner">
            <div className="absolute inset-0 bg-gradient-to-r from-blue-200 via-white to-red-200 opacity-40"></div>

            <div className="flex flex-col items-center z-10 w-1/3">
              <img
                src="https://play.pokemonshowdown.com/sprites/trainers/red-gen3.png"
                alt="Player"
                className="h-20 md:h-32 pixelated drop-shadow-md"
                style={{ imageRendering: 'pixelated' }}
              />
              <span className="mt-2 text-[10px] md:text-xs font-bold uppercase bg-blue-600 text-white px-3 py-1 border-2 border-black shadow-[2px_2px_0px_#000]">
                You
              </span>
            </div>

            <div className="z-10 flex flex-col items-center justify-center w-1/3">
              <span className="text-4xl md:text-6xl text-red-600 font-bold italic retro-title">VS</span>
            </div>

            <div className="flex flex-col items-center z-10 w-1/3">
              <img
                src={getLeaderSpriteUrl(GYM_LEADERS.find((leader) => leader.name === selectedLeader)?.sprite || '')}
                alt={selectedLeader || 'Leader'}
                className="h-20 md:h-32 pixelated drop-shadow-md"
                style={{ imageRendering: 'pixelated' }}
              />
              <span className="mt-2 text-[10px] md:text-xs font-bold uppercase bg-red-600 text-white px-3 py-1 border-2 border-black shadow-[2px_2px_0px_#000]">
                {selectedLeader}
              </span>
            </div>
          </div>

          <div className="relative z-20 grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-8 mb-8">
            <div className="bg-blue-50 p-3 md:p-4 border-4 border-blue-900 rounded-lg shadow-[4px_4px_0px_#1e3a8a]">
              <div className="flex justify-between items-end mb-3 border-b-4 border-blue-900 pb-2">
                <h3 className="text-blue-900 uppercase text-xs md:text-sm font-bold">Your Squad</h3>
              </div>
              <div className="grid grid-cols-2 gap-3 md:gap-4">
                {result.team.map((member, idx) => {
                  const dexNumber = POKEMON_LIST.indexOf(member.name) + 1;
                  const cardKey = `${member.name}-${idx}`;
                  const isActive = activeTeamMember === cardKey;
                  return (
                    <button
                      key={cardKey}
                      type="button"
                      className={`battle-card retro-box group h-28 md:h-32 flex flex-col items-center justify-center bg-white border-blue-900 ${isActive ? 'active' : ''}`}
                      onClick={() => setDetailMember(member)}
                      onMouseEnter={() => setActiveTeamMember(cardKey)}
                      onMouseLeave={() => setActiveTeamMember(null)}
                    >
                      <div className="flex flex-col items-center justify-center p-2">
                        <img
                          src={getPokemonSpriteUrl(dexNumber)}
                          alt={member.name}
                          className="w-14 h-14 md:w-16 md:h-16 pixelated"
                          style={{ imageRendering: 'pixelated' }}
                        />
                        <span className="text-[8px] md:text-[10px] mt-2 uppercase text-center leading-tight w-full px-1">
                          {member.name}
                        </span>
                      </div>
                      <div className="battle-card-tooltip">
                        <span className="text-[8px] md:text-[9px] leading-tight normal-case text-blue-900 font-bold">
                          {member.reason}
                        </span>
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>

            <div className="bg-red-50 p-3 md:p-4 border-4 border-red-900 rounded-lg shadow-[4px_4px_0px_#7f1d1d]">
              <div className="flex justify-between items-end mb-3 border-b-4 border-red-900 pb-2">
                <h3 className="text-red-900 uppercase text-xs md:text-sm font-bold">Rival Squad</h3>
              </div>
              <div className="grid grid-cols-2 gap-3 md:gap-4">
                {result.rival_team.map((pokemonName, idx) => {
                  const dexNumber = POKEMON_LIST.indexOf(pokemonName) + 1;
                  return (
                    <div
                      key={`${pokemonName}-${idx}`}
                      className="retro-box h-28 md:h-32 flex flex-col items-center justify-center bg-white p-2 border-red-900"
                    >
                      <img
                        src={getPokemonSpriteUrl(dexNumber)}
                        alt={pokemonName}
                        className="w-14 h-14 md:w-16 md:h-16 pixelated"
                        style={{ imageRendering: 'pixelated' }}
                      />
                      <span className="text-[8px] md:text-[10px] mt-2 uppercase text-center leading-tight w-full px-1">
                        {pokemonName}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          <div className="relative border-4 border-black bg-white p-5 md:p-6 mb-8 shadow-[4px_4px_0px_#222] rounded-lg text-left">
            <div className="absolute -top-3 left-4 bg-white px-2 text-red-600 font-bold text-[10px] md:text-xs uppercase border-x-2 border-black">
              Oak&apos;s Advice
            </div>
            <p className="text-[10px] md:text-xs leading-loose uppercase mt-2">
              {result.strategy}
            </p>
          </div>

          <button 
            onClick={resetSelection}
            className="retro-button px-8 py-4 text-sm flex items-center justify-center mx-auto gap-3"
          >
            <RefreshCcw size={18} />
            Start Over
          </button>

          {detailMember && (() => {
            const dexNumber = POKEMON_LIST.indexOf(detailMember.name) + 1;
            return (
              <div
                className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60"
                onClick={() => setDetailMember(null)}
              >
                <div
                  className="relative bg-white border-4 border-black shadow-[8px_8px_0px_#222] w-full max-w-lg p-6 animate-in fade-in zoom-in duration-200"
                  onClick={(e) => e.stopPropagation()}
                >
                  <button
                    onClick={() => setDetailMember(null)}
                    className="absolute top-3 right-3 border-2 border-black p-1 hover:bg-black hover:text-white transition-colors"
                    aria-label="Close"
                  >
                    <X size={14} />
                  </button>

                  <div className="flex flex-col items-center mb-4">
                    <img
                      src={getPokemonSpriteUrl(dexNumber)}
                      alt={detailMember.name}
                      className="w-24 h-24 pixelated"
                      style={{ imageRendering: 'pixelated' }}
                    />
                    <h3 className="retro-title text-xl uppercase mt-1">{detailMember.name}</h3>
                  </div>

                  <div className="space-y-3 text-[11px] uppercase">
                    <div className="border-2 border-black p-3">
                      <p className="font-bold text-gray-500 mb-1">Role</p>
                      <p className="leading-relaxed normal-case">{detailMember.reason}</p>
                    </div>

                    {detailMember.held_item && (
                      <div className="border-2 border-black p-3">
                        <p className="font-bold text-gray-500 mb-1">Held Item</p>
                        <p>{detailMember.held_item}</p>
                      </div>
                    )}

                    {detailMember.moves && detailMember.moves.length > 0 && (
                      <div className="border-2 border-black p-3">
                        <p className="font-bold text-gray-500 mb-1">Moves</p>
                        <ul className="space-y-1">
                          {detailMember.moves.map((move, i) => (
                            <li key={i} className="flex items-center gap-2">
                              <span className="w-4 h-4 bg-black text-white flex items-center justify-center text-[9px] shrink-0">{i + 1}</span>
                              {move}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {detailMember.evs && (
                      <div className="border-2 border-black p-3">
                        <p className="font-bold text-gray-500 mb-1">EV Spread</p>
                        <p>{detailMember.evs}</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })()}
        </div>
      ) : (
        <div className="space-y-12">
          {/* Gym Leader Selection */}
          <section>
            <div className="flex items-center gap-3 mb-6">
              <div className="w-8 h-8 bg-red-600 border-2 border-black rounded-full flex items-center justify-center text-white text-xs">1</div>
              <h2 className="text-xl uppercase">Target Gym Leader</h2>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              {GYM_LEADERS.map((leader) => (
                <button
                  key={leader.name}
                  onClick={() => setSelectedLeader(leader.name)}
                  className={`p-4 flex flex-col items-center cursor-pointer ${
                    selectedLeader === leader.name ? 'retro-box-selected' : 'retro-box'
                  }`}
                >
                  <img 
                    src={getLeaderSpriteUrl(leader.sprite)} 
                    alt={leader.name}
                    className="h-24 object-contain mb-2"
                    style={{ imageRendering: 'pixelated' }}
                  />
                  <span className="text-[10px] md:text-xs uppercase font-bold text-center">{leader.name}</span>
                  <span className="text-[8px] mt-1 text-gray-600 uppercase">{leader.type}</span>
                </button>
              ))}
            </div>
          </section>

          {/* Pokemon Selection */}
          <section className="pb-24">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-red-600 border-2 border-black rounded-full flex items-center justify-center text-white text-xs">2</div>
                <h2 className="text-xl uppercase">Available Pokémon</h2>
              </div>
              <span className="text-xs bg-white px-3 py-1 border-2 border-black shadow-[2px_2px_0px_#000]">
                Selected: {selectedPokemon.length}
              </span>
            </div>
            
            <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 lg:grid-cols-8 gap-3">
              {POKEMON_LIST.map((pokemon, index) => {
                const isSelected = selectedPokemon.includes(pokemon);
                return (
                  <button
                    key={pokemon}
                    onClick={() => togglePokemon(pokemon)}
                    className={`p-2 flex flex-col items-center cursor-pointer ${
                      isSelected ? 'retro-box-selected' : 'retro-box'
                    }`}
                  >
                    <img 
                      src={getPokemonSpriteUrl(index + 1)} 
                      alt={pokemon}
                      className="w-16 h-16"
                      style={{ imageRendering: 'pixelated' }}
                      loading="lazy"
                    />
                    <span className="text-[8px] uppercase text-center mt-1 truncate w-full">
                      {pokemon}
                    </span>
                  </button>
                );
              })}
            </div>
          </section>
        </div>
      )}

      {/* Sticky Bottom Action Bar */}
      {!result && (
        <div className="fixed bottom-0 left-0 right-0 p-4 bg-white border-t-4 border-black shadow-[0_-4px_0px_rgba(0,0,0,0.1)] z-10 flex justify-center">
          <button
            onClick={handleSubmit}
            disabled={!selectedLeader || selectedPokemon.length === 0 || isSubmitting}
            className="retro-button px-8 py-4 text-sm md:text-base flex items-center gap-3 w-full max-w-md justify-center"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="animate-spin" size={20} />
                Analyzing...
              </>
            ) : (
              <>
                <Swords size={20} />
                Find Ideal Team
              </>
            )}
          </button>
        </div>
      )}
    </div>
  );
}
