import os
from dotenv import load_dotenv
from langchain.tools import tool
from vector import retriever
from tavily import TavilyClient

load_dotenv()  # Load environment variables from .env file
tavily_key = os.getenv("TAVILY_API_KEY")


@tool
def buscar_reviews_comida_peruana(query: str) -> str:
    """
    Busca reseñas de comida peruana hechas por youtubers en la base de datos vectorial.

    Usa esta herramienta cuando el usuario pregunte por platos, restaurantes o
    experiencias gastronómicas peruanas, para obtener opiniones y recomendaciones
    reales extraídas de videos de reseñas.

    Args:
        query: Consulta o tema de búsqueda (ej. nombre de un plato, restaurante o ciudad).

    Returns:
        Texto con los fragmentos de reseñas más relevantes encontrados.
    """
    documentos_relevantes = retriever.invoke(query)
    reviews_encontradas = "\n\n".join(doc.page_content for doc in documentos_relevantes)
    return reviews_encontradas

@tool
def buscar_con_tavily(query: str) -> str:
    """
    Busca información relevante en la web usando Tavily.

    Usa esta herramienta cuando el usuario pregunte por información general sobre
    comida peruana, restaurantes, recetas o cultura culinaria, para obtener datos
    actualizados y confiables de la web.

    Args:
        query: Consulta o tema de búsqueda (ej. historia de un plato, mejores restaurantes).

    Returns:
        Texto con los resultados más relevantes encontrados en la web.
    """
    client = TavilyClient(tavily_key)
    response = client.search(
        query=query,
        search_depth="advanced",
    )

    resultados = response.get("results", [])
    if not resultados:
        return f"No se encontraron resultados en la web para '{query}'."

    texto_resultados = "\n\n".join(
        f"{r.get('title', 'Sin título')}\n{r.get('content', '')}\nFuente: {r.get('url', '')}"
        for r in resultados
    )
    return texto_resultados