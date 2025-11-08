"""
Test script for the speech-to-text module.
Run this to test real-time speech recognition.
"""

import sys
import os

# Add src to path to import the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from core.speech_to_text import SpeechToText, AudioCapture


def test_real_time_stt():
    """
    Test real-time speech-to-text with microphone input.
    """
    # Path to the downloaded Vosk model
    MODEL_PATH = os.path.join(os.path.dirname(__file__), '../../models', 'vosk-model-en-us-0.22')
    
    print("=" * 60)
    print("Real-Time Speech-to-Text Test")
    print("=" * 60)
    
    # Check if model exists
    if not os.path.exists(MODEL_PATH):
        print(f"❌ Error: Model not found at {MODEL_PATH}")
        print("Please download a Vosk model first.")
        return
    
    try:
        # Initialize the speech-to-text system
        print(f"\n📦 Loading model from: {MODEL_PATH}")
        stt = SpeechToText(model_path=MODEL_PATH, sample_rate=16000)
        
        # Optional: List available audio devices
        print("\n🎤 Available audio devices:")
        AudioCapture.list_devices()
        
        # Custom callback to handle recognized speech
        def on_speech_recognized(result):
            """
            Callback function that handles the recognition results.
            """
            if result['partial']:
                # Partial results (speech in progress)
                print(f"🗣️  [Speaking...] {result['text']}", end='\r')
            else:
                # Final results (end of utterance)
                print(f"\n✅ [Recognized] {result['text']}")
        
        # Start listening
        print("\n" + "=" * 60)
        print("🎙️  START SPEAKING (Press Ctrl+C to stop)")
        print("=" * 60 + "\n")
        
        stt.start_listening(callback=on_speech_recognized)
        
    except KeyboardInterrupt:
        print("\n\n✋ Test stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


def test_components_separately():
    """
    Test audio capture and recognition components separately.
    This is useful for debugging individual components.
    """
    from core.speech_to_text import AudioCapture, VoskRecognizer
    
    MODEL_PATH = os.path.join(os.path.dirname(__file__), 'models', 'vosk-model-small-en-us-0.15')
    
    print("=" * 60)
    print("Testing Components Separately")
    print("=" * 60)
    
    # Initialize components
    audio = AudioCapture(sample_rate=16000)
    recognizer = VoskRecognizer(model_path=MODEL_PATH, sample_rate=16000)
    
    # Start audio capture
    audio.start_stream()
    
    try:
        print("\n🎙️  Speak now...")
        while True:
            # Get audio data
            audio_data = audio.get_audio_data()
            
            # Process with recognizer
            result = recognizer.process_audio(audio_data)
            
            if result['text']:
                prefix = "[Partial]" if result['partial'] else "[Final]"
                print(f"{prefix} {result['text']}")
                
    except KeyboardInterrupt:
        print("\n\nStopping...")
    finally:
        audio.stop_stream()


if __name__ == "__main__":
    # Run the real-time test
    test_real_time_stt()
    
    # Uncomment to test components separately
    # test_components_separately()
