import subprocess
import uuid
from pathlib import Path

AUDIO_DIR = Path("data/audio")
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

def synthesize_speech(text: str, language: str) -> str:
    text = text.strip()
    if not text:
        raise ValueError("TTS text is empty")

    audio_path = AUDIO_DIR / f"{uuid.uuid4()}.wav"

    voice_map = {
        "en": "en-US-AriaNeural",
        "fr": "fr-FR-DeniseNeural",
        "hi": "hi-IN-SwaraNeural"
    }

    voice = voice_map.get(language, "en-US-AriaNeural")

    subprocess.run([
        "edge-tts",
        "--voice", voice,
        "--text", text,
        "--write-media", str(audio_path)
    ], check=True)

    return str(audio_path)
