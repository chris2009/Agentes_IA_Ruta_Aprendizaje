import os
import pandas as pd
from langchain_ollama import OllamaEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

retriever = None


def load_reviews(aimode: str):
    global retriever

    df = pd.read_csv("data/data.csv")

    if aimode != "1":
        embeddings = OllamaEmbeddings(model="mxbai-embed-large")
        db_location = "./chroma_ollama_rest_reviews"
    else:
        embeddings = OpenAIEmbeddings()
        db_location = "./chroma_openai_rest_reviews"

    add_documents = not os.path.exists(db_location)

    vector_store = Chroma(
        collection_name="restaurant_reviews",
        persist_directory=db_location,
        embedding_function=embeddings,
    )

    if add_documents:
        documents = []
        ids = []

        for i, row in df.iterrows():
            content = (
                f"Nombre Restaurante: {row['Nombre']}\n"
                f"Autor Review: {row['Autor']}\n"
                f"Calificacion: {row['Calificacion']}\n"
                f"Resumen de Review: {row['Review']}\n"
                f"Plato estrella: {row['Plato_Estrella']}\n"
                f"Distrito: {row['Distrito']}\n"
                f"Tipo de comida: {row['Tipo_comida']}\n"
            )
            document = Document(
                page_content=content,
                metadata={"Clasificacion": row["Tipo_comida"]},
                id=str(i),
            )
            ids.append(str(i))
            documents.append(document)

        vector_store.add_documents(documents=documents, ids=ids)

    retriever = vector_store.as_retriever(search_kwargs={"k": 5})
    return retriever


load_reviews("1")  # Load reviews using Ollama embeddings