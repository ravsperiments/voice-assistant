# config.py

PICOVOICE_ACCESS_KEY = "rGn8kk49k1Dr5RAnkO0uVSpn+koiCn6s3KZyWXSnUUhPSZh/5HcGkw==" # Replace with your key

OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL_NAME = "granite3.2:2b" # Ensure this matches the name of your pulled Ollama model

# Wake word configuration
WAKE_WORD_NAME = "jarvis"  # Friendly name used for logging
# Provide the absolute path to your custom Porcupine keyword (.ppn) file if using a non-built-in wake word.
# Example: WAKE_WORD_CUSTOM_PATH = "models/picovoice/hey-buddy_en_mac_v3_0_0.ppn"
WAKE_WORD_CUSTOM_PATH = None
