import os
import glob
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
# ---------------------------------------------------------
# IMPORT BARU YANG SUDAH DIPERBARUI SESUAI STANDAR LANGCHAIN
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
# ---------------------------------------------------------

DATA_DIR = "data/Susu Mbok Darmi" 

def run_multifile_ingestion():
    pdf_files = glob.glob(os.path.join(DATA_DIR, "*.pdf"))
    
    if not pdf_files:
        print(f"🚨 Tidak ditemukan file PDF di folder '{DATA_DIR}'.")
        return
        
    print(f"📚 Ditemukan {len(pdf_files)} file PDF untuk diproses.")
    
    all_documents = []
    
    for pdf_path in pdf_files:
        file_name = os.path.basename(pdf_path)
        print(f"📂 Membaca dokumen: {file_name}...")
        try:
            loader = PyMuPDFLoader(pdf_path)
            documents = loader.load()
            all_documents.extend(documents)
            print(f"   ✅ Berhasil memuat {len(documents)} halaman dari {file_name}")
        except Exception as e:
            print(f"   ❌ Gagal membaca {file_name}. Error: {e}")

    if not all_documents:
        print("🚨 Gagal memproses seluruh dokumen. Ingestion dibatalkan.")
        return

    print("\n✂️ Memotong seluruh dokumen menjadi bagian-bagian kecil...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=50
    )
    chunks = text_splitter.split_documents(all_documents)
    print(f"✅ Berhasil memecah menjadi total {len(chunks)} potongan teks dari semua PDF.")

    print("\n🧠 Memuat model embedding (paraphrase-multilingual-MiniLM-L12-v2)...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )

    print("💾 Menyimpan vektor teks ke dalam database Qdrant...")
    # CLASS QDRANT SEKARANG BERUBAH MENJADI QdrantVectorStore
    qdrant = QdrantVectorStore.from_documents(
        chunks,
        embeddings,
        # location=":memory:", 
        path="qdrant_db",  # BERUBAH: Simpan permanen ke folder lokal
        collection_name="onboarding_docs",
    )
    
    print("\n🎉 PROSES INGESTION MULTIFILE SELESAI!")
    print("Semua dokumen sudah terindeks di Qdrant dan siap digunakan untuk tanya-jawab.")

if __name__ == "__main__":
    if not os.path.exists(DATA_DIR):
        print(f"📁 Membuat folder '{DATA_DIR}' karena belum ada...")
        os.makedirs(DATA_DIR)
        print(f"Silakan masukkan file PDF kamu ke folder '{DATA_DIR}' lalu jalankan ulang script ini.")
    else:
        run_multifile_ingestion()