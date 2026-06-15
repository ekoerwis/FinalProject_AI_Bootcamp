# RAG Onboarding Chatbot for F&B Industry

<p align="center">
  <img src="assets/Pipeline_RAG_Final_Bootcamp.png" width="600"/>
</p>

> Final Project AI Bootcamp NaLaPro Batch 10  
> Retrieval-Augmented Generation (RAG) untuk onboarding karyawan baru di industri F&B

---

## Demo

Chatbot live dan bisa diakses di:  https://finalprojectaibootcamp-katering.streamlit.app

---

## Deskripsi Proyek

Chatbot berbasis RAG yang dirancang untuk membantu karyawan baru memahami dokumen internal perusahaan secara interaktif. Sistem ini memungkinkan pengguna mengajukan pertanyaan dalam bahasa natural dan mendapatkan jawaban yang relevan berdasarkan dokumen resmi perusahaan, tanpa perlu membaca seluruh dokumen secara manual.

Proyek ini menggunakan **Katering Yeyeti** sebagai studi kasus, dengan dataset dokumen internal perusahaan.

---

## Dataset

| Perusahaan | Brand | Dokumen |
|---|---|---|
| Yeyeti Katering & Peyek Yeyeti | Katering Yeyeti | 11 PDF |

**Total: 11 dokumen PDF · 31 halaman · 145 chunks**

---

## Tech Stack

| Komponen | Teknologi |
|---|---|
| Orchestration | LangChain |
| Language Model | Groq: LLaMA 3.1 8B Instant |
| Embedding Model | `paraphrase-multilingual-MiniLM-L12-v2` |
| Vector Database | Qdrant Cloud |
| Compute | Google Colab + T4 GPU |
| Document Storage | Google Drive |
| UI | Streamlit |
| Chat Logging | Google Sheets API |
| Evaluation | ROUGE Score |

> Estimasi pemakaian: ~1.400 tokens per request (960 input + 396 output) dengan model LLaMA 3.1 8B Instant

---

## Mengapa Groq + LLaMA?

Dalam arsitektur RAG, kualitas sistem tidak hanya ditentukan oleh LLM-nya — informasi faktual justru sebagian besar berasal dari dokumen yang di-retrieve. Karena itu, model flagship yang sangat mahal bukan keharusan. Berikut alasan pemilihan **Groq + LLaMA 3.1**:

| # | Alasan | Penjelasan |
|---|--------|------------|
| 1 | **Latensi sangat rendah** | Groq menggunakan arsitektur LPU (*Language Processing Unit*) khusus — token generation jauh lebih cepat dari GPU konvensional, membuat respons chatbot terasa real-time. |
| 2 | **Cost efficiency** | Biaya operasional jauh lebih rendah dibanding model flagship (GPT, Claude). Cocok untuk prototipe dan deployment skala menengah. |
| 3 | **Kesesuaian dengan RAG** | LLM dalam RAG lebih berfungsi sebagai *reasoning + response engine*, bukan sumber pengetahuan. LLaMA mampu menghasilkan jawaban berkualitas baik ketika diberi konteks yang relevan. |
| 4 | **Open-weight model** | LLaMA adalah model open-weight — tidak terikat satu provider. Jika Groq tidak digunakan, model yang sama bisa dijalankan via Together AI, Fireworks, Replicate, atau local inference. |
| 5 | **Kualitas memadai untuk use case** | Use case onboarding (tanya-jawab berbasis dokumen) tidak memerlukan reasoning kompleks tingkat tinggi. Performa LLaMA sudah sangat memadai dikombinasikan dengan retrieval yang baik. |
| 6 | **Skalabilitas** | Throughput tinggi + biaya terkendali = fondasi yang siap untuk peningkatan jumlah pengguna di masa depan. |

> **Kesimpulan:** Groq + LLaMA dipilih karena memberikan kombinasi seimbang antara kecepatan, efisiensi biaya, kualitas jawaban, dan fleksibilitas deployment — tanpa overhead model premium yang tidak diperlukan untuk use case ini.
>
> *Catatan: Groq dipilih setelah evaluasi dengan Gemini Flash (Google) yang terkendala quota limit di free tier, sehingga mengganggu stabilitas pipeline selama pengembangan.*

---

## Cara Kerja RAG Pipeline

```
PDF Dokumen → Chunking → Embedding → Qdrant Cloud
                                           ↓
Pertanyaan User → Embedding → Vector Search → Context + Pertanyaan → LLM → Jawaban
                                                                              ↓
                                                                    Log → Google Sheets
```

1. **Load** - Dokumen PDF dibaca menggunakan PyMuPDF
2. **Chunking** - Dokumen dipecah menjadi potongan 500 karakter dengan overlap 50 karakter
3. **Embedding** - Tiap chunk dikonversi menjadi vektor menggunakan SentenceTransformers
4. **Store** - Vektor disimpan permanen di Qdrant Cloud
5. **Retrieve** - Pertanyaan user di-embed, lalu dicari chunk paling relevan via cosine similarity
6. **Generate** - Context + pertanyaan dikirim ke Groq LLaMA 3.1 untuk menghasilkan jawaban
7. **Log** - Setiap percakapan otomatis tercatat di Google Sheets (timestamp, pertanyaan, jawaban, perusahaan, response time)

---

## Tipe RAG yang Digunakan

Sistem ini menggunakan pendekatan **Enhanced RAG** — bukan Naive RAG standar.

**Naive RAG** adalah pipeline paling dasar: dokumen di-retrieve → digabung dengan pertanyaan → dikirim ke LLM. Tidak ada mekanisme tambahan di dalamnya.

