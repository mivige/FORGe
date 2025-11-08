"""
Test script for call handler without audio playback.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.natural_language_understanding import ConversationalNLU
from core.text_to_speech import text_to_speech
from core.text_to_ticket import text_to_incident_ticket
from core.post_to_n8n import N8NWebhookClient
from dotenv import load_dotenv

def test_call_handler_no_audio():
    """Test the call handler without audio I/O."""
    load_dotenv()
    
    print("=" * 50)
    print("Starting Call Handler Test (No Audio)")
    print("=" * 50)
    
    # Initialize components
    nlu = ConversationalNLU()
    n8n_webhook_url = os.getenv("N8N_WEBHOOK_URL")
    
    if n8n_webhook_url:
        n8n_client = N8NWebhookClient(webhook_url=n8n_webhook_url)
    else:
        print("Warning: N8N_WEBHOOK_URL not set. Ticket posting disabled.")
        n8n_client = None
    
    # Print greeting
    greeting = nlu.get_greeting()
    print(f"\n[ASSISTANT] {greeting}\n")
    
    # Simulate conversation with typed input
    print("Type your messages (or 'quit' to exit):\n")
    
    while True:
        try:
            user_input = input("[YOU] ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n[SYSTEM] Ending test.\n")
                break
            
            # Process through NLU
            result = nlu.process_input(user_input)
            
            print(f"[ASSISTANT] {result['response']}")
            
            # Show collected data
            if result['collected_data']:
                print(f"[COLLECTED] {result['collected_data']}")
            
            # Generate TTS (but don't play)
            try:
                audio = text_to_speech(result['response'])
                print(f"[SYSTEM] Generated {len(audio)} bytes of audio")
            except Exception as e:
                print(f"[ERROR] TTS failed: {e}")
            
            print()  # Blank line
            
            # Handle transfer
            if result['should_transfer']:
                print("[SYSTEM] Transfer requested!\n")
                break
            
            # Handle completion
            if result['is_complete']:
                print("[SYSTEM] All information collected! Creating ticket...\n")
                
                # Create ticket
                full_conversation = " ".join([
                    msg['content'] for msg in nlu.conversation_history
                ])
                ticket = text_to_incident_ticket(full_conversation)
                
                print(f"[TICKET] {ticket}\n")
                
                # Post to n8n
                if n8n_client:
                    try:
                        response = n8n_client.post_incident_from_dict(ticket)
                        print(f"[N8N] Ticket posted: {response}\n")
                    except Exception as e:
                        print(f"[ERROR] Failed to post ticket: {e}\n")
                
                print("[ASSISTANT] Your claim has been submitted. Thank you!\n")
                break
                
        except KeyboardInterrupt:
            print("\n\n[SYSTEM] Test stopped by user.\n")
            break
        except Exception as e:
            print(f"\n[ERROR] {e}\n")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_call_handler_no_audio()