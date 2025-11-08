from elevenlabs import ElevenLabs
from pydub import AudioSegment
from pydub.playback import play
import io
import os
from dotenv import load_dotenv


load_dotenv()
client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

def text_to_speech(text_input: str):
    """
    Convert text to speech and play it.

    Args:
        text_input: The text to be converted to speech.
    """
    # Stream audio from ElevenLabs
    audio_stream = client.text_to_speech.convert(
        voice_id="2EiwWnXFnvU5JabPnv8n",
        model_id="eleven_multilingual_v2",
        text=text_input
    )

    # Combine all chunks from generator
    audio_bytes = b"".join(audio_stream)

    # Decode MP3 to AudioSegment
    audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format="mp3")

    # Add small silence to avoid cutoff at start
    silence = AudioSegment.silent(duration=100)
    audio = silence + audio

    # Play and wait for completion using pydub's play (blocks until done)
    #play(audio)
    return