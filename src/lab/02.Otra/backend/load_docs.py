from pypdf import PdfReader
from pathlib import Path

DATA_DIR = Path("data")

for pdf_file in DATA_DIR.rglob("*.pdf"):
    try:
        reader = PdfReader(pdf_file)

        text = ""

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text

        print("\n" + "="*60)
        print(pdf_file)
        print(text[:300])

    except Exception as e:
        print(f"ERROR {pdf_file}: {e}")
