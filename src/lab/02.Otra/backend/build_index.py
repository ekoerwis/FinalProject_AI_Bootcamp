from pypdf import PdfReader
from pathlib import Path

chunks = []

DATA_DIR = Path("data")

for pdf_file in DATA_DIR.rglob("*.pdf"):

    company = pdf_file.parent.name
    source = pdf_file.name

    reader = PdfReader(pdf_file)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    chunk_size = 500

    for i in range(0, len(text), chunk_size):

        chunk = text[i:i + chunk_size]

        chunks.append({
            "company": company,
            "source": source,
            "content": chunk
        })

print(f"Total chunks: {len(chunks)}")

print(chunks[0])
