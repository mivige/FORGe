"""
Complete pipeline for FORGe call handling system.

This pipeline orchestrates the full flow:
1. Speech-to-Text: Transcribes caller audio
2. NLU: Processes transcription, extracts data, generates response
3. Text-to-Speech: Converts response to audio and plays it

Call ends when ConversationState is COMPLETE or EMERGENCY_TRANSFER.
"""

from core.speech_to_text import SpeechToText
from core.natural_language_understanding import ConversationalNLU, ConversationState
from core.text_to_speech import text_to_speech
from core.text_to_ticket import text_to_incident_ticket
from core.post_to_n8n import N8NWebhookClient
import os
from dotenv import load_dotenv

load_dotenv()


def run_call_handler():
    """
    Complete real-time call handling pipeline.
    
    Flow:
    1. Start call with greeting (TTS)
    2. Listen for speech (STT)
    3. Process input (NLU)
    4. Generate response (NLU)
    5. Speak response (TTS)
    6. Repeat 2-5 until call ends (COMPLETE or EMERGENCY_TRANSFER)
    7. Submit ticket to n8n if complete
    """
    
    print("=" * 60)
    print("FORGe Call Handler - Starting...")
    print("=" * 60)
    
    # Initialize components
    print("\n[SYSTEM] Initializing components...")
    
    # Check for Vosk model
    model_path = "models/vosk-model-en-us-0.22"
    if not os.path.exists(model_path):
        model_path = "models/vosk-model-small-en-us-0.15"
    
    if not os.path.exists(model_path):
        print(f"[ERROR] Vosk model not found. Please download a model to the 'models' directory.")
        return
    
    stt = SpeechToText(model_path=model_path)
    nlu = ConversationalNLU()
    
    # Initialize n8n client if webhook URL is available
    n8n_webhook_url = os.getenv("N8N_WEBHOOK_URL")
    if n8n_webhook_url:
        n8n_client = N8NWebhookClient(webhook_url=n8n_webhook_url)
        print("[SYSTEM] n8n webhook configured")
    else:
        print("[SYSTEM] N8N_WEBHOOK_URL not set - ticket posting disabled")
        n8n_client = None
    
    # Start call with greeting
    print("\n[CALL START]")
    print("-" * 60)
    greeting_text = nlu.get_greeting()
    print(f"[ASSISTANT] {greeting_text}")
    
    try:
        text_to_speech(greeting_text)
    except Exception as e:
        print(f"[ERROR] TTS failed for greeting: {e}")
    
    print("-" * 60)
    print("\n[SYSTEM] Listening for caller... (Press Ctrl+C to stop)\n")
    
    # Track call state
    call_active = True
    
    def handle_speech_callback(transcription_result):
        """
        Callback function for handling transcribed speech.
        
        Args:
            transcription_result: Dict with 'text', 'partial', 'result' keys
        """
        nonlocal call_active
        
        # Only process complete (non-partial) transcriptions
        if transcription_result.get('partial'):
            return
        
        user_input = transcription_result.get('text', '').strip()
        
        if not user_input:
            return
        
        print(f"[CALLER] {user_input}")
        
        try:
            # Process through NLU
            nlu_result = nlu.process_input(user_input)
            
            response_text = nlu_result['response']
            current_state = nlu_result['state']
            
            print(f"[ASSISTANT] {response_text}")
            
            # Debug info
            if nlu_result['frustration_score'] > 0:
                print(f"[DEBUG] Frustration Score: {nlu_result['frustration_score']:.1f}/10")
            if nlu_result['claim_data']:
                filled_fields = [k for k, v in nlu_result['claim_data'].items() if v]
                if filled_fields:
                    print(f"[DEBUG] Collected: {', '.join(filled_fields)}")
            
            # Convert response to speech and play
            try:
                text_to_speech(response_text)
            except Exception as e:
                print(f"[ERROR] TTS failed: {e}")
            
            print("-" * 60 + "\n")
            
            # Check if call should end - EMERGENCY_TRANSFER
            if nlu_result['should_transfer']:
                print(f"[CALL END] Transfer requested: {nlu_result['transfer_reason']}")
                print(f"[SYSTEM] Call would be transferred to agent")
                print(f"[SYSTEM] Collected data: {nlu_result['claim_data']}")
                call_active = False
                stt.stop_listening()
                return
            
            # Check if call should end - COMPLETE
            if nlu_result['is_complete']:
                print("[CALL END] Claim complete!")
                print(f"[SYSTEM] Final claim data: {nlu_result['claim_data']}")
                
                # Create ticket from conversation
                try:
                    # Use the collected claim data directly
                    ticket = nlu_result['claim_data']
                    print(f"\n[TICKET] {ticket}")
                    
                    # Post to n8n if available
                    if n8n_client:
                        try:
                            result = n8n_client.post_incident_from_dict(ticket)
                            print(f"[N8N] Ticket posted successfully: {result}")
                        except Exception as e:
                            print(f"[ERROR] Failed to post ticket to n8n: {e}")
                    
                except Exception as e:
                    print(f"[ERROR] Failed to create ticket: {e}")
                
                # Say goodbye
                goodbye_text = "Your claim has been submitted successfully. Thank you for calling. Have a great day!"
                print(f"\n[ASSISTANT] {goodbye_text}")
                
                try:
                    text_to_speech(goodbye_text)
                except Exception as e:
                    print(f"[ERROR] TTS failed for goodbye: {e}")
                
                call_active = False
                stt.stop_listening()
                return
                
        except Exception as e:
            print(f"[ERROR] Error processing speech: {e}")
            import traceback
            traceback.print_exc()
            
            # Try to say error message
            try:
                error_msg = "I apologize, I'm having technical difficulties. Let me connect you with an agent."
                print(f"[ASSISTANT] {error_msg}")
                text_to_speech(error_msg)
            except:
                pass
            
            call_active = False
            stt.stop_listening()
    
    # Start listening with callback
    try:
        stt.start_listening(callback=handle_speech_callback)
    except KeyboardInterrupt:
        print("\n\n[SYSTEM] Call stopped by user")
    except Exception as e:
        print(f"\n[ERROR] Call handler error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n" + "=" * 60)
        print("FORGe Call Handler - Stopped")
        print("=" * 60 + "\n")


if __name__ == "__main__":
    run_call_handler()