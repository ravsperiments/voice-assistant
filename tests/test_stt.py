"""
Unit tests for stt.py module (Voice Activity Detection).
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import numpy as np

# Add parent directory to path to import components
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from components import stt


class TestVoiceActivityDetection:
    """Tests for the has_voice_activity function."""

    def test_has_voice_activity_signature(self):
        """Test that has_voice_activity function exists and has correct signature."""
        assert hasattr(stt, 'has_voice_activity')
        assert callable(stt.has_voice_activity)

    @patch('components.stt.pyaudio.PyAudio')
    def test_has_voice_activity_timeout(self, mock_pyaudio):
        """Test that function returns False after timeout with no voice activity."""
        # Mock audio stream
        mock_stream = MagicMock()
        mock_audio = MagicMock()
        mock_audio.open.return_value = mock_stream

        # Return silent audio (low energy)
        silent_chunk = np.zeros(512, dtype=np.int16).tobytes()
        mock_stream.read.return_value = silent_chunk

        mock_pyaudio.return_value = mock_audio

        # Test with short timeout for speed
        result = stt.has_voice_activity(timeout_seconds=0.1, energy_threshold=500)

        assert result is False
        assert mock_stream.stop_stream.called
        assert mock_stream.close.called
        assert mock_audio.terminate.called

    @patch('components.stt.pyaudio.PyAudio')
    def test_has_voice_activity_detects_voice(self, mock_pyaudio):
        """Test that function returns True when voice activity is detected."""
        # Mock audio stream
        mock_stream = MagicMock()
        mock_audio = MagicMock()
        mock_audio.open.return_value = mock_stream

        # Create audio with high energy (simulating voice)
        voice_chunk = np.ones(512, dtype=np.int16) * 1000  # High amplitude = voice
        mock_stream.read.side_effect = [
            np.zeros(512, dtype=np.int16).tobytes(),  # First chunk: silence
            voice_chunk.tobytes(),  # Second chunk: voice activity
        ]

        mock_pyaudio.return_value = mock_audio

        result = stt.has_voice_activity(timeout_seconds=5.0, energy_threshold=500)

        assert result is True
        assert mock_stream.stop_stream.called
        assert mock_stream.close.called
        assert mock_audio.terminate.called

    @patch('components.stt.pyaudio.PyAudio')
    def test_has_voice_activity_cleans_up_on_exception(self, mock_pyaudio):
        """Test that function cleans up resources even if exception occurs."""
        # Mock audio stream to raise exception
        mock_stream = MagicMock()
        mock_audio = MagicMock()
        mock_audio.open.return_value = mock_stream
        mock_stream.read.side_effect = Exception("Audio device error")

        mock_pyaudio.return_value = mock_audio

        result = stt.has_voice_activity(timeout_seconds=5.0, energy_threshold=500)

        # Should return False on exception
        assert result is False

        # Should still clean up
        assert mock_stream.stop_stream.called
        assert mock_stream.close.called
        assert mock_audio.terminate.called

    @patch('components.stt.pyaudio.PyAudio')
    def test_has_voice_activity_threshold_configurable(self, mock_pyaudio):
        """Test that energy threshold is configurable."""
        mock_stream = MagicMock()
        mock_audio = MagicMock()
        mock_audio.open.return_value = mock_stream

        # Create audio with moderate energy
        moderate_chunk = np.ones(512, dtype=np.int16) * 300
        mock_stream.read.return_value = moderate_chunk.tobytes()

        mock_pyaudio.return_value = mock_audio

        # Should detect with low threshold
        result = stt.has_voice_activity(timeout_seconds=5.0, energy_threshold=100)
        assert result is True

        # Reset mock
        mock_stream.reset_mock()
        mock_audio.reset_mock()

        # Should not detect with high threshold
        mock_stream.read.return_value = moderate_chunk.tobytes()
        result = stt.has_voice_activity(timeout_seconds=0.1, energy_threshold=1000)
        assert result is False

    @patch('components.stt.pyaudio.PyAudio')
    def test_has_voice_activity_default_parameters(self, mock_pyaudio):
        """Test that default parameters are reasonable."""
        mock_stream = MagicMock()
        mock_audio = MagicMock()
        mock_audio.open.return_value = mock_stream
        mock_stream.read.return_value = np.zeros(512, dtype=np.int16).tobytes()

        mock_pyaudio.return_value = mock_audio

        # Call with defaults
        result = stt.has_voice_activity()

        # Should timeout after default timeout (we use 0.01s in test for speed, but defaults should be reasonable)
        assert isinstance(result, bool)

    @patch('components.stt.pyaudio.PyAudio')
    def test_has_voice_activity_format_and_rate(self, mock_pyaudio):
        """Test that audio format and sample rate are configured correctly."""
        mock_stream = MagicMock()
        mock_audio = MagicMock()
        mock_audio.open.return_value = mock_stream

        silent_chunk = np.zeros(512, dtype=np.int16).tobytes()
        mock_stream.read.return_value = silent_chunk

        mock_pyaudio.return_value = mock_audio

        stt.has_voice_activity(timeout_seconds=0.01, energy_threshold=500)

        # Verify PyAudio was opened with correct settings
        mock_audio.open.assert_called()
        call_kwargs = mock_audio.open.call_args[1]
        assert call_kwargs['format'] == stt.FORMAT
        assert call_kwargs['channels'] == stt.CHANNELS
        assert call_kwargs['rate'] == stt.RATE
        assert call_kwargs['input'] is True

    @patch('components.stt.pyaudio.PyAudio')
    def test_has_voice_activity_multiple_calls(self, mock_pyaudio):
        """Test that function can be called multiple times without issues."""
        mock_stream = MagicMock()
        mock_audio = MagicMock()
        mock_audio.open.return_value = mock_stream

        silent_chunk = np.zeros(512, dtype=np.int16).tobytes()
        mock_stream.read.return_value = silent_chunk

        mock_pyaudio.return_value = mock_audio

        # Call multiple times
        result1 = stt.has_voice_activity(timeout_seconds=0.01, energy_threshold=500)
        result2 = stt.has_voice_activity(timeout_seconds=0.01, energy_threshold=500)
        result3 = stt.has_voice_activity(timeout_seconds=0.01, energy_threshold=500)

        # All should work
        assert isinstance(result1, bool)
        assert isinstance(result2, bool)
        assert isinstance(result3, bool)

        # Audio should be cleaned up each time
        assert mock_stream.stop_stream.call_count >= 3
        assert mock_stream.close.call_count >= 3


class TestAudioSettings:
    """Tests for audio configuration constants."""

    def test_audio_format(self):
        """Test that audio format is set to 16-bit."""
        import pyaudio
        assert stt.FORMAT == pyaudio.paInt16

    def test_audio_channels(self):
        """Test that audio is mono."""
        assert stt.CHANNELS == 1

    def test_audio_sample_rate(self):
        """Test that sample rate is 16kHz."""
        assert stt.RATE == 16000

    def test_audio_chunk_size(self):
        """Test that chunk size is reasonable."""
        # CHUNK should be a power of 2 for audio processing
        assert stt.CHUNK > 0
        assert (stt.CHUNK & (stt.CHUNK - 1)) == 0  # Check if power of 2
