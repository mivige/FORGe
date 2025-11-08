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

def text_to_speech(text_input: str) -> float:
    """
    Convert text to speech and play it asynchronously.
    Returns the estimated duration so caller can sleep if needed.

    Args:
        text_input: The text to be converted to speech.
        
    Returns:
        Actual audio duration in seconds
    """
    global _audio_playing
    
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
    
    # Calculate actual duration
    duration = len(audio) / 1000.0  # Convert ms to seconds

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
    
    # Return actual duration
    return duration

def is_audio_playing() -> bool:
    """Check if audio is currently playing"""
    with _audio_lock:
        return _audio_playing