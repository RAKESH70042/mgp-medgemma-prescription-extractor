import os
from dotenv import load_dotenv

load_dotenv()

def transcribe_audio(audio_path: str) -> str:
    if audio_path is None:
        return "No audio recorded. Please record something first."
    try:
        from groq import Groq
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        with open(audio_path, "rb") as f:
            transcription = client.audio.transcriptions.create(
                model="whisper-large-v3-turbo",
                file=f,
                response_format="text"
            )
        return transcription
    except Exception as e:
        return f"Error: {str(e)}"