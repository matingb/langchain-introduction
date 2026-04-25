import os
from functools import lru_cache
from dotenv import load_dotenv
from langchain_groq import ChatGroq

from prompts.prompt import build_initial_recommendation_messages

load_dotenv()
@lru_cache(maxsize=1)



def build_llm() -> ChatGroq:
    return ChatGroq(
        model="llama-3.3-70b-versatile", 
        api_key=os.getenv("GROQ_API_KEY")
    )

available = """Charizard, Blastoise, Venusaur, Charmeleon, 
            Pidgeot, Blastoise, Venusaur, Charmeleon Pikachu"""

gym_leader = "Blaine"

agent = build_llm()
response = agent.invoke(build_initial_recommendation_messages(available, gym_leader))
print("\n\n" + response.content)
