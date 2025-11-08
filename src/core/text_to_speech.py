from elevenlabs import ElevenLabs
from pydub import AudioSegment
import io
import simpleaudio as sa
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

    # ✅ Add 0.5 seconds of silence to avoid cutoff at start
    silence = AudioSegment.silent(duration=100)
    audio = silence + audio

    # Debug info
    # print(f"Audio loaded — duration: {audio.duration_seconds:.2f}s, channels: {audio.channels}")

    # Play from memory using simpleaudio
    play_obj = sa.play_buffer(
        audio.raw_data,
        num_channels=audio.channels,
        bytes_per_sample=audio.sample_width,
        sample_rate=audio.frame_rate
    )
    play_obj.wait_done()
    # print("Playback finished.")
    return