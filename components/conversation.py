"""
Conversation history management module.

Manages conversation history as a simple list of dictionaries,
handles pruning, ending detection, and formatting for LLM consumption.
"""

# Global conversation history
conversation_history = []

# Configuration constants
MAX_HISTORY_TURNS = 10  # Maximum turns to keep (1 turn = user + assistant message pair)
ENDING_PHRASES = [
    "goodbye",
    "bye",
    "see you",
    "that's all",
    "nevermind",
    "stop",
    "quit",
    "exit",
]


def add_user_message(text: str) -> None:
    """
    Add a user message to the conversation history.

    Args:
        text: The user's message text
    """
    conversation_history.append({"role": "user", "content": text})
    _prune_history()


def add_assistant_message(text: str) -> None:
    """
    Add an assistant message to the conversation history.

    Args:
        text: The assistant's message text
    """
    conversation_history.append({"role": "assistant", "content": text})
    _prune_history()


def clear_history() -> None:
    """Clear all conversation history."""
    conversation_history.clear()


def get_history() -> list:
    """
    Get a copy of the conversation history.

    Returns:
        A list copy of conversation history dictionaries
    """
    return conversation_history.copy()


def _prune_history() -> None:
    """
    Prune conversation history to maintain MAX_HISTORY_TURNS.

    Keeps only the last N exchanges (user+assistant pairs).
    MAX_HISTORY_TURNS of 10 means 20 messages (10 user + 10 assistant).
    """
    max_messages = MAX_HISTORY_TURNS * 2  # 2 messages per turn
    if len(conversation_history) > max_messages:
        # Remove oldest messages to keep only the last max_messages
        excess = len(conversation_history) - max_messages
        for _ in range(excess):
            conversation_history.pop(0)


def is_conversation_ending() -> bool:
    """
    Check if the last message indicates conversation should end.

    Returns:
        True if last message contains an ending phrase, False otherwise
    """
    if not conversation_history:
        return False

    last_message = conversation_history[-1]
    content = last_message.get("content", "").lower()

    return any(phrase in content for phrase in ENDING_PHRASES)


def format_for_llm(provider: str = "ollama") -> str | list:
    """
    Format conversation history for LLM consumption.

    Args:
        provider: The LLM provider name ("ollama", "openai", "anthropic")

    Returns:
        For Ollama: formatted prompt string
        For OpenAI/Anthropic: list of message dictionaries

    Raises:
        ValueError: If provider is unknown
    """
    system_message = "You are a helpful voice assistant. Keep responses brief (1-2 sentences)."

    if provider == "ollama":
        # Ollama format: system prompt + conversation history as text
        prompt = f"{system_message}\n\n"
        for msg in conversation_history:
            role = msg["role"].capitalize()
            content = msg["content"]
            prompt += f"{role}: {content}\n"
        prompt += "Assistant:"
        return prompt

    elif provider in ["openai", "anthropic"]:
        # OpenAI/Anthropic format: list of message dicts with system message
        messages = [{"role": "system", "content": system_message}]
        messages.extend(conversation_history)
        return messages

    else:
        raise ValueError(f"Unknown provider: {provider}")
