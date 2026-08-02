import os
import json
import uuid

from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file
global retriever
retriever = None
def load_quotes():
    
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    db_location = "./chroma_kratos"
    add_documents = not os.path.exists(db_location)

    vector_store = Chroma(
        collection_name="kratos_quotes",
        persist_directory=db_location,
        embedding_function=embeddings,
    )

    with open("./server/quotes.json", "r") as file:
        items = json.load(file)

    if add_documents:
        documents = []
        ids = []

        for item in items:
            content = (
                item
            )
            this_id = str(uuid.uuid4())
            document = Document(
                page_content=content,
                metadata={"Clasificacion": item["categoria"]},
                id=this_id,
            )
            ids.append(this_id)
            documents.append(document)

        vector_store.add_documents(documents=documents, ids=ids)

    retriever = vector_store.as_retriever(search_kwargs={"k": 5})
    return retriever

retriever = load_quotes()