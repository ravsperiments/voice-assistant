
import json
import pyaudio
from vosk import Model, KaldiRecognizer

# Path to your Vosk model
MODEL_PATH = "models/vosk-model-small-en-us-0.15"

# Audio settings
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 8192

def transcribe_audio():
    """
    Captures audio from the microphone and transcribes it to text using Vosk.
    """
    model = Model(MODEL_PATH)
    recognizer = KaldiRecognizer(model, RATE)

    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

    print("Listening for command...")

    while True:
        data = stream.read(CHUNK)
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text = result.get("text", "")
            if text:
                print(f"Recognized: {text}")
                stream.stop_stream()
                stream.close()
                audio.terminate()
                return text
