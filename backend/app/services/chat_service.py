from dotenv import load_dotenv
import os
from groq import Groq
from app.services.rag_service import rag_search

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def detect_brand(message: str) -> str | None:
    message_lower = message.lower()

    if "pecel lele" in message_lower or "lala" in message_lower:
        return "Pecel Lele Lala"
    elif "yeyeti" in message_lower or "katering" in message_lower:
        return "Katering Yeyeti"
    elif "mbok darmi" in message_lower or "susu" in message_lower:
        return "Susu Mbok Darmi"

    return None

def get_response(message: str, brand: str = None) -> str:
    try:
        
        brand = detect_brand(message)

        doc = rag_search(message, brand=brand)

        if not doc:
            return "Maaf, saya tidak menemukan informasi yang relevan."

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"Kamu adalah asisten internal {brand or 'perusahaan'}."
                        "Jawab berdasarkan dokumen SOP yang diberikan. "
                        "Gunakan bahasa Indonesia yang sopan dan ringkas."
                    )
                 },
                 {
                     "role": "user",
                     "content": f"Dokumen SOP:\n{doc}\n\nPertanyaan: {message}"
                 }
             ],
             max_tokens=1024
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Error: {str(e)}"
