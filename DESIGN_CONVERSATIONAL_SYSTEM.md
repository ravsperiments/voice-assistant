# Conversational Voice Assistant System Design

**Version:** 2.0 (Simplified)
**Date:** 2025-10-25
**Author:** System Architect
**Target Hardware:** Raspberry Pi 5

---

## 1. Executive Summary

This document outlines the architecture for evolving the existing single-turn voice assistant into a natural, multi-turn conversational system. The design emphasizes simplicity and practicality while maintaining provider flexibility for LLM, STT, and TTS components.

**Design Philosophy:**
- **Simple over complex**: Two-loop structure instead of formal state machines
- **Functions over classes**: Minimal abstraction, maximum clarity
- **Flexible where needed**: Provider abstractions for LLM/STT/TTS switching
- **Practical over perfect**: Focus on working code, not framework building

**Key Goals:**
- Enable natural multi-turn conversations without wake word repetition
- Support switching between local (privacy) and cloud (quality) providers via configuration
- Maintain <500ms response start latency
- Memory-efficient conversation history management
- Target ~400-500 lines of new code (achievable in 2-3 weeks)

**What Makes This Design Different:**
- No formal state machine classes or state transition tables
- No manager classes (SessionManager, StateMachineCoordinator)
- No complex dataclasses for messages or metrics
- Simple list-based conversation history
- Function-based architecture with clear control flow
- 9 total providers (down from 12 in previous design)

---

## 2. Requirements

### 2.1 Functional Requirements

**FR-1: Multi-Turn Conversations**
- System must support continuous back-and-forth dialogue after initial wake word
- No wake word required between conversation turns
- Maintain conversation context across multiple exchanges

**FR-2: Session Management**
- Detect when user has finished speaking vs. waiting for response
- Implement conversation timeout (configurable, default 10 seconds)
- Support explicit exit phrases ("goodbye", "that's all", "nevermind", etc.)
- Return to wake word listening after conversation ends

**FR-3: Conversation Context**
- Maintain conversation history for LLM context
- Limit history to last N turns (configurable, default 10)
- Include both user and assistant messages in context

**FR-4: Provider Flexibility**
- Support multiple LLM providers (Ollama, OpenAI, Anthropic)
- Support multiple STT providers (Vosk, Whisper, Deepgram)
- Support multiple TTS providers (Orca, Piper, OpenAI)
- Switch providers via configuration without code changes

**FR-5: Smart Audio Handling**
- Wake word detection mode (low power, continuous listening)
- Conversation mode (voice activity detection, turn-taking)
- Simple VAD for detecting user speech vs. silence

**FR-6: Low Latency Response**
- Target <500ms from end of user speech to start of response
- Minimize processing overhead between components

### 2.2 Non-Functional Requirements

**NFR-1: Performance**
- CPU usage: Target <30% average on Raspberry Pi 5
- Memory footprint: <500MB including all models
- Response latency: <500ms to start speaking response

**NFR-2: Resource Management**
- Bounded conversation history (memory cleanup)
- Efficient audio buffer management
- Model loading optimization (lazy loading, singleton patterns)

**NFR-3: Reliability**
- Graceful degradation on network/Ollama failures
- Recovery from audio device errors
- Simple error handling with try/except blocks

**NFR-4: Maintainability**
- Clear, readable code with minimal abstraction
- Functions and modules over complex class hierarchies
- Configuration-driven behavior (timeouts, limits, providers)

**NFR-5: Simplicity**
- Total new code: ~400-500 lines
- Implementation time: 2-3 weeks
- No over-engineering or premature optimization

---

## 3. System Architecture Overview

### 3.1 High-Level Architecture

```
┌──────────────────────────────────────────────────────────┐
│                   Voice Assistant                         │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────────────────────────────────────────┐   │
│  │               main.py (150 lines)                 │   │
│  │                                                    │   │
│  │  Outer loop: Wait for wake word                   │   │
│  │  Inner loop: Conversation turns                   │   │
│  │                                                    │   │
│  │  Flow:                                            │   │
│  │  1. wait_for_wake_word()                          │   │
│  │  2. clear_history()                               │   │
│  │  3. while conversation_active:                    │   │
│  │     - transcribe_audio()                          │   │
│  │     - generate_response()                         │   │
│  │     - speak_text()                                │   │
│  │     - has_voice_activity(timeout)                 │   │
│  └──────────────────────────────────────────────────┘   │
│                          │                                │
│         ┌────────────────┼────────────────┐             │
│         │                │                 │             │
│    ┌────▼─────┐   ┌─────▼──────┐   ┌─────▼──────┐     │
│    │ wake_word│   │conversation│   │   llm.py   │     │
│    │   .py    │   │   .py      │   │            │     │
│    │          │   │            │   │ Providers: │     │
│    │ (keep    │   │ Functions: │   │ - Ollama   │     │
│    │ as-is)   │   │ - add_msg  │   │ - OpenAI   │     │
│    └──────────┘   │ - format   │   │ - Anthropic│     │
│                   │ - is_end   │   └────────────┘     │
│    ┌──────────┐   └────────────┘                       │
│    │  stt.py  │                      ┌──────────┐     │
│    │          │                      │  tts.py  │     │
│    │Providers:│                      │          │     │
│    │- Vosk    │                      │Providers:│     │
│    │- Whisper │                      │- Orca    │     │
│    │- Deepgram│                      │- Piper   │     │
│    └──────────┘                      │- OpenAI  │     │
│                                       └──────────┘     │
└──────────────────────────────────────────────────────────┘

External Dependencies:
┌──────────────┐  ┌─────────────┐  ┌──────────────┐
│   Porcupine  │  │   Ollama/   │  │  Vosk/Orca/  │
│  (Wake Word) │  │  OpenAI/    │  │   Whisper/   │
│              │  │  Anthropic  │  │   Piper      │
└──────────────┘  └─────────────┘  └──────────────┘
```

### 3.2 Component Responsibilities

**main.py** (NEW - core conversation loop)
- Implements simple two-loop structure
- Outer loop: Wait for wake word, then start conversation
- Inner loop: Conversation turns (listen → process → speak → check for continuation)
- No state machine classes, just clear control flow
- ~100-150 lines of code

**wake_word.py** (EXISTING - keep as-is)
- Handles Porcupine wake word detection
- Already implemented and working
- No changes needed

**stt.py** (MODIFY - add provider routing)
- Adds provider abstraction for STT
- Main function: `transcribe_audio(provider: str) -> Optional[str]`
- Supports Vosk (default), Whisper, Deepgram
- Includes simple VAD function: `has_voice_activity(timeout: float) -> bool`
- ~150-200 lines total

**llm.py** (MODIFY - add provider routing)
- Adds provider abstraction for LLM
- Main function: `generate_response(prompt: str, provider: str) -> str`
- Supports Ollama (default), OpenAI, Anthropic
- Routes to provider-specific internal functions
- ~150-200 lines total

