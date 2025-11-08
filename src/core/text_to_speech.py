from elevenlabs import ElevenLabs
from pydub import AudioSegment
import sounddevice as sd
import numpy as np
import io
import os
import threading
from dotenv import load_dotenv


load_dotenv()
client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

# Global flag to track if audio is playing
_audio_playing = False
_audio_lock = threading.Lock()

def text_to_speech(text_input: str):
    """
    Convert text to speech and play it asynchronously.

    Args:
        text_input: The text to be converted to speech.
    """
    global _audio_playing
    
    # Stream audio from ElevenLabs
    audio_stream = client.text_to_speech.convert(
        voice_id="2EiwWnXFnvU5JabPnv8n",
        model_id="eleven_flash_v2_5",  # Flash model for maximum speed
        text=text_input,
        output_format="mp3_22050_32"  # Lower quality for faster streaming
    )

    # Combine all chunks from generator
    audio_bytes = b"".join(audio_stream)

    # Decode MP3 to AudioSegment
    audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format="mp3")

    # Convert to numpy array for sounddevice
    samples = np.array(audio.get_array_of_samples())
    
    # If stereo, reshape
    if audio.channels == 2:
        samples = samples.reshape((-1, 2))
    
    # Normalize to float32
    samples = samples.astype(np.float32) / (2**15)
    
    def play_audio():
        """Play audio in a separate thread"""
        global _audio_playing
        with _audio_lock:
            _audio_playing = True
        try:
            sd.play(samples, audio.frame_rate, blocking=True)
            sd.wait()  # Wait for playback to finish
        finally:
            with _audio_lock:
                _audio_playing = False
    
    # Start playback in background thread
    thread = threading.Thread(target=play_audio, daemon=True)
    thread.start()

def is_audio_playing() -> bool:
    """Check if audio is currently playing"""
    with _audio_lock:
        return _audio_playing 