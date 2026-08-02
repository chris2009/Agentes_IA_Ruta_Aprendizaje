import os
from langchain.agents import create_agent
from dotenv import load_dotenv

from _utils import resolver_modelo

load_dotenv()

MODELO = resolver_modelo(temperature=0.3)

with open(os.path.join(os.path.dirname(__file__), "editor_estilo.prompt"), "r", encoding="utf-8") as file:
    editor_estilo_prompt = file.read()

editor_estilo = create_agent(
    model=MODELO,
    system_prompt=editor_estilo_prompt,
    tools=[],
)
