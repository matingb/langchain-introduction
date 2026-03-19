import os
from functools import lru_cache
from pathlib import Path

from langchain_community.document_loaders import TextLoader
from langchain_core.tools import tool
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

DOCS_DIR = Path(__file__).parent / "docs"


@lru_cache(maxsize=1)
def build_vectorstore() -> InMemoryVectorStore | None:
    docs = []
    for file_path in sorted(DOCS_DIR.glob("*.txt")):
        loader = TextLoader(str(file_path), encoding="utf-8")
        loaded = loader.load()
        docs.extend(d for d in loaded if d.page_content.strip())

    if not docs:
        return None

    splits = RecursiveCharacterTextSplitter(
        chunk_size=500, chunk_overlap=50
    ).split_documents(docs)

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
    )
    return InMemoryVectorStore.from_documents(documents=splits, embedding=embeddings)


@tool
def search_docs(query: str) -> str:
    """Search the internal knowledge base for relevant information.
    Use this to find tips, mechanics, or any topic covered in the docs.
    """
    vectorstore = build_vectorstore()
    if vectorstore is None:
        return "No documents available in the knowledge base."

    results = vectorstore.similarity_search(query, k=3)
    if not results:
        return "No relevant information found."

    return "\n\n".join(doc.page_content for doc in results)
