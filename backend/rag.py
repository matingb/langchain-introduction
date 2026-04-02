import os
from pathlib import Path

from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

VECTORSTORE_DIR = Path(__file__).parent / ".chroma"
COLLECTION_NAME = "pokemon_docs"

_vectorstore: Chroma | None = None


def _get_api_key() -> str:
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Gemini API key not found. Set `GOOGLE_API_KEY` or `GEMINI_API_KEY` before "
            "starting the API."
        )
    return api_key


def _build_embeddings() -> GoogleGenerativeAIEmbeddings:
    return GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        api_key=_get_api_key(),
    )


def _open_vectorstore() -> Chroma:
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=_build_embeddings(),
        persist_directory=str(VECTORSTORE_DIR),
    )


def init_vectorstore() -> None:
    global _vectorstore

    if not VECTORSTORE_DIR.exists():
        raise RuntimeError(
            "RAG index not found. Run `python -m scripts.rag_rebuild` from the `backend` directory "
            "before starting the API."
        )

    vectorstore = _open_vectorstore()
    if not vectorstore.get(limit=1)["ids"]:
        raise RuntimeError(
            "RAG index is empty or invalid. Run `python -m scripts.rag_rebuild` from the `backend` "
            "directory before starting the API."
        )
    _vectorstore = vectorstore


def retrieve(query: str, k: int = 3) -> str:
    if _vectorstore is None:
        return ""
    results = _vectorstore.similarity_search(query, k=k)
    return "\n\n".join(doc.page_content for doc in results)


def retrieve_from_source(query: str, source: str, k: int) -> str:
    if _vectorstore is None:
        return ""
    results = _vectorstore.similarity_search(query, k=k, filter={"source": source})
    return "\n\n".join(doc.page_content for doc in results)
