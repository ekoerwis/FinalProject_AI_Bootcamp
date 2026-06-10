import os
import time
import streamlit as st
from datetime import datetime
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from groq import Groq
import gspread
from google.oauth2.service_account import Credentials

# ============================================================
# Konfigurasi Perusahaan
# ============================================================
COMPANY_NAME    = "Katering Yeyeti"
COLLECTION_NAME = "katering_yeyeti"

# ============================================================
# Setup halaman
# ============================================================
st.set_page_config(
    page_title=f"Chatbot Onboarding — {COMPANY_NAME}",
    page_icon="🤖",
    layout="centered"
)

# ============================================================
# Load model & koneksi
# ============================================================
@st.cache_resource
def load_resources():
    embedder = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    qdrant = QdrantClient(
        url=st.secrets["QDRANT_URL"],
        api_key=st.secrets["QDRANT_API_KEY"],
    )
    groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    return embedder, qdrant, groq_client

@st.cache_resource
def load_sheets():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scopes
    )
    client = gspread.authorize(creds)
    sheet = client.open_by_key(st.secrets["SPREADSHEET_ID_KELOMPOK"]).sheet1
    return sheet

embedder, qdrant, groq_client = load_resources()
sheet = load_sheets()

# ============================================================
# Fungsi Log ke Google Sheets
# ============================================================
def log_to_sheets(pertanyaan, jawaban, response_time, score):
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sheet.append_row([
            timestamp,
            pertanyaan,
            jawaban,
            COMPANY_NAME,
            f"{response_time:.2f}",
            f"{score:.4f}"
        ])
    except Exception as e:
        st.warning(f"Log gagal: {e}")

# ============================================================
# Fungsi RAG Chat
# ============================================================
def rag_chat(pertanyaan: str, top_k: int = 11):
    query_vector = embedder.encode(pertanyaan).tolist()

    results = qdrant.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k,
#        with_score=True,
    ).points

    # Ambil rata-rata skor sebagai representasi relevansi dokumen
    avg_score = sum(r.score for r in results) / len(results) if results else 0

    context = "\n\n".join([r.payload["text"] for r in results])

    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": f"""Kamu adalah asisten onboarding karyawan baru di {COMPANY_NAME}.
Jawab pertanyaan HANYA berdasarkan konteks dokumen internal perusahaan yang diberikan.
Gunakan bahasa Indonesia yang ramah dan mudah dipahami.

Kamu dapat menjawab pertanyaan seputar:
- Profil, visi, misi, dan nilai-nilai perusahaan
- Hak dan kewajiban karyawan
- Peraturan dan kebijakan kerja
- Jam kerja, shift, dan sistem absensi serta kode kehadiran
- Benefit, santunan, dan kesejahteraan karyawan
- Prosedur dan SOP operasional dapur
- Standar kebersihan dan keselamatan dapur
- Kebijakan halal dan standar bahan baku
- Produk dan layanan perusahaan
- Penanganan keluhan pelanggan
- Pelaporan insiden dan form laporan harian

Jika informasi tidak ada di konteks, katakan dengan jujur bahwa kamu tidak tahu."""
            },
            {
                "role": "user",
                "content": f"KONTEKS:\n{context}\n\nPERTANYAAN:\n{pertanyaan}"
            }
        ]
    )
    return response.choices[0].message.content, avg_score

# ============================================================
# UI Streamlit
# ============================================================
st.title("🤖 Chatbot Onboarding")
st.subheader(f"{COMPANY_NAME}")
st.caption("Tanyakan apa saja tentang perusahaan, benefit, prosedur, dan kebijakan kerja.")
st.divider()

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant",
        "content": f"Halo! Saya asisten setia, ramah, dan amanah perwakilan {COMPANY_NAME}. Ada yang bisa saya bantu?"
    })

# Tampilkan chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input pertanyaan
if pertanyaan := st.chat_input("Ketik pertanyaan kamu di sini..."):
    # Tampilkan pertanyaan user
    st.session_state.messages.append({"role": "user", "content": pertanyaan})
    with st.chat_message("user"):
        st.markdown(pertanyaan)

    # Generate jawaban + hitung response time
    with st.chat_message("assistant"):
        with st.spinner("Mencari jawaban..."):
            start_time = time.time()
            jawaban, score = rag_chat(pertanyaan)
            response_time = time.time() - start_time
        st.markdown(jawaban)
        st.caption(f"⏱️ {response_time:.2f} detik")
        st.session_state.messages.append({"role": "assistant", "content": jawaban})

    # Log ke Google Sheets
    log_to_sheets(pertanyaan, jawaban, response_time, score)