**tts.py** (MODIFY - add provider routing)
- Adds provider abstraction for TTS
- Main function: `speak_text(text: str, provider: str) -> bool`
- Supports Orca (default), Piper, OpenAI
- Routes to provider-specific internal functions
- ~150-200 lines total

**conversation.py** (NEW - simple history management)
- Manages conversation history as simple list of dicts
- Functions: `add_user_message()`, `add_assistant_message()`, `clear_history()`
- Function: `format_for_llm(provider: str) -> str` (handles provider-specific formatting)
- Function: `is_conversation_ending() -> bool` (detects goodbye phrases)
- ~50-80 lines of code

**config.py** (MODIFY - add provider settings)
- Add provider selection fields (LLM_PROVIDER, STT_PROVIDER, TTS_PROVIDER)
- Add provider-specific configuration
- Add conversation settings (MAX_HISTORY_TURNS, AWAITING_TIMEOUT, etc.)
- ~50 lines of additions

### 3.3 Control Flow

**Simple Two-Loop Structure:**

```python
def main():
    """Main conversation loop - simple and clear."""

    while True:
        # OUTER LOOP: Wait for wake word
        print("Listening for wake word...")
        wait_for_wake_word()

        # Start new conversation
        clear_history()
        speak_text("Hello! How can I help?", config.TTS_PROVIDER)
        conversation_active = True

        # INNER LOOP: Conversation turns
        while conversation_active:
            # 1. Listen for user input
            user_text = transcribe_audio(config.STT_PROVIDER)
            if not user_text:
                # No speech detected, end conversation
                break

            add_user_message(user_text)

            # 2. Generate response
            prompt = format_for_llm(config.LLM_PROVIDER)
            response = generate_response(prompt, config.LLM_PROVIDER)
            add_assistant_message(response)

            # 3. Speak response
            speak_text(response, config.TTS_PROVIDER)

            # 4. Check if conversation should continue
            if is_conversation_ending():
                break

            # 5. Wait for next user turn (with timeout)
            if not has_voice_activity(timeout=config.AWAITING_TIMEOUT):
                # Timeout - no speech detected
                break

        # Conversation ended
        speak_text("Goodbye!", config.TTS_PROVIDER)
```

**Why This Works:**
- Crystal clear control flow - anyone can understand it
- No state machine classes or transition tables
- Easy to debug - just step through the loops
- Easy to modify - add features by editing the loop
- Conversation logic is explicit, not hidden in state handlers

---

## 4. Component Specifications

### 4.1 LLM Provider Abstraction (llm.py)

**Purpose:** Abstract LLM interface supporting multiple providers (Ollama, OpenAI, Anthropic) with unified API.

**Why Keep This Abstraction:**
- Realistic need to switch between local (privacy, offline) and cloud (quality, speed)
- Different deployment scenarios (home vs. commercial)
- Cost/quality tradeoffs (Ollama free but slow, OpenAI fast but paid)

**Supported Providers (3 total):**

| Provider   | Best For                    | Latency    | Cost      | Requires        |
|------------|-----------------------------|------------|-----------|-----------------|
| Ollama     | Privacy, offline, Pi deploy | 2-5s       | Free      | Local install   |
| OpenAI     | Low latency, high quality   | 0.5-2s     | Paid      | API key         |
| Anthropic  | Natural conversation        | 0.5-2s     | Paid      | API key         |

**Implementation:**

```python
def generate_response(prompt: str, provider: str = "ollama") -> str:
    """Generate LLM response using configured provider.

    Args:
        prompt: Formatted conversation history + user message
        provider: "ollama", "openai", or "anthropic"

    Returns:
        Assistant response text

    Raises:
        ValueError: Unknown provider
        ConnectionError: Provider unavailable
    """
    try:
        if provider == "ollama":
            return _call_ollama(prompt)
        elif provider == "openai":
            return _call_openai(prompt)
        elif provider == "anthropic":
            return _call_anthropic(prompt)
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")
    except Exception as e:
        logger.error(f"LLM error: {e}")
        return "I'm having trouble thinking right now. Could you repeat that?"


def _call_ollama(prompt: str) -> str:
    """Call local Ollama API."""
    response = requests.post(
        f"{config.OLLAMA_BASE_URL}/api/generate",
        json={
            "model": config.OLLAMA_MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": config.MAX_RESPONSE_TOKENS,
                "temperature": 0.7,
            }
        },
        timeout=30
    )
    return response.json()["response"]


def _call_openai(prompt: str) -> str:
    """Call OpenAI API."""
    # Convert prompt to messages format
    messages = _prompt_to_messages(prompt)

    client = OpenAI(api_key=config.OPENAI_API_KEY)
    response = client.chat.completions.create(
        model=config.OPENAI_MODEL_NAME,
        messages=messages,
        max_tokens=config.MAX_RESPONSE_TOKENS,
        temperature=0.7
    )
    return response.choices[0].message.content


def _call_anthropic(prompt: str) -> str:
    """Call Anthropic API."""
    # Convert prompt to messages format
    messages = _prompt_to_messages(prompt)

    client = Anthropic(api_key=config.ANTHROPIC_API_KEY)
    response = client.messages.create(
        model=config.ANTHROPIC_MODEL_NAME,
        messages=messages,
        max_tokens=config.MAX_RESPONSE_TOKENS,
        temperature=0.7
    )
    return response.content[0].text


def _prompt_to_messages(prompt: str) -> List[Dict]:
    """Convert Ollama-style prompt to OpenAI/Anthropic messages format."""
    # Simple implementation: split by "User:" and "Assistant:" markers
    # Or get from conversation.py history directly
    pass
```

**Configuration:**

```python
# config.py additions
LLM_PROVIDER = "ollama"  # ollama, openai, anthropic
MAX_RESPONSE_TOKENS = 100  # ~15-20 seconds of speech

# Ollama settings (existing)
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL_NAME = "granite3.2:2b"

# OpenAI settings (new)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL_NAME = "gpt-4o-mini"

# Anthropic settings (new)
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_MODEL_NAME = "claude-3-5-haiku-20241022"
```

**Why 100 tokens?**
- 100 tokens ≈ 60-80 words ≈ 15-20 seconds of TTS playback
- Voice interactions should be brief
- Users lose attention after 20-30 seconds
- Keeps responses conversational, not lecture-like

---

### 4.2 STT Provider Abstraction (stt.py)

**Purpose:** Abstract STT interface supporting multiple providers (Vosk, Whisper, Deepgram) with unified API.

**Why Keep This Abstraction:**
- May need better accuracy than Vosk (e.g., accents, noisy environments)
- Cloud providers much faster and more accurate
- Whisper good for offline high-accuracy fallback

**Supported Providers (3 total, reduced from 4):**

| Provider   | Best For               | Latency    | Accuracy  | Cost      | Offline |
|------------|------------------------|------------|-----------|-----------|---------|
| Vosk       | Privacy, Pi default    | 1-3s       | Good      | Free      | Yes     |
| Whisper    | High accuracy offline  | 2-5s       | Excellent | Free      | Yes     |
| Deepgram   | Low latency cloud      | 0.3-1s     | Excellent | Paid      | No      |

