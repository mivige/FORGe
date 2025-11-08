# Voice-to-Voice Call Handler - Implementation Documentation

This document covers the actual implementation of the FORGe voice-to-voice call handler system built in `src/`.

---

## Overview

The FORGe system implements an AI-powered voice call handler for insurance claim intake. It combines speech recognition, natural language understanding, and text-to-speech to create a conversational experience.

### Core Components

The system is built with four main modules in `src/core/`:

1. **Speech-to-Text** (`speech_to_text.py`) - Converts caller's voice to text using Vosk
2. **Natural Language Understanding** (`natural_language_understanding.py`) - Processes text, extracts claim data, generates responses
3. **Text-to-Speech** (`text_to_speech.py`) - Converts responses to voice using ElevenLabs
4. **Pipeline** (`pipeline.py`) - Orchestrates the complete conversation flow

---

## Implementation Details

### 1. Speech-to-Text Module (`speech_to_text.py`)

**Technology:** Vosk (offline speech recognition) + sounddevice (audio capture)

**Architecture:**
- `AudioCapture`: Manages microphone input using sounddevice
- `VoskRecognizer`: Processes audio chunks and returns transcriptions
- `SpeechToText`: High-level interface combining both components

**Key Features:**
- Real-time streaming audio capture
- Separate partial and final recognition results
- Queue-based audio processing
- Callback support for handling transcriptions

**Usage:**
```python
from core.speech_to_text import SpeechToText

stt = SpeechToText(model_path="models/vosk-model-en-us-0.22")

def on_speech(result):
    if not result['partial']:
        print(f"User said: {result['text']}")

stt.start_listening(callback=on_speech)
```

**Why Vosk?**
- Works completely offline (no API costs or internet dependency)
- Fast, real-time processing
- Good accuracy for conversational speech
- Free and open-source

---

### 2. Natural Language Understanding (`natural_language_understanding.py`)

**Technology:** OpenAI GPT-4o-mini with structured JSON outputs

**Architecture:**
- `ConversationState`: Enum tracking conversation progress
- `ConversationalNLU`: Main class handling all NLU tasks in a single API call

**Key Features:**
- **Single API Call Efficiency**: All processing in one request
  - Emergency/panic detection
  - Frustration scoring (0-10 scale)
  - Claim data extraction
  - Response generation
  - State management

- **Token Optimization**: Base system prompt built once at initialization, only dynamic context sent per request

- **Automatic Transfers**:
  - Emergency (injury/panic detected) → immediate transfer
  - High frustration (>7.0) → transfer with apology
  - Technical errors → transfer to agent

**Conversation States:**
```
GREETING → GATHERING_POLICY_INFO → GATHERING_INCIDENT_DETAILS 
→ GATHERING_DAMAGE_INFO → CONFIRMING → COMPLETE
```

**Data Structure (follows text_to_ticket.py schema):**
```python
{
    "policyId": "string",
    "customerName": "string",
    "incidentType": "string",
    "description": "[Frustration Score: X/10] details...",
    "location": "string",
    "estimatedDamage": float,
    "incidentDate": "YYYY-MM-DD"
}
```

**Usage:**
```python
from core.natural_language_understanding import ConversationalNLU

nlu = ConversationalNLU()
result = nlu.process_input("My car was hit yesterday")

print(result['response'])  # AI-generated response
print(result['claim_data'])  # Extracted claim information
print(result['frustration_score'])  # 0-10 score
```

**Why This Approach?**
- Single API call reduces latency and costs (~72% token savings)
- Structured JSON output ensures reliable parsing
- Context window maintains conversation coherence
- Real-time processing suitable for voice conversations

---

### 3. Text-to-Speech Module (`text_to_speech.py`)

**Technology:** ElevenLabs API + pydub for playback

**Implementation:**
```python
def text_to_speech(text_input: str):
    # Stream audio from ElevenLabs
    audio_stream = client.text_to_speech.convert(
        voice_id="2EiwWnXFnvU5JabPnv8n",
        model_id="eleven_multilingual_v2",
        text=text_input
    )
    
    # Convert to AudioSegment
    audio_bytes = b"".join(audio_stream)
    audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format="mp3")
    
    # Add silence to prevent cutoff
    silence = AudioSegment.silent(duration=100)
    audio = silence + audio
    
    # Play and block until finished
    play(audio)
```

**Key Design Decision:**
- Uses `pydub.playback.play()` which **blocks** until audio finishes
- This prevents microphone from picking up assistant's voice (no echo)
- No threading needed - blocking is the desired behavior

**Why ElevenLabs?**
- High-quality, natural-sounding voices
- Low latency streaming
- Multilingual support
- Simple API integration

---

### 4. Pipeline Orchestration (`pipeline.py`)

**Function:** `run_call_handler()`

**Complete Flow:**
```
1. Initialize components (STT, NLU, n8n client)
2. Play greeting (blocking TTS)
3. Start listening loop:
   a. STT captures speech → transcription
   b. NLU processes → response + data extraction
   c. TTS plays response (blocking)
   d. Check for call end conditions:
      - COMPLETE: Submit ticket to n8n, play goodbye, end
      - EMERGENCY_TRANSFER: Play transfer message, end
   e. If continuing, return to (a)
4. Cleanup and exit
```

**Callback Architecture:**
```python
def handle_speech_callback(transcription_result):
    # Only process complete (non-partial) transcriptions
    if transcription_result.get('partial'):
        return
    
    user_input = transcription_result.get('text', '')
    
    # Process through NLU
    nlu_result = nlu.process_input(user_input)
    
    # Play response (blocks until finished)
    text_to_speech(nlu_result['response'])
    
    # Check for call end conditions
    if nlu_result['should_transfer'] or nlu_result['is_complete']:
        stt.stop_listening()
        # Handle ticket submission if complete
```

**Why This Design?**
- Callback architecture allows STT to run continuously
- Blocking TTS prevents feedback loops
- Clean separation of concerns
- Easy to debug and modify

---
