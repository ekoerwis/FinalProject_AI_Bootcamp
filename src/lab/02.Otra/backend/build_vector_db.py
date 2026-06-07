from pathlib import Path
from pypdf import PdfReader

import chromadb
from sentence_transformers import SentenceTransformer

client = chromadb.PersistentClient(path="./chroma_db")

collection = client.get_or_create_collection(
    name="fnb_docs"
)

model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

DATA_DIR = Path("data")

doc_id = 0

for pdf_file in DATA_DIR.rglob("*.pdf"):

    company = pdf_file.parent.name
    source = pdf_file.name

    reader = PdfReader(pdf_file)

    text= ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    chunk_size = 500

    for i in range(0, len(text), chunk_size):

        chunk = text[i:i + chunk_size]

        embedding = model.encode(chunk).tolist()

        collection.add(
            ids=[str(doc_id)],
            documents=[chunk],
            embeddings=[embedding],
            metadatas=[{
                "company": company,
                "source": source
            }]
        )

        doc_id += 1

print(f"Indexed {doc_id} chunks")
