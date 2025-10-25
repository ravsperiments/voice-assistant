
import pvorca
import pyaudio
import struct
import sys
import os

# Add the parent directory to sys.path for module discovery
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import PICOVOICE_ACCESS_KEY

# Path to the Orca model file
ORCA_MODEL_PATH = "models/picovoice/orca_params_en_female.pv"

def list_audio_devices(pyaudio_instance):
    print("Available audio devices:")
    for i in range(pyaudio_instance.get_device_count()):
        dev = pyaudio_instance.get_device_info_by_index(i)
        print(f"  {i}: {dev['name']} (Input channels: {dev['maxInputChannels']}), (Output channels: {dev['maxOutputChannels']})")

def speak_text(text):
    """
    Synthesizes text to speech using Picovoice Orca and plays it.
    """
    orca = None
    pa = None
    audio_stream = None

    try:
        orca = pvorca.create(
            access_key=PICOVOICE_ACCESS_KEY,
            model_path=ORCA_MODEL_PATH
        )

        pa = pyaudio.PyAudio()
        list_audio_devices(pa)
        print(f"Orca sample rate: {orca.sample_rate}, type: {type(orca.sample_rate)}")
        audio_stream = pa.open(
            rate=orca.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=False,
            output=True,
            frames_per_buffer=1024)

        synth_result = orca.synthesize(text)

        # Extract the raw PCM buffer from the synth result regardless of the container type.
        def _resolve_pcm(result):
            if isinstance(result, (bytes, bytearray)):
                return result
            if isinstance(result, dict):
                for key in ("pcm", "audio", "linear_pcm"):
                    if key in result:
                        return result[key]
            if isinstance(result, tuple) and result:
                resolved = _resolve_pcm(result[0])
                if resolved is not None:
                    return resolved
            if hasattr(result, "pcm"):
                return getattr(result, "pcm")
            return result

        pcm = _resolve_pcm(synth_result)
        if pcm is None:
            raise ValueError("Orca synth result did not include PCM audio data")

        # Picovoice returns PCM samples as 16-bit values but they may not be Python ints.
        if isinstance(pcm, (bytes, bytearray)):
            audio_stream.write(pcm)
        else:
            def _flatten(items):
                if isinstance(items, dict):
                    for value in items.values():
                        yield from _flatten(value)
                    return
                for sample in items:
                    if isinstance(sample, (list, tuple)):
                        yield from _flatten(sample)
                    else:
                        yield sample

            # Handle numpy arrays without importing numpy explicitly.
            sequence = pcm.tolist() if hasattr(pcm, "tolist") else pcm
            pcm_ints = []
            for sample in _flatten(sequence):
                if isinstance(sample, (bytes, bytearray)):
                    # Interpret 2-byte chunks as signed shorts.
                    pcm_ints.extend(struct.unpack("<" + "h" * (len(sample) // 2), sample))
                else:
                    try:
                        pcm_ints.append(int(sample))
                    except (TypeError, ValueError):
                        continue

            if pcm_ints:
                audio_bytes = struct.pack("<" + "h" * len(pcm_ints), *pcm_ints)
                audio_stream.write(audio_bytes)

    except pvorca.OrcaError as e:
        print(f"Orca error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if audio_stream is not None:
            audio_stream.close()
        if pa is not None:
            pa.terminate()
        if orca is not None:
            orca.delete()
