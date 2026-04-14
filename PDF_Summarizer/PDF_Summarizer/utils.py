

from pypdf import PdfReader
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load env
load_dotenv()

# ✅ Groq client (IMPORTANT CHANGE)
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

def extract_text(pdf):
    text = ""
    reader = PdfReader(pdf)

    for page in reader.pages:
        text += page.extract_text() or ""

    return text


# Split text into chunks
def chunk_text(text, chunk_size=4000):
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]


# Summarize chunk
def summarize_chunk(chunk):
    response = client.chat.completions.create(
        model= "llama-3.1-8b-instant",   # ✅ Groq model (CHANGE)
        messages=[
            {
                "role": "user",
                "content": f"Summarize this in 3-4 concise bullet points:\n{chunk}"
            }
        ],
        temperature=0.3,
        max_tokens=200
    )

    return response.choices[0].message.content


# Main function
def summarizer(pdf):
    if pdf is None:
        return "No PDF uploaded."

    text = extract_text(pdf)

    if not text.strip():
        return "No text found in PDF."

    try:
        chunks = chunk_text(text)
        summaries = []

        for chunk in chunks[:3]:  # limit for cost
            summaries.append(summarize_chunk(chunk))

        return "\n\n".join(summaries)

    except Exception as e:
        return f"Error: {str(e)}"