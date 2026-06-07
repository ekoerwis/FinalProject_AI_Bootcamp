import chromadb

client = chromadb.PersistentClient(path="./chroma_db")

collection = client.get_collection("fnb_docs")

print("Total docs:", collection.count())
