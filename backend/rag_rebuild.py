import os
import re
import shutil
import time

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from rag import COLLECTION_NAME, VECTORSTORE_DIR

DOCS_DIR = VECTORSTORE_DIR.parent / "docs"
_SECTION_PATTERN = re.compile(r"^=== (.+?) ===$", re.MULTILINE)
_RETRY_DELAY_PATTERN = re.compile(r"retry in ([0-9]+(?:\.[0-9]+)?)s", re.IGNORECASE)

BATCH_SIZE = 20
BATCH_PAUSE_SECONDS = 60


def _get_api_key() -> str:
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Gemini API key not found. Export `GOOGLE_API_KEY` or `GEMINI_API_KEY` in the "
            "shell before running `python -m rag_rebuild`."
        )
    return api_key


def _build_embeddings() -> GoogleGenerativeAIEmbeddings:
    return GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        api_key=_get_api_key(),
    )


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


def _load_documents() -> list[Document]:
    docs: list[Document] = []
    for file_path in sorted(DOCS_DIR.glob("*.txt")):
        text = file_path.read_text(encoding="utf-8")
        docs.extend(_split_by_sections(text, file_path.name))
    return docs


def _iter_batches(docs: list[Document]) -> list[list[Document]]:
    return [docs[i : i + BATCH_SIZE] for i in range(0, len(docs), BATCH_SIZE)]


def _get_retry_delay(exc: Exception) -> float | None:
    message = str(exc)
    if "429" not in message and "RESOURCE_EXHAUSTED" not in message:
        return None

    match = _RETRY_DELAY_PATTERN.search(message)
    if match:
        return float(match.group(1)) + 1
    return float(BATCH_PAUSE_SECONDS)


def _add_batch_with_retry(
    vectorstore: Chroma,
    batch: list[Document],
    batch_index: int,
    batch_count: int,
) -> None:
    while True:
        try:
            print(
                f"Indexing batch {batch_index}/{batch_count} "
                f"({len(batch)} documents)..."
            )
            vectorstore.add_documents(batch)
            return
        except Exception as exc:
            retry_delay = _get_retry_delay(exc)
            if retry_delay is None:
                raise
            print(
                f"Batch {batch_index}/{batch_count} hit rate limit. "
                f"Retrying in {retry_delay:.1f}s..."
            )
            time.sleep(retry_delay)


def rebuild_vectorstore() -> None:
    docs = _load_documents()
    if not docs:
        raise RuntimeError("No documents found in backend/docs to index.")

    if VECTORSTORE_DIR.exists():
        shutil.rmtree(VECTORSTORE_DIR)
    VECTORSTORE_DIR.mkdir(parents=True, exist_ok=True)

    vectorstore = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=_build_embeddings(),
        persist_directory=str(VECTORSTORE_DIR),
    )
    batches = _iter_batches(docs)
    for index, batch in enumerate(batches, start=1):
        _add_batch_with_retry(vectorstore, batch, index, len(batches))
        if index < len(batches):
            print(f"Sleeping {BATCH_PAUSE_SECONDS}s before next batch...")
            time.sleep(BATCH_PAUSE_SECONDS)


def main() -> int:
    rebuild_vectorstore()
    print(f"RAG index rebuilt in {VECTORSTORE_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
