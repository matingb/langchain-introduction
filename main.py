import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_groq import ChatGroq


load_dotenv()


def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"


def build_agent():

    chat_model = ChatGroq(
        model=os.getenv("MODEL_NAME"),
        api_key=os.getenv("GROQ_API_KEY"),
    )
    return create_agent(
        model=chat_model,
        tools=[get_weather],
        system_prompt="You are a helpful assistant",
    )


if __name__ == "__main__":
    if not os.getenv("GROQ_API_KEY"):
        raise ValueError(
            "Missing GROQ_API_KEY. Create a .env file based on .env.example."
        )

    agent = build_agent()
    response = agent.invoke(
        {"messages": [{"role": "user", "content": "what is the weather in sf"}]}
    )
    print(response)