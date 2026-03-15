import os

from langchain_groq import ChatGroq

from models import TeamRecommendation, TeamRequest
from prompts.prompt import TEAM_RECOMMENDATION_PROMPT

def build_llm() -> ChatGroq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("Missing GROQ_API_KEY in environment.")
    return ChatGroq(
        model=os.getenv("MODEL_NAME", "llama-3.3-70b-versatile"),
        api_key=api_key,
    )


async def get_team_recommendation(request: TeamRequest) -> TeamRecommendation:
    structured_llm = build_llm().with_structured_output(TeamRecommendation)

    available = ", ".join(p.value for p in request.available_pokemon)
    leader = request.leader_to_beat.value

    messages = [
        {"role": "system", "content": TEAM_RECOMMENDATION_PROMPT},
        {
            "role": "user",
            "content": (
                f"Available Pokémon: {available}\n"
                f"Gym Leader to beat: {leader}\n\n"
                "Select the best team of up to 6 Pokémon from the available list "
                "and explain why each one is useful."
            ),
        },
    ]

    return await structured_llm.ainvoke(messages)
