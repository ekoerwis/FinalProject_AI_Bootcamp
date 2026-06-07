import os
from dotenv import load_dotenv
from google import genai

# 1. Memuat (load) API Key dari file .env
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("🚨 Error: API Key tidak ditemukan!")
else:
    print("✅ API Key berhasil dimuat!")
    
    # 2. Inisialisasi Client
    client = genai.Client(api_key=api_key)
    
    print("⏳ Sedang mengirim pesan ke Gemini...")
    
    prompt = (
        "Halo Gemini! Saya sedang menguji koneksi dari komputer lokal "
        "untuk proyek chatbot RAG Onboarding F&B perusahaan. "
        "Tolong balas dengan sapaan singkat dan semangat untuk tim developer kami!"
    )
    
    try:
        # MENGGUNAKAN NAMA MODEL STANDAR BARU UNTUK GEMINI 2.0 FLASH
        response = client.models.generate_content(
            model='models/gemini-2.5-flash',  # Jika ini bawaan SDK baru, pastikan stringnya presisi
            contents=prompt
        )
        
        print("\n🤖 Balasan dari Gemini:")
        print("-" * 40)
        print(response.text)
        print("-" * 40)
        print("🎉 Test BERHASIL! Koneksi lokal dengan SDK baru sukses 100%.")
        
    except Exception as e:
        # Jika nama string di atas masih tersangkut di versi v1beta, kita paksa pakai full-path resmi Google:
        print("🔄 Mencoba jalur alternatif full-path...")
        try:
            response = client.models.generate_content(
                model='models/aqa', 
                contents=prompt
            )
            print("\n🤖 Balasan dari Gemini (Jalur Alternatif):")
            print("-" * 40)
            print(response.text)
            print("-" * 40)
            print("🎉 Test BERHASIL via jalur alternatif!")
        except Exception as e_alt:
            print(f"\n❌ Terjadi kesalahan pada kedua jalur: {e_alt}")