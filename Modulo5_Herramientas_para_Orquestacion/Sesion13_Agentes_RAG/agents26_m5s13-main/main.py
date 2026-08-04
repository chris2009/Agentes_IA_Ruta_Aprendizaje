from dotenv import load_dotenv
from langchain.agents import create_agent
from pydantic import BaseModel, Field
from toolbox import buscar_con_tavily, buscar_reviews_comida_peruana
from prompt import sysprompt
load_dotenv()  # Load environment variables from .env file

class ResearcherResponse(BaseModel):
    descripcion_plato: str = Field(description="Descripción breve del plato recomendado")
    recomendaciones: str = Field(description="Recomendaciones de restaurantes o platos")
    referencias: list[str] = Field(description="Fuentes o documentos usados como referencia")
    tools_usadas: list[str] = Field(description="Nombres de las herramientas utilizadas para responder")


agent = create_agent(model = "openai:gpt-4o-mini",
                     debug=False,
                     system_prompt=sysprompt,
                     tools=[buscar_reviews_comida_peruana, buscar_con_tavily],
                     response_format=ResearcherResponse)

while True:
    user_input = input("Ingrese su consulta (o 'salir' para terminar): ")
    if user_input.lower() == "salir":
        break

    response = agent.invoke({"messages": [{"role": "user", "content": user_input}]},
                            config={"recursion_limit": 10})

    structured = response["structured_response"]

    print("Descripción del plato:", structured.descripcion_plato)
    print("Recomendaciones:", structured.recomendaciones)
    print("Referencias:", structured.referencias)
    print("Herramientas usadas:", structured.tools_usadas)