# components/wake_word.py

import os
import pvporcupine
import pyaudio
import struct
import sys

# Add the parent directory to sys.path for module discovery
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import (
    PICOVOICE_ACCESS_KEY,
    WAKE_WORD_CUSTOM_PATH,
    WAKE_WORD_NAME,
)


def list_audio_devices(pyaudio_instance):
    print("Available audio devices:")
    for i in range(pyaudio_instance.get_device_count()):
        dev = pyaudio_instance.get_device_info_by_index(i)
        print(f"  {i}: {dev['name']} (Input channels: {dev['maxInputChannels']})")

def wait_for_wake_word():
    """
    Listens for the configured wake word and returns when it is detected.
    """
    if PICOVOICE_ACCESS_KEY == "YOUR_PICOVOICE_ACCESS_KEY_HERE":
        print(
            "Warning: PICOVOICE_ACCESS_KEY is not set in config.py. Wake word detection will not work."
        )
        return

    wake_word_label = (WAKE_WORD_NAME or "").strip() or "wake word"

    keyword_paths = None
    if WAKE_WORD_CUSTOM_PATH:
        if not os.path.isfile(WAKE_WORD_CUSTOM_PATH):
            raise FileNotFoundError(
                f"Configured wake word file does not exist: {WAKE_WORD_CUSTOM_PATH}"
            )
        keyword_paths = [WAKE_WORD_CUSTOM_PATH]
    else:
        builtin_key = wake_word_label.lower()
        builtin_path = pvporcupine.KEYWORD_PATHS.get(builtin_key)
        if builtin_path is None:
            raise ValueError(
                f"Wake word '{wake_word_label}' is not available in Porcupine's built-in keywords. "
                "Set WAKE_WORD_CUSTOM_PATH in config.py to the path of your custom .ppn file."
            )
        keyword_paths = [builtin_path]

    porcupine = None
    pa = None
    audio_stream = None

    try:
        porcupine = pvporcupine.create(
            access_key=PICOVOICE_ACCESS_KEY,
            keyword_paths=keyword_paths,
        )

        pa = pyaudio.PyAudio()
        list_audio_devices(pa)

        audio_stream = pa.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length,
        )

        print(f"Listening for wake word: '{wake_word_label}'...")

        while True:
            pcm = audio_stream.read(porcupine.frame_length)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

            keyword_index = porcupine.process(pcm)

            if keyword_index >= 0:
                print(f"Wake word '{wake_word_label}' detected!")
                return
            # else:
            #     print(".", end="", flush=True) # Uncomment for verbose listening indication

    except pvporcupine.PorcupineActivationError as e:
        print(f"Porcupine activation error: {e}")
    except pvporcupine.PorcupineError as e:
        print(f"Porcupine error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if audio_stream is not None:
            audio_stream.close()
        if pa is not None:
            pa.terminate()
        if porcupine is not None:
            porcupine.delete()


if __name__ == "__main__":
    wait_for_wake_word()
