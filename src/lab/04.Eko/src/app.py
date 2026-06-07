import streamlit as st
import sys
import os

# Memastikan Python bisa membaca file rag_pipeline yang ada di folder yang sama
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from rag_pipeline import ask_bot

# Mengatur tampilan halaman web
st.set_page_config(page_title="Onboarding MbokDarmi", page_icon="🥛", layout="centered")

st.title("🥛 Dairysta Bot - MbokDarmi")
st.caption("Asisten AI Cerdas untuk Panduan SOP dan Onboarding Karyawan")
st.divider()

# Inisialisasi memori untuk menyimpan riwayat percakapan (chat history)
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Halo! Saya adalah asisten virtual HR MbokDarmi. Ada yang bisa saya bantu terkait SOP, aturan operasional, atau absensi hari ini?"}
    ]

# Tampilkan seluruh riwayat percakapan di layar
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Kolom input untuk pengguna mengetik pertanyaan
if prompt := st.chat_input("Tanyakan sesuatu tentang SOP Mbok Darmi..."):
    
    # 1. Tampilkan pertanyaan pengguna di layar
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Simpan pertanyaan ke memori
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. Proses jawaban dari AI (dengan animasi loading)
    with st.chat_message("assistant"):
        with st.spinner("Sedang mencari di tumpukan dokumen SOP..."):
            # Memanggil fungsi otak chatbot dari file rag_pipeline.py
            jawaban = ask_bot(prompt)
            st.markdown(jawaban)
    
    # Simpan jawaban ke memori
    st.session_state.messages.append({"role": "assistant", "content": jawaban})