**Removed:** Google Cloud STT (redundant with Deepgram, Deepgram is faster)

**Implementation:**

```python
def transcribe_audio(provider: str = "vosk") -> Optional[str]:
    """Transcribe audio from microphone using configured provider.

    Args:
        provider: "vosk", "whisper", or "deepgram"

    Returns:
        Transcribed text or None if no speech detected

    Raises:
        ValueError: Unknown provider
    """
    try:
        if provider == "vosk":
            return _transcribe_vosk()
        elif provider == "whisper":
            return _transcribe_whisper()
        elif provider == "deepgram":
            return _transcribe_deepgram()
        else:
            raise ValueError(f"Unknown STT provider: {provider}")
    except Exception as e:
        logger.error(f"STT error: {e}")
        return None


def has_voice_activity(timeout_seconds: float = 10.0) -> bool:
    """Simple VAD to detect if user is speaking.

    Args:
        timeout_seconds: How long to wait for speech

    Returns:
        True if voice detected within timeout, False otherwise
    """
    # Simple energy-based VAD
    start_time = time.time()
    energy_threshold = config.VAD_ENERGY_THRESHOLD

    while time.time() - start_time < timeout_seconds:
        # Read audio frame
        audio_data = pyaudio_stream.read(CHUNK_SIZE)

        # Calculate energy
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        energy = np.abs(audio_array).mean()

        # Check if above threshold
        if energy > energy_threshold:
            return True

        time.sleep(0.1)

    return False


def _transcribe_vosk() -> Optional[str]:
    """Transcribe using Vosk (existing implementation)."""
    # Keep existing Vosk code
    pass


def _transcribe_whisper() -> Optional[str]:
    """Transcribe using Whisper (local model)."""
    import whisper

    # Record audio to temp file
    audio_file = _record_to_file()

    # Transcribe
    model = whisper.load_model(config.WHISPER_MODEL)
    result = model.transcribe(audio_file, language="en")

    return result["text"].strip()


def _transcribe_deepgram() -> Optional[str]:
    """Transcribe using Deepgram API."""
    from deepgram import Deepgram

    # Record audio to buffer
    audio_data = _record_to_buffer()

    # Call Deepgram API
    dg_client = Deepgram(config.DEEPGRAM_API_KEY)
    response = dg_client.transcription.sync_prerecorded(
        {"buffer": audio_data, "mimetype": "audio/wav"},
        {"punctuate": True, "language": "en-US"}
    )

    return response["results"]["channels"][0]["alternatives"][0]["transcript"]
```

**Configuration:**

```python
# config.py additions
STT_PROVIDER = "vosk"  # vosk, whisper, deepgram

# Vosk settings (existing)
VOSK_MODEL_PATH = "models/vosk-model-small-en-us-0.15"

# Whisper settings (new)
WHISPER_MODEL = "base"  # tiny, base, small (for Pi)

# Deepgram settings (new)
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

# VAD settings
VAD_ENERGY_THRESHOLD = 500
```

---

### 4.3 TTS Provider Abstraction (tts.py)

**Purpose:** Abstract TTS interface supporting multiple providers (Orca, Piper, OpenAI) with unified API.

**Why Keep This Abstraction:**
- Orca costs money ($1.99/month), Piper is free
- May want higher quality for commercial deployments
- OpenAI TTS very natural but costs per character

**Supported Providers (3 total, reduced from 5):**

| Provider   | Best For               | Latency    | Quality    | Cost        | Offline |
|------------|------------------------|------------|------------|-------------|---------|
| Orca       | Current default        | ~1s        | Good       | $1.99/month | Yes     |
| Piper      | Free alternative       | ~1s        | Good       | Free        | Yes     |
| OpenAI     | Highest quality        | 0.5-1s     | Excellent  | $15/1M chars| No      |

**Removed:** Google TTS (redundant), ElevenLabs (too expensive, OpenAI better value)

**Implementation:**

```python
def speak_text(text: str, provider: str = "orca") -> bool:
    """Speak text using configured TTS provider.

    Args:
        text: Text to speak
        provider: "orca", "piper", or "openai"

    Returns:
        True if successful, False otherwise
    """
    try:
        if provider == "orca":
            return _speak_orca(text)
        elif provider == "piper":
            return _speak_piper(text)
        elif provider == "openai":
            return _speak_openai(text)
        else:
            raise ValueError(f"Unknown TTS provider: {provider}")
    except Exception as e:
        logger.error(f"TTS error: {e}")
        return False


def _speak_orca(text: str) -> bool:
    """Speak using Orca (existing implementation)."""
    # Keep existing Orca code
    pass


def _speak_piper(text: str) -> bool:
    """Speak using Piper TTS."""
    # Call Piper command-line tool
    subprocess.run([
        "piper",
        "--model", config.PIPER_MODEL_PATH,
        "--output-file", "/tmp/piper_output.wav"
    ], input=text.encode(), check=True)

    # Play audio file
    _play_audio_file("/tmp/piper_output.wav")
    return True


def _speak_openai(text: str) -> bool:
    """Speak using OpenAI TTS API."""
    from openai import OpenAI

    client = OpenAI(api_key=config.OPENAI_API_KEY)
    response = client.audio.speech.create(
        model="tts-1",  # or tts-1-hd for higher quality
        voice=config.OPENAI_TTS_VOICE,
        input=text
    )

    # Save and play
    response.stream_to_file("/tmp/openai_tts.mp3")
    _play_audio_file("/tmp/openai_tts.mp3")
    return True
```

**Configuration:**

```python
# config.py additions
TTS_PROVIDER = "orca"  # orca, piper, openai

# Orca settings (existing)
# ... keep existing Orca config ...

# Piper settings (new)
PIPER_MODEL_PATH = "models/en_US-lessac-medium.onnx"

# OpenAI TTS settings (new)
OPENAI_TTS_VOICE = "alloy"  # alloy, echo, fable, onyx, nova, shimmer
```

---

### 4.4 Conversation Management (conversation.py)

**Purpose:** Simple conversation history management with provider-specific formatting.

**Why Keep This Simple:**
- No need for dataclasses or complex structures
- List of dicts is easy to understand and debug
- Easy to serialize/log for debugging
- Minimal code (~50-80 lines)

**Implementation:**

