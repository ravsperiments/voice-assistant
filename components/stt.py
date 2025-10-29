
import json
import pyaudio
import numpy as np
import time
import logging
from vosk import Model, KaldiRecognizer

# Configure logging
logger = logging.getLogger(__name__)

# Path to your Vosk model
MODEL_PATH = "models/vosk-model-small-en-us-0.15"

# Audio settings
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 512  # Reduced chunk size for faster VAD response

def transcribe_audio():
    """
    Captures audio from the microphone and transcribes it to text using Vosk.

    Returns:
        str: Transcribed text from the audio input.

    Raises:
        Exception: If audio capture or transcription fails.
    """
    model = None
    recognizer = None
    audio = None
    stream = None

    try:
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
            # Use exception_on_overflow=False to drop frames instead of crashing
            # This prevents OSError: [Errno -9981] Input overflowed
            data = stream.read(CHUNK, exception_on_overflow=False)

            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "")
                if text:
                    logger.info(f"Recognized: {text}")
                    return text

    except OSError as e:
        logger.error(f"Audio input error: {e}")
        raise
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        raise
    finally:
        # Clean up resources in reverse order of creation
        if stream is not None:
            try:
                stream.stop_stream()
                stream.close()
            except Exception as e:
                logger.warning(f"Error closing audio stream: {e}")
        if audio is not None:
            try:
                audio.terminate()
            except Exception as e:
                logger.warning(f"Error terminating PyAudio: {e}")


def has_voice_activity(timeout_seconds: float = 10.0, energy_threshold: int = 500) -> bool:
    """
    Detect voice activity using energy-based VAD.

    Listens for audio activity and returns True if voice is detected within
    the timeout period, False if timeout expires without detecting voice.

    Args:
        timeout_seconds: Maximum time to wait for voice activity (default: 10.0s)
        energy_threshold: Energy level threshold for voice detection (default: 500)

    Returns:
        True if voice activity detected, False if timeout expires without voice
    """
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT,
                       channels=CHANNELS,
                       rate=RATE,
                       input=True,
                       frames_per_buffer=CHUNK)

    try:
        logger.debug(f"Waiting for voice activity (timeout: {timeout_seconds}s, threshold: {energy_threshold})")
        start_time = time.time()

        while True:
            # Check timeout
            elapsed = time.time() - start_time
            if elapsed >= timeout_seconds:
                logger.debug(f"Voice activity timeout after {elapsed:.1f}s")
                return False

            # Read audio chunk with overflow protection
            data = stream.read(CHUNK, exception_on_overflow=False)

            # Convert bytes to numpy array
            audio_array = np.frombuffer(data, dtype=np.int16)

            # Calculate RMS energy
            energy = np.abs(audio_array).mean()

            logger.debug(f"Energy level: {energy:.1f} (threshold: {energy_threshold})")

            # Check if energy exceeds threshold
            if energy > energy_threshold:
                logger.info(f"Voice activity detected (energy: {energy:.1f})")
                return True

    except Exception as e:
        logger.error(f"Error in voice activity detection: {e}")
        return False

    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()
