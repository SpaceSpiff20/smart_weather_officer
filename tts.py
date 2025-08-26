import os
from io import BytesIO
from dotenv import load_dotenv
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
import streamlit as st

# Load API key
load_dotenv()
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
elevenlabs = ElevenLabs(api_key=ELEVENLABS_API_KEY)

def text_to_speech(text: str, voice_id: str) -> BytesIO | None:
    try:
        response = elevenlabs.text_to_speech.stream(
            text=text,
            voice_id=voice_id,
            model_id="eleven_multilingual_v2",
            output_format="mp3_22050_32",
            voice_settings=VoiceSettings(
                stability=0.3,
                similarity_boost=0.7,
                style=0.0,
                use_speaker_boost=True,
                speed=1.0
            ),
        )

        audio_stream = BytesIO()
        for chunk in response:
            if chunk:
                audio_stream.write(chunk)
        audio_stream.seek(0)
        return audio_stream
    except Exception as e:
        print(f"TTS error: {e}")
        st.markdown("error")
        return None