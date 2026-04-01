import os
import re
from pathlib import Path

from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings

DOCS_DIR = Path(__file__).parent / "docs"

_SECTION_PATTERN = re.compile(r"^=== (.+?) ===$", re.MULTILINE)

_vectorstore: InMemoryVectorStore | None = None


def _split_by_sections(text: str, source: str) -> list[Document]:
    matches = list(_SECTION_PATTERN.finditer(text))
    documents = []
    for i, match in enumerate(matches):
        name = match.group(1)
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        if body:
            documents.append(
                Document(
                    page_content=f"=== {name} ===\n{body}",
                    metadata={"name": name, "source": source},
                )
            )
    return documents


def init_vectorstore() -> None:
    global _vectorstore
    docs: list[Document] = []
    for file_path in sorted(DOCS_DIR.glob("*.txt")):
        text = file_path.read_text(encoding="utf-8")
        docs.extend(_split_by_sections(text, file_path.name))

    if not docs:
        return

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
    )
    _vectorstore = InMemoryVectorStore.from_documents(documents=docs, embedding=embeddings)


def retrieve(query: str, k: int = 3) -> str:
    if _vectorstore is None:
        return ""
    results = _vectorstore.similarity_search(query, k=k)
    return "\n\n".join(doc.page_content for doc in results)
