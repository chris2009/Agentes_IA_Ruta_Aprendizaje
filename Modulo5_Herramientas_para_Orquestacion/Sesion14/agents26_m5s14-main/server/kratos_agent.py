from langchain.agents import create_agent
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from feedquotes import load_quotes, retriever
from dotenv import load_dotenv
load_dotenv()

@tool
def get_kratos_quote(query:str) -> str:
    """
    Obtiene algunos quotes de referencia dada la categoria a información relevante a ser buscada por medio de RAG.
    Accediendo a una base de datos vectorial se puede obtener inspiración para las respuestas.

    Args:
        query: Categoria o palabra clave que considera para la busqueda en la bd vectorial

    Returns:
        quotes relevantes a la busqueda solicitada
    """
    if retriever is None: load_quotes()
    documentos_relevantes = retriever.invoke(query)
    quotes_encontradas = "\nQuotes encontrados\n".join(doc.page_content for doc in documentos_relevantes)
    return quotes_encontradas

llm = ChatOpenAI(
    model="gpt-4.1",
    temperature=0.3
)

with open("./server/kratos.prompt", "r", encoding="utf-8") as file:
    kratos_prompt = file.read()

kratos = create_agent(
    model=llm,
    system_prompt=kratos_prompt,
    tools=[get_kratos_quote]
)

# while(1):
#     x = input("usted>")
#     if x == "salir":
#         break
#     result = kratos.invoke({"messages": x})
#     print(result["messages"][-1].content)