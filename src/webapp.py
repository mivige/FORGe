"""
Web-based demo interface for FORGe.
Reuses pipeline.py logic through a callback system.
"""

from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import threading
from dotenv import load_dotenv

# Import everything from pipeline - we'll reuse the logic
from core.natural_language_understanding import ConversationalNLU
from core.text_to_speech import text_to_speech, is_audio_playing
from core.post_to_n8n import N8NWebhookClient
import os
import time

load_dotenv()

app = Flask(__name__, template_folder='demo/templates')
app.config['SECRET_KEY'] = 'forge-demo-secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# Override the callback mechanism
class WebCallHandler:
    def __init__(self):
        self.nlu = None
        self.n8n_client = None
        self.call_active = False
        self.waiting_for_callback_choice = False
    
    def start_call(self):
        """Start a new call - copied from pipeline.py run_call_handler()"""
        self.call_active = True
        self.waiting_for_callback_choice = False
        
        # Initialize (same as pipeline.py)
        self.nlu = ConversationalNLU()
        
        n8n_webhook_url = os.getenv("N8N_WEBHOOK_URL")
        if n8n_webhook_url:
            self.n8n_client = N8NWebhookClient(webhook_url=n8n_webhook_url)
        
        # Greeting
        greeting = self.nlu.get_greeting()
        print(f"[ASSISTANT] {greeting}")
        
        socketio.emit('assistant_message', {'text': greeting, 'frustration': 0})
        socketio.emit('claim_update', {'data': self.nlu.claim_data})
        
        threading.Thread(target=self._play_and_listen, args=(greeting,), daemon=True).start()
    
    def handle_speech(self, user_text):
        """Handle user speech - FULL implementation from pipeline.py"""
        if not self.call_active or not user_text:
            return
        
        print(f"[USER] {user_text}")
        socketio.emit('user_message', {'text': user_text})
        
        try:
            # Check if waiting for callback choice
            if self.waiting_for_callback_choice:
                user_lower = user_text.lower()
                
                if any(word in user_lower for word in ['agent', 'now', 'speak', 'yes', 'human']):
                    response = "Transferring you to an agent now. Please hold."
                    print(f"[ASSISTANT] {response}")
                    socketio.emit('assistant_message', {'text': response, 'frustration': 0})
                    
                    text_to_speech(response)
                    while is_audio_playing():
                        time.sleep(0.1)
                    
                    socketio.emit('call_ended', {'reason': 'transfer', 'message': 'Transferred to agent'})
                    self.call_active = False
                    self.waiting_for_callback_choice = False
                    return
                    
                elif any(word in user_lower for word in ['call back', 'callback', 'later', 'no']):
                    response = "Got it! We'll call you back within 24 hours. Have a great day!"
                    print(f"[ASSISTANT] {response}")
                    socketio.emit('assistant_message', {'text': response, 'frustration': 0})
                    
                    text_to_speech(response)
                    while is_audio_playing():
                        time.sleep(0.1)
                    
                    socketio.emit('call_ended', {'reason': 'complete', 'message': 'Callback scheduled'})
                    self.call_active = False
                    self.waiting_for_callback_choice = False
                    return
                else:
                    response = "I didn't catch that. Would you like to speak with an agent now, or should we call you back later?"
                    print(f"[ASSISTANT] {response}")
                    socketio.emit('assistant_message', {'text': response, 'frustration': 0})
                    threading.Thread(target=self._play_and_listen, args=(response,), daemon=True).start()
                    return
            
            # Normal NLU processing
            nlu_result = self.nlu.process_input(user_text)
            response = nlu_result['response']
            
            print(f"[ASSISTANT] {response}")
            
            socketio.emit('assistant_message', {
                'text': response,
                'frustration': nlu_result.get('frustration_score', 0)
            })
            socketio.emit('claim_update', {'data': nlu_result['claim_data']})
            
            # Check if should transfer
            if nlu_result.get('should_transfer', False):
                text_to_speech(response)
                while is_audio_playing():
                    time.sleep(0.1)
                
                if self.n8n_client:
                    try:
                        result = self.n8n_client.post_incident_from_dict(nlu_result['claim_data'])
                        print(f"[N8N] Ticket posted: {result}")
                    except Exception as e:
                        print(f"[ERROR] n8n post failed: {e}")
                
                socketio.emit('call_ended', {
                    'reason': 'transfer',
                    'message': nlu_result.get('transfer_reason', 'Emergency transfer')
                })
                self.call_active = False
                return
            
            # Check if complete
            if nlu_result.get('is_complete', False):
                print("[CALL] Claim complete!")
                
                # Post to n8n
                if self.n8n_client:
                    try:
                        result = self.n8n_client.post_incident_from_dict(nlu_result['claim_data'])
                        print(f"[N8N] Ticket posted: {result}")
                        socketio.emit('ticket_posted', {'result': result})
                    except Exception as e:
                        print(f"[ERROR] n8n post failed: {e}")
                
                socketio.emit('call_complete', {'data': nlu_result['claim_data']})
                
                # Set flag and continue listening
                self.waiting_for_callback_choice = True
                threading.Thread(target=self._play_and_listen, args=(response,), daemon=True).start()
                return
            
            # Continue conversation
            threading.Thread(target=self._play_and_listen, args=(response,), daemon=True).start()
            
        except Exception as e:
            print(f'[ERROR] Processing error: {e}')
            import traceback
            traceback.print_exc()
            socketio.emit('error', {'message': str(e)})
    
    def _play_and_listen(self, text):
        text_to_speech(text)
        while is_audio_playing():
            time.sleep(0.1)
        socketio.emit('ready_to_listen')
    
    def end_call(self):
        self.call_active = False
        print('[WEB] Call ended by user')

# Global handler
handler = WebCallHandler()

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print('[WEB] Client connected')

@socketio.on('start_call')
def handle_start_call():
    handler.start_call()

@socketio.on('user_speech')
def handle_user_speech(data):
    text = data.get('text', '').strip()
    if text:
        handler.handle_speech(text)

@socketio.on('end_call')
def handle_end_call():
    handler.end_call()
    emit('call_ended', {'reason': 'user', 'message': 'Call ended'})

if __name__ == '__main__':
    print('=' * 60)
    print('FORGe Web Demo Server')
    print('=' * 60)
    print('\nOpen in browser: http://localhost:5000')
    print('Or from phone on same network: http://<your-ip>:5000\n')
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)