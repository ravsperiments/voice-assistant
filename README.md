# Voice Assistant

Lightweight voice assistant that listens for a configurable wake word, transcribes your command with Vosk, calls a local LLM through Ollama, and speaks the response with Picovoice Orca.

## Prerequisites

- Python 3.11+
- [Picovoice Console](https://console.picovoice.ai/) account to obtain a Picovoice access key
- Porcupine wake word model (built-in or custom `.ppn`)
- Orca TTS model (`models/picovoice/orca_params_en_female.pv`)
- Vosk English model (`models/vosk-model-small-en-us-0.15`)
- Ollama running with the model configured in `config.py`

Install Python dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration

Edit `config.py` to set:

- `PICOVOICE_ACCESS_KEY`: your Picovoice key.
- `OLLAMA_API_URL` / `OLLAMA_MODEL_NAME`: endpoint and model name exposed by Ollama.
- `WAKE_WORD_NAME`: friendly name used for logging (`jarvis` by default).
- `WAKE_WORD_CUSTOM_PATH`: optional path to a custom Porcupine `.ppn` file if you want a wake word that is not built in.

## Running

```bash
python3 main.py
```

Workflow:
1. Assistant waits for the wake word (default “jarvis”).
2. After detection it records one command and transcribes it with Vosk.
3. The transcript is sent to the LLM for a response.
4. Orca converts the response to speech and plays it through the system output.
5. The assistant returns to the idle state, waiting for the wake word again.

## Troubleshooting

- Run from a quiet environment to improve wake word detection and speech recognition.
- If TTS playback is silent, verify audio output device selection and that the Orca model path is correct.
- For custom wake words, ensure the `.ppn` file path is accurate and matches your platform (macOS, Windows, etc.).
