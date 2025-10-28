"""
Unit tests for main.py conversation loop logic.
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock, call
from io import StringIO

# Add parent directory to path to import components
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import config
from components import conversation


class TestConversationFlow:
    """Tests for the conversation flow logic."""

    def test_conversation_module_imported(self):
        """Test that conversation module can be imported and used."""
        assert hasattr(conversation, 'clear_history')
        assert hasattr(conversation, 'add_user_message')
        assert hasattr(conversation, 'add_assistant_message')
        assert hasattr(conversation, 'get_history')
        assert hasattr(conversation, 'is_conversation_ending')

    def test_config_conversation_settings_exist(self):
        """Test that all required conversation config settings exist."""
        assert hasattr(config, 'MAX_HISTORY_TURNS')
        assert hasattr(config, 'AWAITING_TIMEOUT')
        assert hasattr(config, 'MAX_RESPONSE_TOKENS')
        assert hasattr(config, 'VAD_ENERGY_THRESHOLD')

    def test_config_conversation_settings_reasonable(self):
        """Test that conversation settings have reasonable default values."""
        assert config.MAX_HISTORY_TURNS > 0
        assert config.AWAITING_TIMEOUT > 0
        assert config.MAX_RESPONSE_TOKENS > 0
        assert config.VAD_ENERGY_THRESHOLD > 0

    def test_config_values_types(self):
        """Test that config values have correct types."""
        assert isinstance(config.MAX_HISTORY_TURNS, int)
        assert isinstance(config.AWAITING_TIMEOUT, float)
        assert isinstance(config.MAX_RESPONSE_TOKENS, int)
        assert isinstance(config.VAD_ENERGY_THRESHOLD, int)

    @patch('main.speak_text')
    @patch('main.generate_response')
    @patch('main.transcribe_audio')
    @patch('main.has_voice_activity')
    def test_conversation_with_goodbye(self, mock_vad, mock_transcribe, mock_llm, mock_speak):
        """Test conversation flow with goodbye phrase."""
        # Simulate: VAD detects voice, user says goodbye
        mock_vad.return_value = True
        mock_transcribe.return_value = "Goodbye"

        # Import here to avoid circular imports
        from main import run_conversation

        conversation.clear_history()
        run_conversation()

        # Verify flow: greeting, VAD check, transcribe, end
        assert mock_speak.called  # Should speak greeting and farewell
        assert mock_vad.called  # Should check voice activity
        assert mock_transcribe.called  # Should transcribe user input
        # Should not call LLM since goodbye was detected before LLM call

    @patch('main.speak_text')
    @patch('main.has_voice_activity')
    def test_conversation_with_timeout(self, mock_vad, mock_speak):
        """Test conversation ends on timeout (no voice activity)."""
        # Simulate: VAD timeout
        mock_vad.return_value = False

        # Import here to avoid circular imports
        from main import run_conversation

        conversation.clear_history()
        run_conversation()

        # Verify speak was called for greeting and farewell
        assert mock_speak.call_count >= 2  # Greeting + farewell
        # Verify VAD was called with correct timeout
        mock_vad.assert_called_with(
            timeout_seconds=config.AWAITING_TIMEOUT,
            energy_threshold=config.VAD_ENERGY_THRESHOLD
        )

    @patch('main.speak_text')
    @patch('main.generate_response')
    @patch('main.transcribe_audio')
    @patch('main.has_voice_activity')
    def test_multi_turn_conversation(self, mock_vad, mock_transcribe, mock_llm, mock_speak):
        """Test multi-turn conversation flow."""
        # Simulate: 3 turns then goodbye
        mock_vad.return_value = True
        mock_transcribe.side_effect = [
            "What is 2+2?",
            "What's the weather?",
            "Goodbye"
        ]
        mock_llm.return_value = "The answer is 4."

        # Import here to avoid circular imports
        from main import run_conversation

        conversation.clear_history()
        run_conversation()

        # Should have transcribed 3 times
        assert mock_transcribe.call_count == 3
        # Should have checked VAD 3 times
        assert mock_vad.call_count == 3
        # Verify history contains messages
        history = conversation.get_history()
        assert len(history) >= 2  # At least greeting + user message

    @patch('main.speak_text')
    @patch('main.has_voice_activity')
    def test_conversation_clears_history(self, mock_vad, mock_speak):
        """Test that conversation history is cleared at start of conversation."""
        # Add some history before conversation
        conversation.add_user_message("Old message")
        conversation.add_assistant_message("Old response")

        # Simulate: VAD timeout (quick end)
        mock_vad.return_value = False

        # Import here to avoid circular imports
        from main import run_conversation

        run_conversation()

        # History should only have the new greeting, not old messages
        history = conversation.get_history()
        # Check that old messages are not in history
        assert not any("Old message" in str(msg.get('content', '')) for msg in history)
        assert not any("Old response" in str(msg.get('content', '')) for msg in history)

    @patch('main.speak_text')
    @patch('main.generate_response')
    @patch('main.transcribe_audio')
    @patch('main.has_voice_activity')
    def test_conversation_handles_empty_transcription(self, mock_vad, mock_transcribe, mock_llm, mock_speak):
        """Test conversation handles empty transcription gracefully."""
        # Simulate: VAD detects voice but transcription fails
        mock_vad.side_effect = [True, False]  # First turn has voice, second times out
        mock_transcribe.return_value = ""  # Empty transcription

        # Import here to avoid circular imports
        from main import run_conversation

        conversation.clear_history()
        run_conversation()

        # Should still end gracefully
        assert mock_speak.called

    @patch('main.speak_text')
    @patch('main.generate_response')
    @patch('main.transcribe_audio')
    @patch('main.has_voice_activity')
    def test_conversation_handles_llm_error(self, mock_vad, mock_transcribe, mock_llm, mock_speak):
        """Test conversation handles LLM errors gracefully."""
        # Simulate: user says something, LLM returns empty
        mock_vad.side_effect = [True, False]  # First turn has voice, second times out
        mock_transcribe.return_value = "Hello"
        mock_llm.return_value = ""  # LLM returns empty

        # Import here to avoid circular imports
        from main import run_conversation

        conversation.clear_history()
        run_conversation()

        # Should handle error and end gracefully
        assert mock_speak.called
        # Should have spoken error message
        error_messages = [call_args[0][0] for call_args in mock_speak.call_args_list]
        assert any("couldn't generate" in msg.lower() for msg in error_messages)


class TestConfigIntegration:
    """Tests for config integration with conversation."""

    def test_conversation_respects_max_history_turns(self):
        """Test that conversation respects MAX_HISTORY_TURNS setting."""
        conversation.clear_history()

        # Add more messages than MAX_HISTORY_TURNS allows
        for i in range(config.MAX_HISTORY_TURNS * 3):
            conversation.add_user_message(f"User message {i}")
            conversation.add_assistant_message(f"Assistant message {i}")

        history = conversation.get_history()

        # Should only keep last MAX_HISTORY_TURNS * 2 messages
        assert len(history) <= config.MAX_HISTORY_TURNS * 2

    def test_vad_uses_config_threshold(self):
        """Test that VAD function signature accepts energy threshold."""
        # This is a signature test - just verify the parameter exists
        from components.stt import has_voice_activity
        import inspect

        sig = inspect.signature(has_voice_activity)
        assert 'energy_threshold' in sig.parameters
        assert sig.parameters['energy_threshold'].default == 500
