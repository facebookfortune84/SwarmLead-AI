# Voice Model Integration — running Genesis Forge on your trained model

The landing-page voice agent is a **text-in/text-out loop**:

```
browser speech → text  →  Ollama LLM (your model)  →  text  →  ElevenLabs TTS → audio
```

The browser does speech recognition (Web Speech API). The **only thing that
defines the assistant's personality, logic, and voice-to-voice feel is the
model powering the middle box**. That box is pluggable via the voice model
registry (`core/services/voice_model.py`).

## One-knob switch

Set `VOICE_MODEL` to your trained model's Ollama name:

```env
# .env.docker.local
VOICE_MODEL=genesis-voice:latest
```

`voice_agent_service` resolves this on every reply, so a restart of the API is
enough. No code change.

## Option A — host the model on Ollama (recommended)

1. Train / export your model (LoRA adapter, GGUF, or a base + adapter) and
   register it with Ollama:

   ```bash
   ollama create genesis-voice:latest -f ./Modelfile
   ```

   A minimal `Modelfile`:

   ```dockerfile
   FROM llama3.2:3b            # your base
   ADAPTER ./adapters/voice/   # your fine-tuned adapter (if any)
   PARAMETER temperature 0.3
   PARAMETER top_p 0.9
   PARAMETER num_ctx 32768
   SYSTEM "You are the Genesis Forge voice launch assistant. ..."
   ```

2. Point the API container at the Ollama host. Locally:

   ```env
   VOICE_MODEL_BASE_URL=http://host.docker.internal:11434
   ```

   (or reuse `OLLAMA_API_BASE`). Set both to the same URL if the model runs on
   the same Ollama instance.

## Option B — separate model service (HTTP)

If your trained model exposes an OpenAI-style `/v1/chat/completions` or
Ollama `/api/generate` endpoint, run it anywhere and set:

```env
VOICE_MODEL=genesis-voice:latest
VOICE_MODEL_BASE_URL=http://your-model-host:11434
```

Only `/api/generate` (Ollama protocol) is supported today.

## Tuning per model

`VOICE_MODEL_OVERRIDES` tunes generation without touching configs, format
`model=temperature,top_p,max_tokens`, separated by `;`:

```env
VOICE_MODEL_OVERRIDES=genesis-voice:latest=0.2,0.8,160;llama3.2:3b=0.4,0.9,200
```

## Verify it is live

```bash
curl http://localhost:8000/api/voice/models
# { "active_model": "genesis-voice:latest", "source": "voice_model_env", ... }
```

The Autonomy console shows the same status. If `source` reads `"default"`,
`VOICE_MODEL` isn't reaching the container (check `.env.docker.local` and that
you recreated the API container after editing it).

## Voice-to-voice notes

- The assistant speaks via ElevenLabs (`ELEVENLABS_DEFAULT_VOICE_ID`). To make
  the *spoken* output match your trained model's tone, pair the model with a
  matching ElevenLabs voice.
- Barge-in is handled in the browser (`frontend/src/lib/voice-engine.ts`). It
  uses an attack/hold envelope and auto-arms a higher threshold when the mic
  lacks echo cancellation. See the `BargeInDetector` tests for behavior.
- The 25s LLM cap (`VoiceAgentService._llm_timeout_s`) keeps the agent
  responsive on CPU-only Ollama. A fast hosted model never hits the cap; a
  slow local one falls back to scripted replies so the visitor never stares at
  a frozen agent.
