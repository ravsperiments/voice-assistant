# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A lightweight Python voice assistant that uses:
- **Picovoice Porcupine** for wake word detection
- **Vosk** for offline speech-to-text transcription
- **Ollama** for local LLM inference
- **Picovoice Orca** for text-to-speech synthesis

The assistant runs in a continuous loop: wake word → voice command → LLM response → TTS playback.

## Development Setup

Install dependencies:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run the assistant:
```bash
python3 main.py
```

## Configuration

All configuration is in `config.py`. The `_env()` helper function reads from environment variables with fallbacks to hardcoded defaults. Key settings:

- `PICOVOICE_ACCESS_KEY`: Required for wake word and TTS (get from console.picovoice.ai)
- `OLLAMA_API_URL` / `OLLAMA_MODEL_NAME`: Local Ollama endpoint and model
- `WAKE_WORD_NAME`: Friendly name for logging (default: "jarvis")
- `WAKE_WORD_CUSTOM_PATH`: Optional path to custom `.ppn` file for non-built-in wake words

## Required Model Files

- **Orca TTS model**: `models/picovoice/orca_params_en_female.pv`
- **Vosk STT model**: `models/vosk-model-small-en-us-0.15/`
- **Porcupine wake word**: Built-in or custom `.ppn` file

## Architecture

The codebase follows a simple modular pipeline in `main.py`:

```python
wait_for_wake_word()  # components/wake_word.py
transcribe_audio()     # components/stt.py
generate_response()    # components/llm.py
speak_text()           # components/tts.py
```

### Component Details

**`components/wake_word.py`**
- Initializes Porcupine with either built-in keywords (e.g., "jarvis") or custom `.ppn` files
- Blocks until wake word is detected
- Handles PyAudio stream for microphone input at Porcupine's required sample rate

**`components/stt.py`**
- Uses Vosk for offline speech recognition at 16kHz
- Captures audio until a complete utterance is recognized
- Returns transcribed text string

**`components/llm.py`**
- Sends prompt to local Ollama API endpoint
- Uses `stream: False` to get complete response in one call
- Returns LLM response text

**`components/tts.py`**
- Synthesizes text using Picovoice Orca
- Handles various PCM format responses from Orca (bytes, arrays, dicts, tuples)
- Plays audio through PyAudio stream at Orca's sample rate

### Error Handling Pattern

All component modules follow a try/except/finally pattern:
- Catch library-specific exceptions (e.g., `pvporcupine.PorcupineError`, `pvorca.OrcaError`)
- Clean up resources (close streams, terminate PyAudio, delete Picovoice objects) in `finally` blocks
- Print diagnostic information for debugging

## Docker Deployment

The project includes Docker support for Raspberry Pi deployment:

```bash
# One-time setup (installs Docker if needed, creates .env from template)
bash deploy/pi-bootstrap.sh

# Manual build and run
docker compose up -d --build
```

**Docker configuration:**
- `network_mode: host` for Ollama access
- Mounts `/dev/snd` for audio I/O
- Adds container to `audio` group
- `restart: unless-stopped` for auto-start on boot

Environment variables are loaded from `.env` file (see `.env.example` template).

## Platform-Specific Notes

- **macOS/Windows**: Custom Porcupine wake word files (`.ppn`) must match the platform
- **Raspberry Pi**: Use Docker deployment for turnkey setup with audio device access
- **Audio devices**: Components list available devices on startup for debugging

## Testing Individual Components

Each component can be run standalone for testing:
```bash
python -m components.wake_word
python -m components.stt
python -m components.llm
python -m components.tts
```

(Note: Some components like `llm.py` and `tts.py` need modification to run standalone as they require input parameters)