```python
"""Conversation history management - simple and practical."""

from typing import List, Dict, Optional

# Global conversation history (simple list of dicts)
conversation_history: List[Dict[str, str]] = []


def add_user_message(text: str) -> None:
    """Add user message to history."""
    conversation_history.append({
        "role": "user",
        "content": text
    })
    _prune_history()


def add_assistant_message(text: str) -> None:
    """Add assistant message to history."""
    conversation_history.append({
        "role": "assistant",
        "content": text
    })
    _prune_history()


def clear_history() -> None:
    """Clear conversation history (start of new conversation)."""
    conversation_history.clear()


def get_history() -> List[Dict[str, str]]:
    """Get current conversation history."""
    return conversation_history.copy()


def format_for_llm(provider: str) -> str:
    """Format conversation history for LLM provider.

    Args:
        provider: "ollama", "openai", or "anthropic"

    Returns:
        Formatted prompt or messages structure
    """
    if provider == "ollama":
        # Ollama uses simple prompt format
        return _format_ollama_prompt()
    elif provider in ["openai", "anthropic"]:
        # OpenAI/Anthropic use messages format (returned as JSON string)
        # Actual conversion happens in llm.py
        return conversation_history
    else:
        raise ValueError(f"Unknown provider: {provider}")


def is_conversation_ending() -> bool:
    """Detect if conversation should end based on last exchange.

    Checks last user or assistant message for ending phrases.

    Returns:
        True if conversation should end, False otherwise
    """
    if not conversation_history:
        return False

    # Check last message (user or assistant)
    last_message = conversation_history[-1]["content"].lower()

    ending_phrases = [
        "goodbye", "bye", "good bye",
        "see you", "see ya",
        "that's all", "that is all",
        "nevermind", "never mind",
        "thanks anyway", "thank you anyway",
        "i'm done", "i am done",
        "stop", "quit", "exit"
    ]

    return any(phrase in last_message for phrase in ending_phrases)


def _prune_history() -> None:
    """Limit history to last N turns."""
    max_turns = config.MAX_HISTORY_TURNS
    if len(conversation_history) > max_turns * 2:
        # Keep system message if present, then last N exchanges
        conversation_history[:] = conversation_history[-(max_turns * 2):]


def _format_ollama_prompt() -> str:
    """Format history as Ollama prompt string."""
    # System message
    prompt = "You are a helpful voice assistant. Keep responses brief (1-2 sentences).\n\n"

    # Add conversation history
    for msg in conversation_history:
        role = msg["role"].capitalize()
        content = msg["content"]
        prompt += f"{role}: {content}\n"

    # Add final assistant prompt
    prompt += "Assistant:"

    return prompt
```

**Configuration:**

```python
# config.py additions
MAX_HISTORY_TURNS = 10  # Last 10 user+assistant exchanges
```

**Data Structure Example:**

```python
# Simple list of dicts
conversation_history = [
    {"role": "user", "content": "What's the weather?"},
    {"role": "assistant", "content": "I don't have access to weather data."},
    {"role": "user", "content": "What time is it?"},
    {"role": "assistant", "content": "I don't have access to the current time."}
]
```

**Why This Works:**
- Simple to understand and debug
- Easy to serialize to JSON for logging
- Compatible with OpenAI/Anthropic message formats
- No complex dataclasses needed
- Easy to extend (add timestamps if needed later)

---

### 4.5 Main Conversation Loop (main.py)

**Purpose:** Orchestrate the conversation flow with simple, clear control logic.

**Complete Implementation:**

```python
"""Main conversation loop - simple two-loop structure."""

import logging
import time
from typing import Optional

import config
from components.wake_word import wait_for_wake_word
from components.stt import transcribe_audio, has_voice_activity
from components.llm import generate_response
from components.tts import speak_text
from components.conversation import (
    add_user_message,
    add_assistant_message,
    clear_history,
    format_for_llm,
    is_conversation_ending
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main conversation loop."""
    logger.info("Voice assistant starting...")

    # Initialize components (lazy loading handled in each module)
    logger.info(f"LLM Provider: {config.LLM_PROVIDER}")
    logger.info(f"STT Provider: {config.STT_PROVIDER}")
    logger.info(f"TTS Provider: {config.TTS_PROVIDER}")

    try:
        while True:
            # ========================================
            # OUTER LOOP: Wait for wake word
            # ========================================
            logger.info("Listening for wake word...")
            wait_for_wake_word()
            logger.info("Wake word detected!")

            # Start new conversation
            clear_history()
            speak_text("Hello! How can I help?", config.TTS_PROVIDER)

            conversation_active = True
            turn_count = 0

            # ========================================
            # INNER LOOP: Conversation turns
            # ========================================
            while conversation_active:
                turn_count += 1
                logger.info(f"Conversation turn {turn_count}")

                # 1. Listen for user input
                logger.info("Listening for user...")
                user_text = transcribe_audio(config.STT_PROVIDER)

                if not user_text:
                    logger.info("No speech detected, ending conversation")
                    break

                logger.info(f"User said: {user_text}")
                add_user_message(user_text)

                # 2. Generate response
                logger.info("Generating response...")
                try:
                    prompt = format_for_llm(config.LLM_PROVIDER)
                    response = generate_response(prompt, config.LLM_PROVIDER)
                    logger.info(f"Assistant response: {response}")
                    add_assistant_message(response)
                except Exception as e:
                    logger.error(f"Error generating response: {e}")
                    response = "I'm sorry, I'm having trouble thinking right now."
                    add_assistant_message(response)

                # 3. Speak response
                logger.info("Speaking response...")
                speak_text(response, config.TTS_PROVIDER)

                # 4. Check if conversation should end
                if is_conversation_ending():
                    logger.info("Conversation ending detected (goodbye phrase)")
                    break

                # 5. Wait for next user turn (with timeout)
                logger.info(f"Waiting for next turn (timeout: {config.AWAITING_TIMEOUT}s)...")
                if not has_voice_activity(timeout=config.AWAITING_TIMEOUT):
                    logger.info("Timeout - no speech detected, ending conversation")
                    break

            # Conversation ended
            logger.info(f"Conversation ended after {turn_count} turns")
            speak_text("Goodbye!", config.TTS_PROVIDER)
            time.sleep(1)  # Brief pause before returning to wake word

    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
    finally:
        # Cleanup (if needed)
        logger.info("Voice assistant stopped")


if __name__ == "__main__":
    main()
```

**Line Count:** ~100-120 lines including comments and logging

**Why This Works:**
- Crystal clear logic - anyone can understand the flow
- Easy to debug - just step through the loops
- Easy to modify - want a feature? Add it to the loop
- No hidden complexity - everything is explicit
- Logging at every step for debugging

---

## 5. Configuration

### 5.1 Configuration Structure (config.py)

**Complete configuration with provider settings:**

