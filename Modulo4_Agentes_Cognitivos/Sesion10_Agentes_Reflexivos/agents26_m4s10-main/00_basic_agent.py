from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool

load_dotenv()

@tool
def saludo(name: str) -> str:
    """Returns a greeting message."""
    return f"Hello, {name}!"

agent = create_agent(
    model="anthropic:claude-opus-4-8",
    system_prompt="You are a helpful assistant that can control a robot to move in a 2D space.",
    tools=[saludo]
)

if __name__ == "__main__":
    while True:
        user_input = input("User: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting the agent. Goodbye!")
            break
        response = agent.invoke(
            {"messages": [{"role": "user", "content": f"{user_input}."}]}
        )
        response =response["messages"][-1].content
        print(f"Agent: {response}")