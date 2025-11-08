"""
Speech-to-Text module with separate audio capture and recognition components.
"""

import json
import queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer


class AudioCapture:
    """
    Handles real-time audio capture from microphone using sounddevice.
    Manages audio streaming and device configuration.
    """
    
    def __init__(self, sample_rate: int = 16000, channels: int = 1, blocksize: int = 8000):
        """
        Initialize the audio capture system.
        
        Args:
            sample_rate: Audio sample rate in Hz (default: 16000)
            channels: Number of audio channels, 1 for mono (default: 1)
            blocksize: Number of frames per buffer (default: 8000)
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.blocksize = blocksize
        self.audio_queue = queue.Queue()
        self.stream = None
    
    def _audio_callback(self, indata, frames, time_info, status):
        """
        Internal callback function invoked by sounddevice for each audio block.
        Converts incoming audio data to bytes and queues it for processing.
        
        Args:
            indata: Input audio data as numpy array
            frames: Number of frames in the buffer
            time_info: Time information dictionary
            status: Status flags indicating any issues
        """
        if status:
            print(f"[AudioCapture] Warning: {status}")
        
        # Convert numpy array to bytes and add to processing queue
        self.audio_queue.put(bytes(indata))
    
    def start_stream(self, device=None):
        """
        Start capturing audio from the microphone.
        Creates and starts an input stream that continuously captures audio.
        
        Args:
            device: Audio device index (None uses default device)
            
        Returns:
            The active audio stream object
        """
        # Clear any existing audio data in the queue
        self._clear_queue()
        
        print(f"[AudioCapture] Starting audio stream (Sample rate: {self.sample_rate} Hz, Channels: {self.channels})")
        
        # Create the audio input stream
        self.stream = sd.RawInputStream(
            samplerate=self.sample_rate,
            blocksize=self.blocksize,
            device=device,
            dtype='int16',  # 16-bit audio
            channels=self.channels,
            callback=self._audio_callback
        )
        
        self.stream.start()
        return self.stream
    
    def stop_stream(self):
        """
        Stop the audio stream and release resources.
        Should be called when audio capture is no longer needed.
        """
        if self.stream:
            print("[AudioCapture] Stopping audio stream...")
            self.stream.stop()
            self.stream.close()
            self.stream = None
    
    def get_audio_data(self, block=True, timeout=None):
        """
        Retrieve captured audio data from the queue.
        This is called by the recognition system to get audio for processing.
        
        Args:
            block: Whether to wait for data if queue is empty (default: True)
            timeout: Maximum time to wait in seconds (None = wait forever)
            
        Returns:
            Bytes object containing raw audio data
            
        Raises:
            queue.Empty: If no data available and block=False or timeout exceeded
        """
        return self.audio_queue.get(block=block, timeout=timeout)
    
    def _clear_queue(self):
        """
        Remove all pending audio data from the queue.
        Used when starting a new stream to avoid processing old data.
        """
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break
    
    def is_active(self):
        """
        Check if the audio stream is currently active.
        
        Returns:
            Boolean indicating if stream is running
        """
        return self.stream is not None and self.stream.active
    
    @staticmethod
    def list_devices():
        """
        Display all available audio input devices.
        Useful for selecting a specific microphone.
        """
        print("[AudioCapture] Available audio devices:")
        print(sd.query_devices())


class VoskRecognizer:
    """
    Handles speech recognition using the Vosk offline recognition engine.
    Processes audio data and converts it to text.
    """
    
    def __init__(self, model_path: str, sample_rate: int = 16000):
        """
        Initialize the Vosk speech recognizer with a language model.
        
        Args:
            model_path: Path to the Vosk model directory
            sample_rate: Audio sample rate in Hz, must match audio capture (default: 16000)
        """
        self.model_path = model_path
        self.sample_rate = sample_rate
        self.model = None
        self.recognizer = None
        
        self._load_model()
    
    def _load_model(self):
        """
        Load the Vosk language model from disk.
        This is called during initialization to prepare the recognizer.
        
        Raises:
            RuntimeError: If model fails to load
        """
        try:
            print(f"[VoskRecognizer] Loading model from: {self.model_path}")
            self.model = Model(self.model_path)
            self.recognizer = KaldiRecognizer(self.model, self.sample_rate)
            self.recognizer.SetWords(True)  # Enable word-level timestamps
            print("[VoskRecognizer] Model loaded successfully")
        except Exception as e:
            raise RuntimeError(f"Failed to load Vosk model from {self.model_path}: {e}")
    
    def process_audio(self, audio_data: bytes):
        """
        Process a chunk of audio data and return recognition results.
        This is the main recognition function called for each audio block.
        
        Args:
            audio_data: Raw audio bytes from the microphone
            
        Returns:
            Dictionary containing:
                - 'text': Recognized text (empty string if no speech detected)
                - 'partial': Boolean indicating if this is a partial or final result
                - 'result': Full JSON result from Vosk with additional metadata
        """
        # Feed audio data to recognizer
        if self.recognizer.AcceptWaveform(audio_data):
            # Final result: end of utterance detected
            result = json.loads(self.recognizer.Result())
            return {
                'text': result.get('text', ''),
                'partial': False,
                'result': result
            }
        else:
            # Partial result: speech in progress
            partial_result = json.loads(self.recognizer.PartialResult())
            return {
                'text': partial_result.get('partial', ''),
                'partial': True,
                'result': partial_result
            }
    
    def get_final_result(self):
        """
        Get the final recognition result after processing is complete.
        Should be called when audio stream ends to get any remaining text.
        
        Returns:
            Dictionary containing the final result from Vosk
        """
        final = json.loads(self.recognizer.FinalResult())
        return {
            'text': final.get('text', ''),
            'partial': False,
            'result': final
        }
    
    def reset(self):
        """
        Reset the recognizer to start fresh with a new audio session.
        Clears any internal state and prepares for new speech input.
        """
        print("[VoskRecognizer] Resetting recognizer")
        self.recognizer = KaldiRecognizer(self.model, self.sample_rate)
        self.recognizer.SetWords(True)


class SpeechToText:
    """
    High-level interface combining audio capture and speech recognition.
    Provides simple methods for real-time speech-to-text conversion.
    """
    
    def __init__(self, model_path: str, sample_rate: int = 16000):
        """
        Initialize the complete speech-to-text system.
        
        Args:
            model_path: Path to the Vosk model directory
            sample_rate: Audio sample rate in Hz (default: 16000)
        """
        self.sample_rate = sample_rate
        
        # Initialize separate components
        self.audio_capture = AudioCapture(sample_rate=sample_rate)
        self.recognizer = VoskRecognizer(model_path=model_path, sample_rate=sample_rate)
    
    def start_listening(self, callback=None, device=None):
        """
        Start real-time speech recognition from microphone.
        Continuously captures and transcribes audio until stopped.
        
        Args:
            callback: Optional function to handle recognition results.
                     Function should accept a dict with 'text', 'partial', and 'result' keys.
            device: Audio input device index (None for default)
        """
        # Reset recognizer for new session
        self.recognizer.reset()
        
        # Start capturing audio
        self.audio_capture.start_stream(device=device)
        
        print("[SpeechToText] Listening... (Press Ctrl+C to stop)")
        
        try:
            # Main processing loop
            while self.audio_capture.is_active():
                # Get audio data from capture queue
                audio_data = self.audio_capture.get_audio_data()
                
                # Process audio through recognizer
                result = self.recognizer.process_audio(audio_data)
                
                # Handle the result
                if result['text']:
                    if callback and not result['partial']:
                        # Use custom callback if provided
                        callback(result)
                    else:
                        # Default: print to console
                        prefix = "[Partial]" if result['partial'] else "[Final]"
                        print(f"{prefix} {result['text']}")
                        
        except KeyboardInterrupt:
            print("\n[SpeechToText] Stopping...")
        finally:
            self.stop_listening()
    
    def stop_listening(self):
        """
        Stop audio capture and get final recognition results.
        """
        self.audio_capture.stop_stream()
        
        # Get any remaining recognized text
        final = self.recognizer.get_final_result()
        if final['text']:
            print(f"[Final] {final['text']}")
