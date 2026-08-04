"""
Indice vectorial (RAG) sobre los materiales del agente personal, con Chroma.

Recorre materiales/ (todas las subcarpetas de tareas), extrae texto de cada
documento compatible (.pdf, .docx, .txt, .md, .py), lo divide en chunks y lo
indexa en una coleccion Chroma persistente en disco. El resto del proyecto
(agente_planificacion_rag.py) solo llama a buscar() para hacer busqueda
semantica sobre ese indice.

Embeddings: Ollama local (`nomic-embed-text`, mismo servidor Ollama que ya
corre en esta maquina para otros modulos) -- se instala una sola vez con:
    ollama pull nomic-embed-text

Reconstruir el indice a mano (por ejemplo tras agregar documentos nuevos):
    python rag.py --reindexar
"""

import os
import shutil
import sys
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

CARPETA_MATERIALES = Path(__file__).parent / "materiales"
CARPETA_INDICE = Path(__file__).parent / "chroma_index"
NOMBRE_COLECCION = "materiales_agente_personal"
EXTENSIONES_ADMITIDAS = {".pdf", ".docx", ".txt", ".md", ".py"}
MODELO_EMBEDDINGS = os.getenv("OLLAMA_EMBEDDINGS_MODEL", "nomic-embed-text")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

_embeddings: OllamaEmbeddings | None = None
_vector_store: Chroma | None = None


def _obtener_embeddings() -> OllamaEmbeddings:
    global _embeddings
    if _embeddings is None:
        _embeddings = OllamaEmbeddings(model=MODELO_EMBEDDINGS, base_url=OLLAMA_BASE_URL)
    return _embeddings


def _extraer_texto_archivo(ruta: Path) -> str:
    sufijo = ruta.suffix.lower()
    if sufijo in {".txt", ".md", ".py"}:
        return ruta.read_text(encoding="utf-8", errors="ignore")
    if sufijo == ".docx":
        from docx import Document as DocumentoWord
        return "\n".join(p.text for p in DocumentoWord(ruta).paragraphs)
    if sufijo == ".pdf":
        from pypdf import PdfReader
        return "\n".join(pagina.extract_text() or "" for pagina in PdfReader(ruta).pages)
    return ""


def _cargar_documentos() -> tuple[list[Document], list[str]]:
    """Recorre materiales/ y arma un Document (LangChain) por chunk de cada archivo compatible."""
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=120)
    documentos: list[Document] = []
    ids: list[str] = []

    for archivo in sorted(CARPETA_MATERIALES.rglob("*")):
        if not archivo.is_file() or archivo.suffix.lower() not in EXTENSIONES_ADMITIDAS:
            continue
        try:
            texto = _extraer_texto_archivo(archivo)
        except Exception as error:
            print(f"[rag] No se pudo leer {archivo.name}: {error}")
            continue
        if not texto.strip():
            continue

        # Mismo formato que ruta_contexto en tareas.json (ej. "materiales/TareaReAct"),
        # para poder filtrar la busqueda por la carpeta de una tarea especifica.
        ruta_contexto = str(archivo.parent.relative_to(CARPETA_MATERIALES.parent)).replace("\\", "/")

        for i, chunk in enumerate(splitter.split_text(texto)):
            documentos.append(Document(
                page_content=chunk,
                metadata={"archivo": archivo.name, "ruta_contexto": ruta_contexto},
            ))
            ids.append(f"{archivo.relative_to(CARPETA_MATERIALES)}::{i}".replace("\\", "/"))

    return documentos, ids


def construir_o_cargar_indice(forzar_reindexado: bool = False) -> Chroma:
    """Crea el indice si no existe (o si se fuerza), y lo deja listo para buscar()."""
    global _vector_store

    if forzar_reindexado and CARPETA_INDICE.exists():
        shutil.rmtree(CARPETA_INDICE)

    indexar = forzar_reindexado or not CARPETA_INDICE.exists()

    vector_store = Chroma(
        collection_name=NOMBRE_COLECCION,
        persist_directory=str(CARPETA_INDICE),
        embedding_function=_obtener_embeddings(),
    )

    if indexar:
        documentos, ids = _cargar_documentos()
        if documentos:
            vector_store.add_documents(documents=documentos, ids=ids)
            print(f"[rag] Indice construido con {len(documentos)} fragmento(s) de materiales/.")
        else:
            print("[rag] No se encontraron documentos compatibles en materiales/.")

    _vector_store = vector_store
    return vector_store


def buscar(consulta: str, k: int = 4, ruta_contexto: str | None = None) -> list[Document]:
    """Busqueda semantica sobre el indice. Si ruta_contexto se da, filtra por esa carpeta."""
    if _vector_store is None:
        construir_o_cargar_indice()
    filtro = {"ruta_contexto": ruta_contexto} if ruta_contexto else None
    return _vector_store.similarity_search(consulta, k=k, filter=filtro)


if __name__ == "__main__":
    construir_o_cargar_indice(forzar_reindexado="--reindexar" in sys.argv)
