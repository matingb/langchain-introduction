from langchain_chroma import Chroma

from rag import COLLECTION_NAME, VECTORSTORE_DIR

store = Chroma(
    collection_name=COLLECTION_NAME,
    persist_directory=str(VECTORSTORE_DIR),
)
data = store.get(include=["documents", "metadatas"])
for meta, doc in zip(data["metadatas"], data["documents"]):
    print(meta)
    print(doc[:2000])
    print("---")
