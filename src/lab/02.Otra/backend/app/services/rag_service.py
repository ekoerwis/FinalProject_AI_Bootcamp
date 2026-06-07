import chromadb
from sentence_transformers import SentenceTransformer

client = chromadb.PersistentClient(path="./chroma_db")

collection = client.get_collection("fnb_docs")

model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

def rag_search(question: str, brand: str = None) -> str:
    try:

        query_embedding = model.encode(question).tolist()

        where_filter = {"brand": brand} if brand else None

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=3,
            where=where_filter
        )

        docs = results["documents"][0]
        metadatas = results["metadatas"][0]

        for doc, meta in zip(docs, metadatas):

            source = meta["source"]

            if "SOP" in source:
                return doc.replace("\\n", "\n")

        return docs[0].replace("\\n", "\n")

    except Exception as e:
        return f"Dokumen tidak ditemukan. ({str(e)})"
