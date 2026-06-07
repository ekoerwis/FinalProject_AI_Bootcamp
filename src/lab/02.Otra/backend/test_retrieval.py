import chromadb
from sentence_transformers import SentenceTransformer

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection("fnb_docs")

model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

question = "Apa SOP opening Pecel Lele Lala?"

query_embedding = model.encode(question).tolist()

results = collection.query(
    query_embeddings=[query_embedding],
    n_results=3
)

print(results["documents"][0])