**Enhanced RAG** yang diimplementasikan pada proyek ini menambahkan beberapa komponen di atas pipeline dasar tersebut:

| Komponen | Keterangan |
|---|---|
| **Query Contextualization** | Pertanyaan lanjutan (mis. *"itu apa?"*) ditulis ulang menjadi pertanyaan mandiri sebelum masuk ke Qdrant — meningkatkan akurasi retrieval |
| **Dynamic Top-K** | Jumlah chunk yang diambil menyesuaikan tipe pertanyaan: lebih banyak untuk pertanyaan menu, lebih sedikit untuk pertanyaan umum |
| **Multi-turn Memory** | 3 pesan terakhir disertakan ke LLM di setiap request — menjaga konsistensi jawaban antar giliran |
| **Confidence Score** | Rata-rata cosine similarity ditampilkan ke user — jika di bawah threshold, user diingatkan untuk konfirmasi ke supervisor |
| **Anti-hallucination Guardrail** | System prompt berlapis dengan 7 aturan eksplisit — mencegah LLM mengarang informasi yang tidak ada di dokumen |

Pendekatan ini dipilih karena pipeline dasar Naive RAG tidak cukup untuk menangani percakapan multi-giliran dan pertanyaan ambigu yang umum terjadi dalam konteks onboarding karyawan baru.

---

## Limitasi & Rekomendasi

**Limitasi:**
- RAG adalah sistem *pencari + penjawab*, bukan *penghitung*. Pertanyaan yang membutuhkan kalkulasi atau enumerasi total tidak selalu dijawab dengan akurat.
- Kualitas jawaban sangat bergantung pada kualitas dan kelengkapan dokumen sumber.
- Sistem dirancang untuk satu perusahaan per sesi, tidak mendukung pencarian lintas perusahaan.
- Sistem memberikan hasil optimal ketika pertanyaan disampaikan dalam bahasa Indonesia yang jelas dan deskriptif. Pertanyaan dengan banyak singkatan, typo, atau bahasa non-formal dapat menurunkan akurasi pencarian dokumen.

**Rekomendasi penggunaan:**
- Gunakan pertanyaan yang **spesifik dan deskriptif** untuk hasil optimal.
-  `"Sebutkan semua menu nasi box di Yeyeti Katering"`
-  `"Berapa banyak menu di Yeyeti Katering?"`
- Untuk pertanyaan enumerasi, tambahkan kata kunci seperti *"sebutkan"*, *"jelaskan"*, atau *"apa saja"*.

**Rekomendasi pengembangan:**
- Tambahkan **query preprocessing** (normalisasi teks, koreksi typo) agar chatbot dapat melayani semua lapisan karyawan, termasuk yang terbiasa menggunakan bahasa sehari-hari atau informal.
- Tambahkan **query expansion** LLM memparafrase ulang pertanyaan user sebelum dicari ke Qdrant untuk meningkatkan akurasi retrieval.

---

##  Struktur Folder

```
FinalProject_AI_Bootcamp/
│
├── src/
│   ├── FinalPresentasi/
│   │   ├── assets/
│   │   │   └── Pipeline_RAG_Final_Bootcamp.png
│   │   ├── notebooks/
│   │   │   └── RAG_kateringyeyeti.ipynb
│   │   ├── scripts/
│   │   │   └── rag_kateringyeyeti.py
│   │   ├── README.md
│   │   ├── app.py
│   │   ├── gitignore.txt
│   │   └── requirements.txt
│   │
│   └── lab/
│       ├── 01.Yasmin/
│       ├── 02.Otra/backend/
│       ├── 03.Wahid/
│       ├── 04.Eko/
│       └── 05.Idris/
│
├── .gitignore
└── README.md
```

---

##  Cara Menjalankan

### Prasyarat
- Akun Google (untuk Colab & Drive)
- API Key: [Groq](https://console.groq.com) · [Qdrant Cloud](https://cloud.qdrant.io)
- Service Account Google Cloud (untuk logging ke Google Sheets)

### Langkah-langkah

1. **Upload notebook** ke Google Colab
2. **Ganti runtime** ke T4 GPU: `Runtime → Change runtime type → T4 GPU`
3. **Simpan API Keys** di Colab Secrets:
   - `GROQ_API_KEY`
   - `QDRANT_URL`
   - `QDRANT_API_KEY`
4. **Sesuaikan path** Google Drive di Cell 3 jika diperlukan
5. **Run All** - pipeline akan berjalan otomatis dari load PDF hingga chatbot siap digunakan
6. Gunakan **Cell Test** di bagian bawah notebook untuk mulai bertanya

### Deploy Streamlit

1. Push repo ke GitHub
2. Buka [share.streamlit.io](https://share.streamlit.io)
3. Connect ke repo, pilih `app.py` sebagai main file
4. Tambahkan Secrets di Streamlit Cloud:
   ```toml
   GROQ_API_KEY = "..."
   QDRANT_URL = "..."
   QDRANT_API_KEY = "..."
   SPREADSHEET_ID_KELOMPOK = "..."

   [gcp_service_account]
   type = "service_account"
   project_id = "..."
   private_key_id = "..."
   private_key = "..."
   client_email = "..."
   client_id = "..."
   ```

---

## Author

## Anggota Tim NLP - B - NaLaPro
- [Wahid Setio Darmadi](https://github.com/whddarmadi)
- [M. Dhimas Agung Sugiharto](https://github.com/otrahigus)
- [Yasmin Kamila](https://github.com/yasminkamila)
- [Eko Erwis Wandoko](https://github.com/ekoerwis)

---

*Built with Python · LangChain · Groq · Qdrant · Google Colab · Streamlit · Google Sheets*
