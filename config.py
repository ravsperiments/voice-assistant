# config.py

import os

def _env(key: str, default: str | None = None) -> str | None:
    """Fetch environment variables while allowing empty strings to fall back to defaults."""
    value = os.getenv(key)
    if value is None or value.strip() == "":
        return default
    return value


def _env_bool(key: str, default: bool = False) -> bool:
    """Parse boolean environment variable."""
    value = os.getenv(key)
    if value is None:
        return default
    return value.lower() in ('true', '1', 'yes', 'on')


PICOVOICE_ACCESS_KEY = _env("PICOVOICE_ACCESS_KEY", "rGn8kk49k1Dr5RAnkO0uVSpn+koiCn6s3KZyWXSnUUhPSZh/5HcGkw==") # Replace with your key

OLLAMA_API_URL = _env("OLLAMA_API_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL_NAME = _env("OLLAMA_MODEL_NAME", "granite3.2:2b") # Ensure this matches the name of your pulled Ollama model

# Wake word configuration
WAKE_WORD_NAME = _env("WAKE_WORD_NAME", "jarvis")  # Friendly name used for logging
# Provide the absolute path to your custom Porcupine keyword (.ppn) file if using a non-built-in wake word.
# Example: WAKE_WORD_CUSTOM_PATH = "models/picovoice/hey-buddy_en_mac_v3_0_0.ppn"
WAKE_WORD_CUSTOM_PATH = _env("WAKE_WORD_CUSTOM_PATH", None)

# Conversation Settings (Phase 1)
MAX_HISTORY_TURNS = int(_env("MAX_HISTORY_TURNS", "10"))  # Maximum turns to keep in conversation history (1 turn = user + assistant pair)
AWAITING_TIMEOUT = float(_env("AWAITING_TIMEOUT", "10.0"))  # Seconds to wait for next user turn before ending conversation
MAX_RESPONSE_TOKENS = int(_env("MAX_RESPONSE_TOKENS", "100"))  # Maximum tokens for LLM response (~15-20 seconds of speech)
VAD_ENERGY_THRESHOLD = int(_env("VAD_ENERGY_THRESHOLD", "500"))  # Energy level threshold for voice activity detection

# Conversation Logging
LOGGING_ENABLED = _env_bool('LOGGING_ENABLED', True)  # Enable conversation logging to database
LOGGING_DB_PATH = _env('LOGGING_DB_PATH', 'data/conversations.db')  # Path to SQLite database file
