import os
from io import BytesIO
from dotenv import load_dotenv
from speechify import Speechify
from speechify.tts import GetSpeechOptionsRequest
import base64
import streamlit as st

# Load API key
load_dotenv()
SPEECHIFY_API_KEY = os.getenv("SPEECHIFY_API_KEY")

# Initialize Speechify client
speechify_client = None
if SPEECHIFY_API_KEY:
    try:
        speechify_client = Speechify(token=SPEECHIFY_API_KEY)
    except Exception as e:
        print(f"Failed to initialize Speechify client: {e}")

def text_to_speech(text: str, voice_id: str) -> BytesIO | None:
    """
    Convert text to speech using Speechify API.
    
    Args:
        text (str): Text to convert to speech
        voice_id (str): Voice ID to use for synthesis
        
    Returns:
        BytesIO | None: Audio stream or None if error occurs
    """
    if not speechify_client:
        print("Speechify client not initialized. Check SPEECHIFY_API_KEY in .env")
        st.markdown("error")
        return None
    
    try:
        # Convert ElevenLabs voice IDs to Speechify voice IDs for backward compatibility
        voice_mapping = {
            "21m00Tcm4TlvDq8ikWAM": "scott",  # Rachel -> scott
            "EXAVITQu4vr4xnSDxMaL": "scott",  # Bella -> scott  
            "AZnzlk1XvdvUeBnXmlld": "scott",  # Antoni -> scott
            "IKne3meq5aSn9XLyUdCD": "scott",  # Daniel -> scott
        }
        
        # Use mapped voice_id or fallback to provided voice_id
        speechify_voice_id = voice_mapping.get(voice_id, voice_id)
        
        # Determine if text contains non-English characters to choose appropriate model
        # Simple heuristic: if text contains non-ASCII characters, use multilingual model
        is_multilingual = any(ord(char) > 127 for char in text)
        model = "simba-multilingual" if is_multilingual else "simba-english"
        
        # Make TTS request
        audio_response = speechify_client.tts.audio.speech(
            audio_format="mp3",
            input=text,
            model=model,
            options=GetSpeechOptionsRequest(
                loudness_normalization=True,
                text_normalization=True
            ),
            voice_id=speechify_voice_id
        )
        
        # Decode base64 audio data
        audio_bytes = base64.b64decode(audio_response.audio_data)
        
        # Create BytesIO stream
        audio_stream = BytesIO(audio_bytes)
        audio_stream.seek(0)
        
        return audio_stream
        
    except Exception as e:
        print(f"TTS error: {e}")
        st.markdown("error")
        return None

def get_available_voices():
    """
    Get available Speechify voices.
    
    Returns:
        list: List of available voice objects
    """
    if not speechify_client:
        return []
    
    try:
        voices_response = speechify_client.tts.voices.list()
        # The response might be a list directly or have a .voices attribute
        if hasattr(voices_response, 'voices'):
            return voices_response.voices
        elif isinstance(voices_response, list):
            return voices_response
        else:
            print(f"Unexpected voices response structure: {type(voices_response)}")
            return []
    except Exception as e:
        print(f"Error fetching voices: {e}")
        return []

def filter_voice_models(voices, *, gender=None, locale=None, tags=None):
    """
    Filter Speechify voices by gender, locale, and/or tags,
    and return the list of model IDs for matching voices.

    Args:
        voices (list): List of GetVoice objects.
        gender (str, optional): e.g. 'male', 'female'.
        locale (str, optional): e.g. 'en-US'.
        tags (list, optional): list of tags, e.g. ['timbre:deep'].

    Returns:
        list[str]: IDs of matching voice models.
    """
    results = []

    for voice in voices:
        # gender filter
        if gender and voice.gender.lower() != gender.lower():
            continue

        # locale filter (check across models and languages)
        if locale:
            if not any(
                any(lang.locale == locale for lang in model.languages)
                for model in voice.models
            ):
                continue

        # tags filter
        if tags:
            if not all(tag in voice.tags for tag in tags):
                continue

        # If we got here, the voice matches -> collect model ids
        for model in voice.models:
            results.append(model.name)

    return results