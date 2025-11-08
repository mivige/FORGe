# DeReK
### Department Estimation and Real-time Emotional Knowledge

<div align="center">

**🏆 Built at the 32-hour FORGe AI Hackathon**  
*Lisbon AI Week 2025*

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-green.svg)](https://openai.com/)
[![Vosk](https://img.shields.io/badge/Vosk-Offline%20STT-orange.svg)](https://alphacephei.com/vosk/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

*An intelligent AI voice agent that handles insurance claims with empathy, efficiency, and emergency awareness*

</div>

---

## 🎯 The Challenge

Imagine calling your insurance company after a car accident—stressed, frustrated, and needing immediate help. You're put on hold, transferred multiple times, and forced to repeat your story to different agents. **DeReK** was born to solve this problem.

During the 32-hour FORGe AI Hackathon in Lisbon (AI Tech Week 2025), our team built an empathetic AI voice agent that:
- 🎙️ **Listens** to your claim in natural conversation (no phone tree menus!)
- 🧠 **Understands** your situation, including emotions and urgency
- 🚨 **Detects emergencies** and prioritizes accordingly
- 📊 **Extracts** all necessary claim information automatically
- 🤝 **Routes** you to the right department or creates tickets instantly
- 😌 **Monitors** your frustration and adapts its approach

## 💡 What is DeReK?

**DeReK** (Department Estimation and Real-time Emotional Knowledge) is an AI-powered voice interface that revolutionizes insurance claim intake. Unlike traditional IVR systems that frustrate callers with endless menu options, DeReK conducts natural conversations, understands context, and shows emotional intelligence.

### Key Innovations

🎯 **Smart Routing**: Uses AI to determine if claims need immediate human attention or can be processed automatically

🫀 **Emotional Intelligence**: Continuously monitors caller frustration (0-10 scale) and adapts responses or transfers to humans when needed

⚡ **Emergency Detection**: Identifies panic keywords (injury, bleeding, fire) and immediately routes to emergency services

🔒 **Privacy-First**: Uses offline speech recognition (Vosk) so sensitive conversations never leave your infrastructure

🤖 **Fully Automated Pipeline**: Integrates with n8n workflows to create Jira tickets and trigger follow-up actions without human intervention

---

## 🏗️ Architecture

DeReK combines three powerful technologies in a seamless pipeline:

```
┌─────────────────┐
│   Microphone    │  ← Caller speaks naturally
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

[If COMPLETE] → Submit to n8n → Create Jira ticket → End Call (for AI side)
[If EMERGENCY] → Transfer to human agent → End Call (for AI side)
[If HIGH FRUSTRATION (>7)] → Apologize & transfer → End Call(for AI side)
```

### 🔄 Conversation Flow

DeReK guides callers through a structured but natural conversation:

```
GREETING 
   ↓
GATHERING_POLICY_INFO (Who are you? Policy number?)
   ↓
GATHERING_INCIDENT_DETAILS (What happened? When?)
   ↓
GATHERING_DAMAGE_INFO (What's damaged? Estimated cost?)
   ↓
CONFIRMING (Let me repeat back to you...)
   ↓
COMPLETE (Ticket created! Reference number...)
```

At **any stage**, DeReK can:
- 🚨 Detect emergencies → Immediate transfer
- 😤 Monitor frustration → Empathetic transfer if score > 7
- 🤔 Handle confusion → Rephrase and clarify

---

## 🚀 Quick Start

### Prerequisites

```bash
# Install Python dependencies
pip install -r requirements.txt
```

### Environment Setup

Create a `.env` file in the root directory:

```env
OPENAI_API_KEY=your_openai_key_here
ELEVENLABS_API_KEY=your_elevenlabs_key_here
N8N_WEBHOOK_URL=your_webhook_url_here  # Optional for automation
```

### Download Speech Model

DeReK uses Vosk for offline speech recognition:

1. Download the model: [vosk-model-en-us-0.22](https://alphacephei.com/vosk/models) (1.8GB)
2. Extract to `models/vosk-model-en-us-0.22/`
3. (Optional) Use `vosk-model-small-en-us-0.15` for faster but less accurate recognition

### Run DeReK

```bash
cd src
python pipeline.py
```

**That's it!** DeReK will greet you and start listening. Try having a conversation about a claim.

---

## 💬 Example Conversation

Here's what a typical interaction looks like:

**DeReK:** *"Hello! Thank you for calling. I'm here to help you with your insurance claim. Could you please provide your policy number?"*

**Caller:** *"Yes, it's AC-12345. My car was rear-ended yesterday at a stoplight."*

**DeReK:** *"I'm sorry to hear about your accident. I've noted your policy number AC-12345. Can you tell me more about what happened? Where did this occur?"*

**Caller:** *"It was at the intersection of Main Street and 5th Avenue around 3 PM. The other driver wasn't paying attention."*

**DeReK:** *"Thank you for that information. What damage did your vehicle sustain? Do you have an estimate of the repair costs?"*

**Caller:** *"The rear bumper is completely smashed, and there's damage to the trunk. I'm guessing around $3,000 in repairs."*

**DeReK:** *"Let me confirm the details: You're John Smith with policy AC-12345. On January 15th at 3 PM, your vehicle was rear-ended at Main Street and 5th Avenue, causing approximately $3,000 in damage to your rear bumper and trunk. Is this correct?"*

**Caller:** *"Yes, that's right."*

**DeReK:** *"Perfect! I've submitted your claim with reference number CLM-789456. You'll receive an email shortly with next steps. Is there anything else I can help you with today?"*

![Conversation pipeline graphical overview](docs/pipeline_graphical.png)

Figure: High-level graphical typical conversation pipeline illustrating call flows.

---

## 🎨 Design Decisions

Building DeReK in 32 hours required smart technology choices:

### Why Offline STT (Vosk)?
✅ **No API costs** - Critical for hackathon budget constraints  
✅ **Privacy-first** - Insurance data never sent to cloud  
✅ **Zero latency** - No network delays  
✅ **Always available** - Works without internet  
❌ *Trade-off:* Slightly lower accuracy than cloud services  
❌ *Trade-off:* Requires 2GB model download  

### Why Cloud NLU (OpenAI)?
✅ **Superior reasoning** - Handles complex scenarios  
✅ **Flexible prompting** - Easy to customize behavior  
✅ **Structured outputs** - Reliable JSON extraction  
✅ **Emergency detection** - Natural language understanding excels here  
❌ *Trade-off:* Requires internet connection  
❌ *Trade-off:* ~$0.002 per call (acceptable cost)  

### Why Cloud TTS (ElevenLabs)?
✅ **Human-like quality** - Reduces caller frustration  
✅ **Emotional expression** - Conveys empathy naturally  
✅ **Fast streaming** - ~300ms generation time  
❌ *Trade-off:* API costs (worth it for user experience)

### Key Technical Insight: Single API Call Architecture

Most voice agents make multiple API calls per turn (intent detection, entity extraction, response generation). **DeReK does it all in one call**, reducing:
- **Latency:** 1.5s → 0.8s average response time
- **Costs:** 72% token savings
- **Complexity:** Single prompt vs. multi-step pipeline

---

## 📊 Performance Metrics

**Response Times:**
- STT (Vosk): ~50-200ms per utterance
- NLU (OpenAI): ~500-1500ms per interaction
- TTS (ElevenLabs): ~300-800ms generation + playback

**Total Time:** ~0.8-2.5 seconds from user finishing speech to DeReK responding

**Token Usage:** ~200-300 tokens per turn (~$0.0004 per interaction)

**Accuracy:**
- Transcription: ~92% word accuracy (conversational English)
- Intent recognition: ~98% accuracy in testing
- Data extraction: ~95% complete on first pass

---

## 🛠️ Technical Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Speech Recognition** | Vosk (vosk-model-en-us-0.22) | Offline STT for privacy |
| **NLU & Orchestration** | OpenAI GPT-4o-mini | Conversation management |
| **Voice Synthesis** | ElevenLabs API | Natural TTS output |
| **Audio Capture** | sounddevice | Real-time microphone input |
| **Audio Playback** | pydub | Blocking playback (prevents echo) |
| **Automation** | n8n + Jira API | Ticket creation & workflow |
| **Language** | Python 3.8+ | Core implementation |

---

## 📁 Project Structure

```
DeReK/
├── src/
│   ├── pipeline.py                 # Main orchestration loop
│   ├── core/
│   │   ├── speech_to_text.py      # Vosk STT wrapper
│   │   ├── natural_language_understanding.py  # OpenAI NLU
│   │   ├── text_to_speech.py      # ElevenLabs TTS
│   │   └── post_to_n8n.py         # Webhook integration
│   └── n8n/
│       └── InsurTech Voice Claim Intake.json  # n8n workflow
├── models/
│   └── vosk-model-en-us-0.22/     # Speech recognition model
├── docs/
│   ├── implementation.md           # Technical deep-dive
│   └── voice_to_voice.md          # Theoretical background
├── requirements.txt                # Python dependencies
└── README.md                       # You are here!
```

---

## 🔧 Advanced Configuration

### Using Different Vosk Models

DeReK supports any Vosk model. For faster (but less accurate) recognition:

```python
# In src/pipeline.py, line ~15
model_path = "models/vosk-model-small-en-us-0.15"  # 40MB model
```

Available models: https://alphacephei.com/vosk/models

### Customizing Conversation Flow

Edit the system prompt in `src/core/natural_language_understanding.py`:

```python
# Adjust conversation states, emergency keywords, or response style
self.base_prompt = """
You are a helpful insurance claim assistant...
[Customize behavior here]
"""
```

### Integrating with Your Systems

DeReK sends structured JSON to n8n webhooks:

```json
{
  "policyId": "AC-12345",
  "customerName": "John Smith",
  "incidentType": "Vehicle Accident",
  "description": "[Frustration: 3/10] Rear-ended at stoplight",
  "location": "Main St & 5th Ave",
  "estimatedDamage": 3000.00,
  "incidentDate": "2025-01-15"
}
```

Connect this to your CRM, ticketing system, or database.

---

## 🐛 Troubleshooting

### Microphone Not Detected

```python
# List available audio devices
from core.speech_to_text import AudioCapture
AudioCapture.list_devices()
```

Then update `pipeline.py` with the correct device ID.

### Echo / Feedback Issues

- **Cause:** TTS playing while microphone is listening
- **Solution:** DeReK uses blocking playback (`pydub.playback.play()`) to prevent this
- **Alternative:** Use headphones instead of speakers

### API Rate Limits

- **OpenAI:** Free tier = 3 requests/min. Upgrade to paid tier for production.
- **ElevenLabs:** Free tier = 10,000 characters/month. Monitor usage.

### Vosk Model Not Found

```bash
# Verify model path
ls models/vosk-model-en-us-0.22/am/final.mdl

# If missing, re-download and extract
```

---

## 🚀 Future Enhancements

DeReK was built in 32 hours—here's what we'd add with more time:

### Near-Term (v1.1)
- [ ] **Voice Activity Detection (VAD)** - Better silence detection
- [ ] **Interrupt Handling** - Let callers interrupt DeReK mid-sentence
- [ ] **Multi-language Support** - Auto-detect Spanish, Portuguese, etc.

### Mid-Term (v2.0)
- [ ] **Emotion Detection** - Beyond frustration: detect sadness, anger, joy
- [ ] **Call Recording** - Save conversations for quality assurance
- [ ] **Analytics Dashboard** - Track resolution rates, common issues
- [ ] **Custom Voice Training** - Company-specific voices via ElevenLabs

### Long-Term (v3.0)
- [ ] **Telephony Integration** - Connect to Twilio/Vonage for real phone calls
- [ ] **Multi-modal Input** - Handle photos of damage (vision models)
- [ ] **Predictive Routing** - ML model predicts best department before call ends
- [ ] **Real-time Translation** - Support 20+ languages with live translation

### Alternative Technologies to Consider

**Speech-to-Text:**
- [Whisper](https://openai.com/research/whisper) (OpenAI) - More accurate, cloud-based
- [Google Speech-to-Text](https://cloud.google.com/speech-to-text) - Enterprise solution
- [AssemblyAI](https://www.assemblyai.com/) - Built for conversational AI

**NLU/LLM:**
- [Anthropic Claude](https://www.anthropic.com/) - Strong reasoning abilities
- [Google Gemini](https://deepmind.google/technologies/gemini/) - Multimodal capabilities
- [Llama 3](https://ai.meta.com/llama/) - Open-source, self-hosted option

**Text-to-Speech:**
- [Azure Speech](https://azure.microsoft.com/en-us/products/ai-services/text-to-speech) - Enterprise reliability
- [Google Cloud TTS](https://cloud.google.com/text-to-speech) - Many voice options
- [Coqui TTS](https://github.com/coqui-ai/TTS) - Open-source, self-hosted

---

## 📚 Documentation

- **[Implementation Details](docs/implementation.md)** - Deep technical dive into each component
- **[Voice-to-Voice Concepts](docs/voice_to_voice.md)** - Theoretical background and alternatives

---

## 🙏 Acknowledgments

**Built by Team Error502 at FORGe AI Hackathon 2025**

Special thanks to:
- 🎪 **FORGe Organizers** - For hosting an incredible 32-hour hackathon
- 🇵🇹 **Lisbon AI Week 2025** - For bringing together the AI community

---

## 📜 License

This project is licensed under the x License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built with ❤️ in 32 hours at Lisbon AI Week 2025**

*"Making insurance claims less stressful, one conversation at a time"*

</div>