```python
"""Configuration for voice assistant - all settings in one place."""

import os
from dataclasses import dataclass
from typing import Optional

# ============================================
# Provider Selection (simple strings)
# ============================================

LLM_PROVIDER = "ollama"  # ollama, openai, anthropic
STT_PROVIDER = "vosk"     # vosk, whisper, deepgram
TTS_PROVIDER = "orca"     # orca, piper, openai

# ============================================
# Conversation Settings
# ============================================

MAX_HISTORY_TURNS = 10  # Last N user+assistant exchanges
AWAITING_TIMEOUT = 10.0  # Seconds to wait for next user turn
MAX_RESPONSE_TOKENS = 100  # ~15-20 seconds of speech

# ============================================
# LLM Provider Settings
# ============================================

# Ollama (existing settings)
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL_NAME = "granite3.2:2b"

# OpenAI (new)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL_NAME = "gpt-4o-mini"

# Anthropic (new)
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_MODEL_NAME = "claude-3-5-haiku-20241022"

# ============================================
# STT Provider Settings
# ============================================

# Vosk (existing settings)
VOSK_MODEL_PATH = "models/vosk-model-small-en-us-0.15"
VOSK_SAMPLE_RATE = 16000

# Whisper (new)
WHISPER_MODEL = "base"  # tiny, base, small (for Pi)

# Deepgram (new)
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

# VAD settings
VAD_ENERGY_THRESHOLD = 500

# ============================================
# TTS Provider Settings
# ============================================

# Orca (existing settings)
ORCA_ACCESS_KEY = os.getenv("ORCA_ACCESS_KEY")
ORCA_MODEL_PATH = "models/orca_params.pv"

# Piper (new)
PIPER_MODEL_PATH = "models/en_US-lessac-medium.onnx"

# OpenAI TTS (new)
OPENAI_TTS_VOICE = "alloy"  # alloy, echo, fable, onyx, nova, shimmer

# ============================================
# Wake Word Settings (existing)
# ============================================

WAKE_WORD_ACCESS_KEY = os.getenv("PORCUPINE_ACCESS_KEY")
WAKE_WORD_KEYWORD = "jarvis"

# ============================================
# Audio Settings (existing)
# ============================================

AUDIO_SAMPLE_RATE = 16000
AUDIO_CHUNK_SIZE = 512
```

### 5.2 Environment Variables

**Required for cloud providers:**

```bash
# .env file example
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
DEEPGRAM_API_KEY=...
ORCA_ACCESS_KEY=...
PORCUPINE_ACCESS_KEY=...
```

---

## 6. Data Architecture

### 6.1 Conversation History Structure

**Simple list of dicts - no dataclasses:**

```python
# Global variable in conversation.py
conversation_history: List[Dict[str, str]] = [
    {"role": "user", "content": "What's the weather?"},
    {"role": "assistant", "content": "I don't have access to weather data."},
    {"role": "user", "content": "What time is it?"},
    {"role": "assistant", "content": "I don't have access to the current time."}
]
```

**Why This Works:**
- Simple to understand and debug
- Compatible with OpenAI/Anthropic message formats
- Easy to serialize to JSON for logging
- No complex dataclasses or schemas
- Can add fields later if needed (timestamps, etc.)

### 6.2 No Session Management

**Deleted from previous design:**
- SessionMetrics dataclass
- SessionState dataclass
- SessionManager class
- Complex session tracking

**What we keep:**
- Turn count (simple integer in main loop)
- Conversation active flag (boolean in main loop)
- History (list of dicts)

**Why:**
- Don't need metrics for MVP
- Don't need session persistence
- Simple variables in main loop are enough
- Can add later if truly needed

### 6.3 No Message Dataclass

**Deleted from previous design:**
```python
# DON'T NEED THIS
@dataclass
class Message:
    role: str
    content: str
    timestamp: float
```

**What we use instead:**
```python
# Simple dict
{"role": "user", "content": "hello"}
```

**Why:**
- Dicts are simpler and more flexible
- No need for timestamps in MVP
- Easy to serialize/deserialize
- One less abstraction to maintain

---

## 7. Error Handling

### 7.1 Simple Try/Except Strategy

**No complex retry logic or exponential backoff:**

```python
# In main loop
try:
    response = generate_response(prompt, config.LLM_PROVIDER)
    add_assistant_message(response)
except Exception as e:
    logger.error(f"Error generating response: {e}")
    response = "I'm sorry, I'm having trouble thinking right now."
    add_assistant_message(response)
```

**Provider-level error handling:**

```python
# In llm.py
def generate_response(prompt: str, provider: str) -> str:
    try:
        if provider == "ollama":
            return _call_ollama(prompt)
        # ... other providers ...
    except ConnectionError:
        logger.error("LLM provider unavailable")
        return "I'm having trouble connecting right now."
    except Exception as e:
        logger.error(f"LLM error: {e}")
        return "I'm having trouble thinking right now. Could you repeat that?"
```

### 7.2 Graceful Degradation

**If STT fails:**
- Return None
- Main loop ends conversation
- Returns to wake word listening

**If LLM fails:**
- Return fallback message
- Conversation continues
- User can retry or end

