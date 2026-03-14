import React, { useState } from 'react';
import { POKEMON_LIST, GYM_LEADERS, getPokemonSpriteUrl, getLeaderSpriteUrl } from './data';
import { Loader2, Swords, RefreshCcw } from 'lucide-react';

export default function App() {
  const [selectedLeader, setSelectedLeader] = useState<string | null>(null);
  const [selectedPokemon, setSelectedPokemon] = useState<string[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [resultTeam, setResultTeam] = useState<string[] | null>(null);

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

    console.log("Sending to API:", payload);

    try {
      const response = await fetch("http://localhost:8000/recommend-team", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const data: { team: { name: string; reason: string }[]; strategy: string } =
        await response.json();

      setResultTeam(data.team.map((member) => member.name));
    } catch (error) {
      console.error("Error fetching ideal team:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const resetSelection = () => {
    setSelectedLeader(null);
    setSelectedPokemon([]);
    setResultTeam(null);
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

      {resultTeam ? (
        <div className="retro-box p-6 md:p-10 text-center animate-in fade-in zoom-in duration-300">
          <h2 className="text-2xl text-red-600 mb-8 uppercase tracking-widest">Ideal Team Found!</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-6 mb-10">
            {resultTeam.map((pokemonName) => {
              const dexNumber = POKEMON_LIST.indexOf(pokemonName) + 1;
              return (
                <div key={pokemonName} className="retro-box p-4 flex flex-col items-center bg-gray-50">
                  <img 
                    src={getPokemonSpriteUrl(dexNumber)} 
                    alt={pokemonName}
                    className="w-24 h-24 pixelated"
                    style={{ imageRendering: 'pixelated' }}
                  />
                  <span className="text-xs mt-2 uppercase">{pokemonName}</span>
                </div>
              );
            })}
          </div>
          <button 
            onClick={resetSelection}
            className="retro-button px-8 py-4 text-sm flex items-center justify-center mx-auto gap-3"
          >
            <RefreshCcw size={18} />
            Start Over
          </button>
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
      {!resultTeam && (
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
