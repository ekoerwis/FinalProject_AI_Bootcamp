import os
from dotenv import load_dotenv
from google import genai
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
import time
import pandas as pd
from datetime import datetime

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

def save_to_excel(filename, data):
    """Fungsi untuk menyimpan data ke file Excel"""
    df_new = pd.DataFrame([data])
    if os.path.exists(filename):
        df_existing = pd.read_excel(filename)
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_combined = df_new
    df_combined.to_excel(filename, index=False)

def ask_bot(question: str):
    start_time = time.time() # Mulai hitung waktu

    """Fungsi utama untuk bertanya ke Bot"""
    print(f"\n❓ PERTANYAAN: {question}")
    print("🔍 Sedang mencari dokumen SOP MbokDarmi yang relevan...")
    
    # A. Cari 3 dokumen paling mirip dengan pertanyaan
    # search_results = qdrant.similarity_search(question, k=11)
    search_results = qdrant.similarity_search_with_score(question, k=11)

    # Ambil score tertinggi (dokumen pertama)
    top_score = search_results[0][1]
    
    # B. Gabungkan teks dari 3 dokumen tersebut
    # context_text = "\n\n---\n\n".join([doc.page_content for doc in search_results])
    context_text = "\n\n---\n\n".join([doc[0].page_content for doc in search_results])
    
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

        # Mengakses metadata penggunaan token dari Gemini
        metadata = response.usage_metadata
        prompt_tokens = metadata.prompt_token_count
        response_tokens = metadata.candidates_token_count
        total_tokens = metadata.total_token_count
        # ------------------------

        end_time = time.time() # Selesai hitung waktu
        response_time = round(end_time - start_time, 2)

        # Simpan ke Excel
        log_data = {
            "Waktu": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Pertanyaan": question,
            "Jawaban": response.text,
            "Response Time (s)": response_time,
            "Score": top_score,
            "Input Token": prompt_tokens,    # <--- Tambahan
            "Output Token": response_tokens, # <--- Tambahan
            "Total Token": total_tokens      # <--- Tambahan
        }
        save_to_excel("chat_history_analisa.xlsx", log_data)
        
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