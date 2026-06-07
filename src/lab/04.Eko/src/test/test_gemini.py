import os
from dotenv import load_dotenv
from google import genai

# Load .env
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

# Init client
client = genai.Client(api_key=api_key)

# Prompt
prompt = "Halo Gemini, balas singkat."

# Generate
response = client.models.generate_content(
    model="models/gemini-2.5-flash",
    contents=prompt
)

print(response.text)