"""
Test script for the complete call handler pipeline.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pipeline import run_call_handler
from dotenv import load_dotenv

def test_call_handler():
    """Test the complete call handling pipeline."""
    load_dotenv()
    
    print("=" * 50)
    print("Starting Call Handler Test")
    print("=" * 50)
    print("\nSpeak into your microphone to test the pipeline.")
    print("The system will:")
    print("1. Transcribe your speech")
    print("2. Generate a response")
    print("3. Convert response to speech")
    print("4. Play the audio")
    print("\nPress Ctrl+C to stop.\n")
    
    try:
        run_call_handler()
    except KeyboardInterrupt:
        print("\n\nTest stopped by user.")
    except Exception as e:
        print(f"\nError during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_call_handler()