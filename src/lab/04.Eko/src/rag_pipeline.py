import os
from dotenv import load_dotenv
from google import genai
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore

# 1. Load API Key Gemini
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("🚨 API Key tidak ditemukan. Pastikan ada di file .env")

# 2. Inisialisasi Client Gemini
client = genai.Client(api_key=api_key)

# 3. Hubungkan kembali ke database Qdrant yang tadi kita buat
print("🧠 Memuat otak pencarian (Qdrant & Model MiniLM)...")
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

# Ambil data dari folder qdrant_db lokal
qdrant = QdrantVectorStore.from_existing_collection(
    embedding=embeddings,
    collection_name="onboarding_docs",
    path="qdrant_db"
)

def ask_bot(question: str):
    """Fungsi utama untuk bertanya ke Bot"""
    print(f"\n❓ PERTANYAAN: {question}")
    print("🔍 Sedang mencari dokumen SOP MbokDarmi yang relevan...")
    
    # A. Cari 3 dokumen paling mirip dengan pertanyaan
    search_results = qdrant.similarity_search(question, k=11)
    
    # B. Gabungkan teks dari 3 dokumen tersebut
    context_text = "\n\n---\n\n".join([doc.page_content for doc in search_results])
    
    if not context_text.strip():
        return "Maaf, saya tidak menemukan informasi tersebut di dalam dokumen."

    print("🤖 Mengirim dokumen ke Gemini untuk merangkum jawaban...")
    
    # C. Buat Prompt ketat (System Instruction) agar AI tidak mengarang
    prompt = f"""Kamu adalah asisten HR dan operasional untuk perusahaan minuman MbokDarmi.
Tugasmu adalah menjawab pertanyaan karyawan berdasarkan dokumen SOP perusahaan.

KONTEKS DOKUMEN:
{context_text}

PERTANYAAN KARYAWAN:
{question}

ATURAN MENJAWAB:
1. Jawab HANYA berdasarkan konteks dokumen di atas.
2. Jika jawabannya tidak ada di konteks, katakan dengan sopan "Maaf, saya tidak menemukan informasi tersebut di buku panduan." JANGAN pernah mengarang jawaban sendiri.
3. Jawab dengan bahasa Indonesia yang ramah, profesional, dan semangat.
"""
    
    try:
        # D. Panggil Gemini (Jika error 429 masih muncul, ingat trik pakai Colab/Akun lain)
        response = client.models.generate_content(
            model='models/gemini-2.5-flash-lite', 
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"❌ Terjadi kesalahan saat menghubungi Gemini: {e}"

# Untuk pengujian langsung di terminal
if __name__ == "__main__":
    print("✅ Sistem RAG MbokDarmi Siap Diuji!\n")
    
    # Mari kita tes dengan pertanyaan yang pasti ada di SOP Opening Outlet
    # pertanyaan_tes = "Bagaimana Ketentuan Absensi Harian ?"
    # pertanyaan_tes = "Gimana kiriman whatsapps nya ?"
    pertanyaan_tes = "Kode Absen nya apa saja ?"
    
    jawaban = ask_bot(pertanyaan_tes)
    
    print("\n💡 JAWABAN BOT:")
    print("=" * 60)
    print(jawaban)
    print("=" * 60)