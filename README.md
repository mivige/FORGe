# FORGe

**AI-Powered Voice Claim Intake System**

Built for the FORGe AI Hackathon in Lisbon 2025, this system demonstrates an intelligent voice interface for insurance claim processing. Using real-time speech recognition, natural language understanding, and text-to-speech, it guides callers through claim submission while detecting emergencies, monitoring frustration, and extracting structured data. The system integrates with n8n automation workflows to automatically create claims and generate tasks in Jira for follow-up.

---

## Running the System

### Prerequisites
```bash
pip install -r requirements.txt
```

**Required environment variables** (`.env`):
```
OPENAI_API_KEY=your_openai_key
ELEVENLABS_API_KEY=your_elevenlabs_key
N8N_WEBHOOK_URL=your_webhook_url  # Optional
```

**Download Vosk Model:**

1. Download from https://alphacephei.com/vosk/models
2. Default model for this project is vosk-model-en-us-0.22 with 1.8G parameters, an accurate generic US English model, to use a different model you MUST change it's path in pipeline.py
3. Extract to models/vosk-model-en-us-0.22/
```

### Run the Pipeline
```bash
cd src
python pipeline.py
```

---
## Typical Conversation Pipeline

![Conversation pipeline graphical overview](docs/pipeline_graphical.png)

Figure: High-level graphical pipeline illustrating call flows.


## System Architecture Diagram

```
┌─────────────────┐
│   Microphone    │
└────────┬────────┘
         │ Audio Stream
         ▼
┌─────────────────────────┐
│  Speech-to-Text (Vosk)  │
│  - AudioCapture         │
│  - VoskRecognizer       │
└────────┬────────────────┘
         │ Transcribed Text
         ▼
┌──────────────────────────────────┐
│  NLU (OpenAI APIs call)          │
│  - Emergency Detection           │
│  - Frustration Scoring           │
│  - Claim Data Extraction         │
│  - Response Generation           │
│  - State Management              │
└────────┬─────────────────────────┘
         │ Response Text + Claim Data
         ▼
┌─────────────────────────────┐
│  Text-to-Speech (ElevenLabs)│
│  - Convert to audio         │
│  - Play (blocks)            │
└─────────┬───────────────────┘
          │ Audio Output
          ▼
┌─────────────────┐
│   Speakers      │
└─────────────────┘

[If COMPLETE] → Decide if Transfer Call or not → Submit to n8n → End Call (for AI)
[If EMERGENCY_TRANSFER] → Transfer Message → End Call (for AI)
```

---

## Design Decisions & Trade-offs

### Why Offline STT (Vosk)?
✅ No API costs or rate limits  
✅ Works without internet  
✅ Real-time processing  
✅ Privacy-friendly (no data sent to cloud)  
❌ Slightly lower accuracy than cloud services  
❌ Requires model download (~2GB for the chosen model)  

### Why Cloud NLU (OpenAI)?
✅ Superior understanding and reasoning  
✅ Easy to customize via prompts  
✅ Structured JSON outputs  
✅ Handles edge cases well  
❌ Requires internet connection  
❌ API costs per request  
❌ Latency from API calls  

### Why Cloud TTS (ElevenLabs)?
✅ Natural, human-like voice quality  
✅ Emotional expression  
✅ Fast streaming  
❌ API costs  
❌ Requires internet  

---

## Performance Metrics

**Typical Latency:**
- STT (Vosk): ~50-200ms per utterance
- NLU (OpenAI): ~500-1500ms per request
- TTS (ElevenLabs): ~300-800ms generation + playback time

**Total Response Time:** ~0.8-2.5 seconds from user finishing speech to assistant starting to speak

**Token Usage (per interaction):** ~200-300 tokens

---

## Future Enhancements

### Potential Improvements
1. **Voice Activity Detection (VAD)** - Better detection of when user stops speaking
2. **Interrupt Handling** - Allow user to interrupt assistant
3. **Multi-language Support** - Auto-detect and respond in caller's language
4. **Emotion Detection** - Detect caller emotions beyond frustration
5. **Call Recording** - Save conversations for quality assurance
6. **Analytics Dashboard** - Track metrics, common issues, resolution rates

### Alternative Technologies to Consider
- **STT:** Whisper (OpenAI), Google Speech-to-Text, AssemblyAI
- **NLU:** Anthropic Claude, Google PaLM, Local LLMs (Llama, Mistral)
- **TTS:** Azure Speech, Google Cloud TTS, Coqui TTS (open-source)

---

## Troubleshooting

### Common Issues

**Microphone not working:**
```python
# List available devices
from core.speech_to_text import AudioCapture
AudioCapture.list_devices()
```

**Echo/Feedback:**
- Ensure TTS is blocking (using `pydub.playback.play()`)
- Check audio output volume
- Use headphones instead of speakers

**API Errors:**
- Verify API keys in `.env`
- Check internet connection
- Monitor API rate limits

**Vosk Model Issues:**
- Ensure model path is correct
- Check model is fully extracted
- Try different model size (small vs large)

---

## References & Resources

### Official Documentation
- [Vosk Documentation](https://alphacephei.com/vosk/)
- [OpenAI API Reference](https://platform.openai.com/docs/)
- [ElevenLabs API Docs](https://elevenlabs.io/docs/)

### Related Documentation
- [`voice_to_voice.md`](docs/voice_to_voice.md) - Theoretical concepts and alternatives
- [`implementation.md`](docs/implementation.md) - Actual implementation of the voice-to-voice call handler system built
- [`Agent-Matching Algorithm`](docs/Agent-Matching%20Algorithm) - How to route to human agents
- [`Text_to_ticket.md`](docs/Text_to_ticket.md) - Claim data schema and extraction
- [`Workflow.md`](docs/Workflow.md) - Overall system workflow
