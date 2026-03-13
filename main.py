import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_groq import ChatGroq

from prompts.prompt import SYSTEM_PROMPT

load_dotenv()

def build_agent():

    chat_model = ChatGroq(
        model=os.getenv("MODEL_NAME"),
        api_key=os.getenv("GROQ_API_KEY"),
    )
    return create_agent(
        model=chat_model,
        system_prompt=SYSTEM_PROMPT,
    )


if __name__ == "__main__":
    if not os.getenv("GROQ_API_KEY"):
        raise ValueError(
            "Missing GROQ_API_KEY. Create a .env file based on .env.example."
        )

    agent = build_agent()
    response = agent.invoke(
        {"messages": [{"role": "user", "content": "Quiero armar un equipo de Pokémon para pasar vencer al primer gimnasio de Rojo Fuego"}]}
    )
    print(response["messages"][-1].content)