**If TTS fails:**
- Log error
- Return False
- Main loop continues (user won't hear response but can continue)

### 7.3 Audio Device Errors

**Simple recovery:**

```python
# In wake_word.py and stt.py
try:
    audio_stream = pyaudio.open(...)
except Exception as e:
    logger.error(f"Audio device error: {e}")
    time.sleep(5)  # Wait and retry
    audio_stream = pyaudio.open(...)
```

---

## 8. File Structure

### 8.1 Project Layout

```
voice-assistant/
├── main.py                          # NEW: Main conversation loop (100-150 lines)
├── config.py                        # MODIFY: Add provider settings (~50 lines added)
├── requirements.txt                 # MODIFY: Add new dependencies
├── .env.example                     # NEW: Example environment variables
├── README.md                        # UPDATE: New usage instructions
│
├── components/
│   ├── __init__.py                 # EXISTING
│   ├── wake_word.py                # EXISTING: Keep as-is (no changes)
│   ├── stt.py                      # MODIFY: Add provider abstraction (~150-200 lines)
│   ├── llm.py                      # MODIFY: Add provider abstraction (~150-200 lines)
│   ├── tts.py                      # MODIFY: Add provider abstraction (~150-200 lines)
│   └── conversation.py             # NEW: History management (~50-80 lines)
│
├── models/                          # EXISTING: Model files
│   ├── vosk-model-small-en-us-0.15/
│   ├── en_US-lessac-medium.onnx   # NEW: Piper model (optional)
│   └── orca_params.pv
│
└── tests/                           # OPTIONAL: Basic tests
    ├── test_conversation.py
    ├── test_llm.py
    ├── test_stt.py
    └── test_tts.py
```

### 8.2 Code Size Estimate

| File              | Lines (approx) | Status   |
|-------------------|----------------|----------|
| main.py           | 100-150        | NEW      |
| conversation.py   | 50-80          | NEW      |
| config.py         | +50            | MODIFY   |
| llm.py            | +100-150       | MODIFY   |
| stt.py            | +100-150       | MODIFY   |
| tts.py            | +100-150       | MODIFY   |
| **Total new code**| **400-500**    | -        |

**Previous design estimate:** 1500+ lines
**Current design estimate:** 400-500 lines
**Reduction:** ~70% less code

---

## 9. Dependencies

### 9.1 Required Packages

**Add to requirements.txt:**

```txt
# Existing dependencies
pvporcupine==3.0.0
vosk==0.3.45
pyaudio==0.2.14
requests==2.31.0

# New LLM providers
openai==1.12.0
anthropic==0.18.0

# New STT providers
openai-whisper==20231117  # For local Whisper
deepgram-sdk==3.0.0

# New TTS providers
# Piper: Install via system package manager
# OpenAI: Already included above

# Utilities
python-dotenv==1.0.0
```

### 9.2 System Dependencies

**For Piper TTS (optional):**

```bash
# Install Piper on Raspberry Pi
sudo apt-get install -y piper-tts

# Download Piper model
wget https://github.com/rhasspy/piper/releases/download/v1.2.0/en_US-lessac-medium.onnx
mv en_US-lessac-medium.onnx models/
```

---

## 10. Testing Strategy

### 10.1 Manual Testing Focus

**No comprehensive test framework for MVP:**

Testing priorities:
1. Manual end-to-end testing (most important)
2. Provider switching validation
3. Error condition testing
4. Basic integration tests (optional)

### 10.2 Test Scenarios

**Test each provider combination:**

| Test | LLM     | STT      | TTS    | Expected Result              |
|------|---------|----------|--------|------------------------------|
| 1    | Ollama  | Vosk     | Orca   | Full offline mode works      |
| 2    | OpenAI  | Vosk     | Orca   | Cloud LLM + local STT/TTS    |
| 3    | Ollama  | Deepgram | Orca   | Cloud STT + local LLM/TTS    |
| 4    | OpenAI  | Deepgram | OpenAI | Full cloud mode works        |

**Test conversation flows:**

1. Wake word → single question → answer → timeout → goodbye
2. Wake word → multi-turn conversation → explicit goodbye
3. Wake word → question → no answer detected → timeout
4. Provider failure handling (disconnect Ollama, invalid API key, etc.)

### 10.3 Optional Unit Tests

**If time permits, test critical functions:**

```python
# tests/test_conversation.py
def test_add_message():
    clear_history()
    add_user_message("hello")
    assert len(conversation_history) == 1
    assert conversation_history[0]["role"] == "user"

def test_is_conversation_ending():
    clear_history()
    add_user_message("goodbye")
    assert is_conversation_ending() == True

def test_prune_history():
    clear_history()
    for i in range(20):
        add_user_message(f"message {i}")
    assert len(conversation_history) <= config.MAX_HISTORY_TURNS
```

---

## 11. Migration Path

### 11.1 Three-Phase Implementation

**Phase 1: Core Conversation Loop (Week 1)**
- Create main.py with simple two-loop structure
- Create conversation.py for history management
- Test with existing single provider (Ollama, Vosk, Orca)
- Deliverable: Working multi-turn conversation with default providers

**Phase 2: Provider Abstractions (Week 2)**
- Add provider routing to llm.py (OpenAI, Anthropic)
- Add provider routing to stt.py (Whisper, Deepgram)
- Add provider routing to tts.py (Piper, OpenAI)
- Update config.py with provider settings
- Deliverable: Full provider flexibility via configuration

**Phase 3: Polish & Optimization (Week 3)**
- Add better error handling
- Optimize VAD parameters
- Add logging and debugging tools
- Test all provider combinations
- Update documentation
- Deliverable: Production-ready system

### 11.2 Backward Compatibility

**Keep existing functionality:**
- wake_word.py unchanged
- Existing Vosk STT code preserved (becomes _transcribe_vosk)
- Existing Orca TTS code preserved (becomes _speak_orca)
- Existing Ollama LLM code preserved (becomes _call_ollama)

**Easy rollback:**
- If Phase 2 fails, Phase 1 still works with default providers
- No breaking changes to existing components
- Can deploy Phase 1 to production while developing Phase 2

---

## 12. Task Breakdown

### 12.1 Implementation Tasks

**Phase 1: Core Conversation Loop (5 tasks)**

**TASK-1: Create conversation.py**
- Complexity: Simple
- Time: 2-3 hours
- Dependencies: None
- Description: Implement conversation history management functions
- Deliverables:
  - `add_user_message()`, `add_assistant_message()`
  - `clear_history()`, `get_history()`
  - `format_for_llm()` (Ollama format only for now)
  - `is_conversation_ending()` (goodbye detection)
  - `_prune_history()` (limit history size)
- Testing: Unit tests for each function
- Acceptance Criteria:
  - Can add messages to history
  - History limited to MAX_HISTORY_TURNS
  - Goodbye detection works for common phrases
  - Format for Ollama produces correct prompt

**TASK-2: Implement has_voice_activity() in stt.py**
- Complexity: Simple
- Time: 2-3 hours
- Dependencies: None
- Description: Add simple energy-based VAD function
- Deliverables:
  - `has_voice_activity(timeout: float) -> bool`
  - Energy threshold configuration in config.py
- Testing: Manual testing with different noise levels
- Acceptance Criteria:
  - Detects voice within timeout
  - Returns False on timeout
  - Configurable energy threshold works

**TASK-3: Create main.py conversation loop**
- Complexity: Moderate
- Time: 4-6 hours
- Dependencies: TASK-1, TASK-2
- Description: Implement two-loop structure
- Deliverables:
  - Outer loop (wake word waiting)
  - Inner loop (conversation turns)
  - Error handling
  - Logging at each step
- Testing: End-to-end manual testing
- Acceptance Criteria:
  - Wake word triggers conversation
  - Multi-turn conversation works
  - Timeout ends conversation
  - Goodbye phrases end conversation
  - Logging shows flow clearly

**TASK-4: Update config.py with conversation settings**
- Complexity: Simple
- Time: 1 hour
- Dependencies: None
- Description: Add conversation configuration
- Deliverables:
  - MAX_HISTORY_TURNS setting
  - AWAITING_TIMEOUT setting
  - MAX_RESPONSE_TOKENS setting
  - VAD_ENERGY_THRESHOLD setting
- Testing: Verify settings are used correctly
- Acceptance Criteria:
  - All settings configurable
  - Settings affect behavior as expected

**TASK-5: Integration testing Phase 1**
- Complexity: Simple
- Time: 3-4 hours
- Dependencies: TASK-1, TASK-2, TASK-3, TASK-4
- Description: Test complete conversation flow
- Deliverables:
  - Test multi-turn conversations
  - Test timeout behavior
  - Test goodbye detection
  - Test history management
- Acceptance Criteria:
  - All conversation flows work
  - No memory leaks
  - Graceful error handling

---

**Phase 2: Provider Abstractions (6 tasks)**

**TASK-6: Add LLM provider routing to llm.py**
- Complexity: Moderate
- Time: 4-6 hours
- Dependencies: None
- Description: Add OpenAI and Anthropic support
- Deliverables:
  - `generate_response()` with provider parameter
  - `_call_ollama()` (refactor existing code)
  - `_call_openai()` (new)
  - `_call_anthropic()` (new)
  - Provider-specific error handling
- Testing: Test each provider separately
- Acceptance Criteria:
  - All 3 providers work
  - Switching via config works
  - Error handling for unavailable providers
  - Response format consistent across providers

**TASK-7: Add STT provider routing to stt.py**
- Complexity: Moderate
- Time: 4-6 hours
- Dependencies: None
- Description: Add Whisper and Deepgram support
- Deliverables:
  - `transcribe_audio()` with provider parameter
  - `_transcribe_vosk()` (refactor existing code)
  - `_transcribe_whisper()` (new)
  - `_transcribe_deepgram()` (new)
  - Provider-specific error handling
- Testing: Test each provider separately
- Acceptance Criteria:
  - All 3 providers work
  - Switching via config works
  - Transcription quality acceptable for each
  - Latency acceptable

**TASK-8: Add TTS provider routing to tts.py**
- Complexity: Moderate
- Time: 4-6 hours
- Dependencies: None
- Description: Add Piper and OpenAI TTS support
- Deliverables:
  - `speak_text()` with provider parameter
  - `_speak_orca()` (refactor existing code)
  - `_speak_piper()` (new)
  - `_speak_openai()` (new)
  - Provider-specific error handling
- Testing: Test each provider separately
- Acceptance Criteria:
  - All 3 providers work
  - Switching via config works
  - Audio quality acceptable for each
  - Latency acceptable

**TASK-9: Update config.py with all provider settings**
- Complexity: Simple
- Time: 2-3 hours
- Dependencies: TASK-6, TASK-7, TASK-8
- Description: Add all provider configurations
- Deliverables:
  - Provider selection fields (LLM_PROVIDER, STT_PROVIDER, TTS_PROVIDER)
  - OpenAI settings (API key, models)
  - Anthropic settings (API key, models)
  - Whisper settings (model selection)
  - Deepgram settings (API key)
  - Piper settings (model path)
  - OpenAI TTS settings (voice selection)
- Testing: Verify all settings work
- Acceptance Criteria:
  - All providers configurable
  - Environment variables loaded correctly
  - Invalid config detected early

**TASK-10: Update conversation.py for multi-provider formatting**
- Complexity: Simple
- Time: 2-3 hours
- Dependencies: TASK-6
- Description: Handle OpenAI/Anthropic message format
- Deliverables:
  - Update `format_for_llm()` to handle all providers
  - Convert between Ollama prompt and messages format
- Testing: Test formatting for each provider
- Acceptance Criteria:
  - Ollama receives correct prompt format
  - OpenAI receives correct messages format
  - Anthropic receives correct messages format

**TASK-11: Integration testing Phase 2**
- Complexity: Moderate
- Time: 4-6 hours
- Dependencies: TASK-6, TASK-7, TASK-8, TASK-9, TASK-10
- Description: Test all provider combinations
- Deliverables:
  - Test matrix of provider combinations
  - Test provider switching
  - Test fallback behavior
  - Document performance differences
- Acceptance Criteria:
  - All provider combinations work
  - No regressions from Phase 1
  - Performance acceptable for each combination
  - Errors handled gracefully

---

**Phase 3: Polish & Optimization (4 tasks)**

**TASK-12: Improve error handling and logging**
- Complexity: Simple
- Time: 3-4 hours
- Dependencies: TASK-11
- Description: Better error messages and debugging
- Deliverables:
  - Better error messages for each provider
  - Structured logging with levels
  - Debug mode with verbose output
- Acceptance Criteria:
  - Errors are clear and actionable
  - Logs help debug issues
  - Debug mode shows all details

**TASK-13: Optimize VAD parameters**
- Complexity: Simple
- Time: 2-3 hours
- Dependencies: TASK-11
- Description: Tune VAD for better detection
- Deliverables:
  - Test different energy thresholds
  - Test different timeout values
  - Document recommended settings
- Acceptance Criteria:
  - VAD works reliably in normal conditions
  - False positives minimized
  - False negatives minimized

**TASK-14: Create .env.example and update README**
- Complexity: Simple
- Time: 2-3 hours
- Dependencies: TASK-11
- Description: Documentation for users
- Deliverables:
  - .env.example with all API keys
  - README with setup instructions
  - README with provider comparison
  - README with troubleshooting
- Acceptance Criteria:
  - Users can set up from scratch
  - Provider options clearly explained
  - Common issues documented

**TASK-15: Final testing and validation**
- Complexity: Moderate
- Time: 4-6 hours
- Dependencies: TASK-12, TASK-13, TASK-14
- Description: Complete end-to-end validation
- Deliverables:
  - Test all features
  - Test all error conditions
  - Performance testing
  - Long-running stability test
- Acceptance Criteria:
  - All features work as specified
  - No memory leaks
  - Stable for extended use
  - Ready for production

---

### 12.2 Task Summary

**Total Tasks:** 15 (reduced from 23 in previous design)

**By Phase:**
- Phase 1 (Core): 5 tasks, ~1 week
- Phase 2 (Providers): 6 tasks, ~1 week
- Phase 3 (Polish): 4 tasks, ~1 week

**By Complexity:**
- Simple: 8 tasks
- Moderate: 7 tasks
- Complex: 0 tasks

**Total Estimated Time:** 2-3 weeks (reduced from 4-5 weeks)

---

## 13. Provider Comparison Matrices

### 13.1 LLM Providers

| Feature              | Ollama (granite3.2:2b) | OpenAI (gpt-4o-mini) | Anthropic (haiku) |
|----------------------|------------------------|----------------------|-------------------|
| **Latency**          | 2-5s                   | 0.5-1s               | 0.5-1s            |
| **Quality**          | Good                   | Excellent            | Excellent         |
| **Cost**             | Free                   | $0.15/1M tokens      | $0.25/1M tokens   |
| **Privacy**          | Complete (local)       | Data sent to cloud   | Data sent to cloud|
| **Offline**          | Yes                    | No                   | No                |
| **Pi Deployment**    | Yes                    | No (needs internet)  | No (needs internet)|
| **Best For**         | Privacy, offline       | Speed, quality       | Conversation      |

**Recommendation:**
- **Home use:** Ollama (privacy, no cost)
- **Commercial:** OpenAI (best speed/cost ratio)
- **High quality:** Anthropic (best conversation)

### 13.2 STT Providers

| Feature              | Vosk                   | Whisper (base)       | Deepgram          |
|----------------------|------------------------|----------------------|-------------------|
| **Latency**          | 1-3s                   | 2-5s                 | 0.3-1s            |
| **Accuracy**         | Good                   | Excellent            | Excellent         |
| **Cost**             | Free                   | Free (local)         | $0.0043/min       |
| **Privacy**          | Complete (local)       | Complete (local)     | Data sent to cloud|
| **Offline**          | Yes                    | Yes                  | No                |
| **Pi Deployment**    | Yes                    | Yes (slow)           | No (needs internet)|
| **Languages**        | 20+                    | 99+                  | 30+               |
| **Best For**         | Default, privacy       | Accuracy, multilang  | Speed, real-time  |

**Recommendation:**
- **Default:** Vosk (good enough for most use)
- **High accuracy needed:** Whisper (still offline)
- **Lowest latency:** Deepgram (cloud)

### 13.3 TTS Providers

| Feature              | Orca                   | Piper                | OpenAI TTS        |
|----------------------|------------------------|----------------------|-------------------|
| **Latency**          | ~1s                    | ~1s                  | 0.5-1s            |
| **Quality**          | Good                   | Good                 | Excellent         |
| **Cost**             | $1.99/month            | Free                 | $15/1M chars      |
| **Privacy**          | Local                  | Complete (local)     | Data sent to cloud|
| **Offline**          | Yes                    | Yes                  | No                |
| **Pi Deployment**    | Yes                    | Yes                  | No (needs internet)|
| **Voices**           | Limited                | Many voices          | 6 high-quality    |
| **Best For**         | Current default        | Free alternative     | Best quality      |

**Recommendation:**
- **Default:** Orca (current setup, good quality)
- **Free:** Piper (when cost matters)
- **Best quality:** OpenAI (commercial deployments)

---

## 14. Deployment

### 14.1 Raspberry Pi 5 Setup

**Install system dependencies:**

```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install Python and audio
sudo apt-get install -y python3 python3-pip python3-venv
sudo apt-get install -y portaudio19-dev python3-pyaudio

# Install Ollama (optional, for local LLM)
curl -fsSL https://ollama.com/install.sh | sh
ollama pull granite3.2:2b

# Install Piper (optional, for free TTS)
sudo apt-get install -y piper-tts
```

**Install Python dependencies:**

```bash
cd voice-assistant
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Configure providers:**

```bash
# Copy and edit .env
cp .env.example .env
nano .env

# Add API keys for cloud providers (if using)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
DEEPGRAM_API_KEY=...
```

**Run the assistant:**

```bash
python main.py
```

### 14.2 Provider Selection Guide

**Scenario 1: Full Privacy (All Local)**
```python
# config.py
LLM_PROVIDER = "ollama"
STT_PROVIDER = "vosk"
TTS_PROVIDER = "piper"  # or "orca"
```

**Scenario 2: Best Performance (Cloud)**
```python
# config.py
LLM_PROVIDER = "openai"
STT_PROVIDER = "deepgram"
TTS_PROVIDER = "openai"
```

**Scenario 3: Hybrid (Local STT/TTS, Cloud LLM)**
```python
# config.py
LLM_PROVIDER = "openai"  # Quality responses
STT_PROVIDER = "vosk"    # Privacy for audio
TTS_PROVIDER = "orca"    # Privacy for audio
```

---

## 15. Risks & Mitigations

### 15.1 Technical Risks

**Risk: Provider API changes break integration**
- Likelihood: Medium
- Impact: High
- Mitigation:
  - Pin dependency versions in requirements.txt
  - Test after any dependency update
  - Keep provider implementations simple and isolated

**Risk: VAD not accurate enough**
- Likelihood: Medium
- Impact: Medium
- Mitigation:
  - Make energy threshold configurable
  - Test in various environments
  - Document tuning process
  - Can improve later if needed

**Risk: Conversation history grows too large**
- Likelihood: Low
- Impact: Low
- Mitigation:
  - History pruning already implemented
  - MAX_HISTORY_TURNS limits size
  - Simple list structure is memory-efficient

**Risk: Network latency affects cloud providers**
- Likelihood: Medium
- Impact: Medium
- Mitigation:
  - Always have offline fallback (Ollama, Vosk, Orca/Piper)
  - Detect network errors and fail gracefully
  - Document performance requirements

### 15.2 Implementation Risks

**Risk: Scope creep (adding features)**
- Likelihood: High
- Impact: High
- Mitigation:
  - Stick to three phases
  - No new features until core works
  - Document future enhancements separately

**Risk: Over-engineering returns**
- Likelihood: Medium
- Impact: High
- Mitigation:
  - Review code for unnecessary abstraction
  - Keep functions simple
  - Resist urge to add "just in case" features

**Risk: Provider testing takes too long**
- Likelihood: Medium
- Impact: Medium
- Mitigation:
  - Test one provider at a time
  - Manual testing is OK for MVP
  - Automated tests can come later

---

## 16. Future Enhancements

**Potential improvements after MVP:**

1. **Streaming TTS** - Start speaking before full response generated
2. **Interrupt Detection** - Allow user to interrupt assistant
3. **Emotion Detection** - Adjust responses based on user tone
4. **Multi-language Support** - Switch languages dynamically
5. **Conversation Summarization** - Compress long conversations
6. **Session Persistence** - Resume conversations after restart
7. **Wake Word Customization** - Train custom wake words
8. **Voice Profiles** - Recognize different users
9. **Contextual Awareness** - Time, location, previous conversations
10. **Parallel Processing** - STT while TTS is speaking

**Do not implement these now** - Focus on core functionality first.

---

## 17. Success Criteria

**The implementation is successful if:**

1. **Core Functionality**
   - Wake word triggers conversation
   - Multi-turn conversation works without wake word
   - Timeout ends conversation naturally
   - Goodbye phrases end conversation
   - History maintained across turns

2. **Provider Flexibility**
   - Can switch LLM provider via config
   - Can switch STT provider via config
   - Can switch TTS provider via config
   - All 9 providers work correctly

3. **Code Quality**
   - Total new code ~400-500 lines
   - Clear, readable control flow
   - No unnecessary abstractions
   - Well-documented functions

4. **Performance**
   - Response latency <500ms for cloud providers
   - Response latency <5s for local providers
   - Memory usage <500MB
   - Stable for extended use

5. **Timeline**
   - Phase 1 complete in 1 week
   - Phase 2 complete in 2 weeks total
   - Phase 3 complete in 3 weeks total

---

## 18. Conclusion

This design represents a **balanced approach** to building a conversational voice assistant:

**What We Kept:**
- Provider abstractions for LLM, STT, and TTS (real flexibility need)
- 9 providers total (3 each) for realistic options
- Configuration-driven provider selection

**What We Simplified:**
- Two-loop structure instead of state machine classes
- Functions instead of manager classes
- Simple lists/dicts instead of complex dataclasses
- ~400-500 lines instead of 1500+ lines
- 2-3 weeks instead of 4-5 weeks

**What We Deleted:**
- StateMachineCoordinator class
- SessionManager class
- Message dataclass
- SessionMetrics tracking
- Complex state transition tables
- Unnecessary providers (Google TTS, ElevenLabs, Google STT)

**The Result:**
- Clear, maintainable code anyone can understand
- Flexible where it matters (provider selection)
- Simple where possible (control flow, data structures)
- Practical and achievable in reasonable time
- Room to add features later without refactoring

**Next Steps:**
1. Review this design
2. Start Phase 1 implementation
3. Test core conversation loop
4. Add provider abstractions
5. Polish and deploy

This design is **ready for implementation**. The code will be simple, practical, and maintainable while providing the flexibility needed for different deployment scenarios.
