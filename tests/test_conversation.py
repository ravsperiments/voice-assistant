"""
Unit tests for conversation.py module.
"""

import pytest
import sys
import os

# Add parent directory to path to import components
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from components import conversation


@pytest.fixture(autouse=True)
def reset_conversation():
    """Reset conversation history before each test."""
    conversation.clear_history()
    yield
    conversation.clear_history()


def test_add_user_message():
    """Test adding a user message to history."""
    conversation.add_user_message("Hello")
    history = conversation.get_history()

    assert len(history) == 1
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "Hello"


def test_add_assistant_message():
    """Test adding an assistant message to history."""
    conversation.add_assistant_message("Hi there!")
    history = conversation.get_history()

    assert len(history) == 1
    assert history[0]["role"] == "assistant"
    assert history[0]["content"] == "Hi there!"


def test_clear_history():
    """Test clearing conversation history."""
    conversation.add_user_message("Hello")
    conversation.add_assistant_message("Hi")

    conversation.clear_history()
    history = conversation.get_history()

    assert len(history) == 0


def test_get_history_returns_copy():
    """Test that get_history returns a copy, not the original list."""
    conversation.add_user_message("Hello")
    history1 = conversation.get_history()
    history2 = conversation.get_history()

    assert history1 is not history2
    assert history1 == history2


def test_prune_history_basic():
    """Test that history is pruned to MAX_HISTORY_TURNS."""
    # Add 25 messages (more than 2 * MAX_HISTORY_TURNS = 20)
    for i in range(15):
        conversation.add_user_message(f"User message {i}")
        conversation.add_assistant_message(f"Assistant message {i}")

    history = conversation.get_history()

    # Should only keep last 20 messages (10 turns)
    assert len(history) == 20

    # First message should be "User message 5" (messages 0-4 pruned)
    assert history[0]["content"] == "User message 5"
    assert history[-1]["content"] == "Assistant message 14"


def test_prune_history_preserves_order():
    """Test that pruning preserves message order."""
    for i in range(12):
        conversation.add_user_message(f"User {i}")
        conversation.add_assistant_message(f"Assistant {i}")

    history = conversation.get_history()

    # Verify order is preserved
    for i in range(len(history) - 1):
        if history[i]["role"] == "user":
            current_num = int(history[i]["content"].split()[-1])
            next_num = int(history[i + 1]["content"].split()[-1])
            assert next_num == current_num


def test_is_conversation_ending_empty():
    """Test ending detection with empty history."""
    assert conversation.is_conversation_ending() is False


def test_is_conversation_ending_goodbye():
    """Test ending detection with 'goodbye' phrase."""
    conversation.add_user_message("Thanks, goodbye!")
    assert conversation.is_conversation_ending() is True


def test_is_conversation_ending_bye():
    """Test ending detection with 'bye' phrase."""
    conversation.add_user_message("Okay bye")
    assert conversation.is_conversation_ending() is True


def test_is_conversation_ending_see_you():
    """Test ending detection with 'see you' phrase."""
    conversation.add_user_message("Alright, see you later")
    assert conversation.is_conversation_ending() is True


def test_is_conversation_ending_thats_all():
    """Test ending detection with 'that's all' phrase."""
    conversation.add_user_message("That's all for now")
    assert conversation.is_conversation_ending() is True


def test_is_conversation_ending_stop():
    """Test ending detection with 'stop' phrase."""
    conversation.add_user_message("Please stop")
    assert conversation.is_conversation_ending() is True


def test_is_conversation_ending_quit():
    """Test ending detection with 'quit' phrase."""
    conversation.add_user_message("I want to quit")
    assert conversation.is_conversation_ending() is True


def test_is_conversation_ending_case_insensitive():
    """Test ending detection is case insensitive."""
    conversation.add_user_message("GOODBYE")
    assert conversation.is_conversation_ending() is True


def test_is_conversation_ending_normal_message():
    """Test ending detection returns False for normal message."""
    conversation.add_user_message("What's the weather today?")
    assert conversation.is_conversation_ending() is False


def test_format_for_llm_ollama():
    """Test formatting for Ollama provider."""
    conversation.add_user_message("Hello")
    conversation.add_assistant_message("Hi there!")
    conversation.add_user_message("How are you?")

    prompt = conversation.format_for_llm("ollama")

    assert isinstance(prompt, str)
    assert "You are a helpful voice assistant" in prompt
    assert "User: Hello" in prompt
    assert "Assistant: Hi there!" in prompt
    assert "User: How are you?" in prompt
    assert prompt.endswith("Assistant:")


def test_format_for_llm_openai():
    """Test formatting for OpenAI provider."""
    conversation.add_user_message("Hello")
    conversation.add_assistant_message("Hi there!")

    messages = conversation.format_for_llm("openai")

    assert isinstance(messages, list)
    assert len(messages) == 3  # system + 2 messages
    assert messages[0]["role"] == "system"
    assert "helpful voice assistant" in messages[0]["content"]
    assert messages[1]["role"] == "user"
    assert messages[1]["content"] == "Hello"
    assert messages[2]["role"] == "assistant"
    assert messages[2]["content"] == "Hi there!"


def test_format_for_llm_anthropic():
    """Test formatting for Anthropic provider."""
    conversation.add_user_message("Hello")
    conversation.add_assistant_message("Hi there!")

    messages = conversation.format_for_llm("anthropic")

    assert isinstance(messages, list)
    assert len(messages) == 3  # system + 2 messages
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    assert messages[2]["role"] == "assistant"


def test_format_for_llm_unknown_provider():
    """Test formatting raises error for unknown provider."""
    conversation.add_user_message("Hello")

    with pytest.raises(ValueError, match="Unknown provider"):
        conversation.format_for_llm("unknown_provider")


def test_format_for_llm_empty_history():
    """Test formatting with empty history."""
    prompt = conversation.format_for_llm("ollama")

    assert isinstance(prompt, str)
    assert "You are a helpful voice assistant" in prompt
    assert prompt.endswith("Assistant:")


def test_conversation_flow():
    """Test a complete conversation flow."""
    # Start conversation
    conversation.add_user_message("Hello")
    conversation.add_assistant_message("Hi! How can I help?")
    conversation.add_user_message("What's the weather?")
    conversation.add_assistant_message("It's sunny today.")
    conversation.add_user_message("Thanks, goodbye!")

    # Check history
    history = conversation.get_history()
    assert len(history) == 5

    # Check ending detection
    assert conversation.is_conversation_ending() is True

    # Format for LLM
    prompt = conversation.format_for_llm("ollama")
    assert "What's the weather?" in prompt

    # Clear for next conversation
    conversation.clear_history()
    assert len(conversation.get_history()) == 0
