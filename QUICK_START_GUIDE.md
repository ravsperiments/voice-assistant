# Quick Start Guide for Implementation

**Quick reference for starting development immediately**

---

## Start Development in 5 Minutes

### 1. Review Design Document
```bash
# Read the design document first
cat DESIGN_CONVERSATIONAL_SYSTEM.md

# Key sections to understand:
# - Section 3: System Architecture (two-loop structure)
# - Section 4: Component Specifications
# - Section 12: Task Breakdown
```

### 2. Review Implementation Plan
```bash
# Complete GitHub-ready issues
cat IMPLEMENTATION_PLAN.md

# What you'll find:
# - 18 detailed GitHub issues ready to copy-paste
# - Acceptance criteria for each task
# - Testing instructions
# - Implementation notes
```

### 3. Check Task Dependencies
```bash
# Visual dependency graph
cat DEPENDENCY_GRAPH.md

# Understand:
# - What can be done in parallel
# - What blocks what
# - Critical path
```

### 4. Start with Phase 1, Task 1
```bash
# Create conversation.py module
# No dependencies - can start immediately!

# See Issue #1 in IMPLEMENTATION_PLAN.md for details
```

---

## What to Build First (Week 1)

### Day 1-2: Foundation (Parallel Work)

**TASK-001: Create conversation.py**
```bash
# Create file
touch components/conversation.py

# Implement functions:
# - add_user_message(text: str)
# - add_assistant_message(text: str)
# - clear_history()
# - get_history()
# - format_for_llm(provider: str)
# - is_conversation_ending()
# - _prune_history()

# Test in Python REPL:
python3
>>> from components.conversation import *
>>> add_user_message("Hello")
>>> add_assistant_message("Hi there!")
>>> get_history()
```

**TASK-002: Add VAD to stt.py**
```bash
# Edit existing file
nano components/stt.py

# Add function:
# def has_voice_activity(timeout_seconds: float = 10.0) -> bool:
#     # Energy-based VAD
#     # Return True if voice detected, False on timeout

# Test:
>>> from components.stt import has_voice_activity
>>> has_voice_activity(5.0)  # Speak within 5 seconds
True
```

**TASK-003: Update config.py**
```bash
# Edit config
nano config.py

# Add settings:
MAX_HISTORY_TURNS = 10
AWAITING_TIMEOUT = 10.0
MAX_RESPONSE_TOKENS = 100
VAD_ENERGY_THRESHOLD = 500
```

### Day 3-4: Main Loop

**TASK-004: Create new main.py**
```bash
# Backup existing
cp main.py main_old.py

# Create new main.py with two-loop structure
nano main.py

# Structure:
# while True:
#     wait_for_wake_word()
#     clear_history()
#     speak_text("Hello!")
#
#     while conversation_active:
#         user_text = transcribe_audio()
#         add_user_message(user_text)
#
#         response = generate_response(...)
#         add_assistant_message(response)
#
#         speak_text(response)
#
#         if is_conversation_ending(): break
#         if not has_voice_activity(): break
```

### Day 5: Test Everything

**TASK-005: Integration Testing**
```bash
# Run the assistant
python main.py

# Test scenarios:
# 1. Wake word → question → answer → timeout
# 2. Wake word → 5 turns → goodbye
# 3. Wake word → silence → timeout
```

---

## Code Snippets to Get Started

### conversation.py Template

```python
"""Conversation history management - simple and practical."""

from typing import List, Dict
import config

# Global conversation history
conversation_history: List[Dict[str, str]] = []

def add_user_message(text: str) -> None:
    """Add user message to history."""
    conversation_history.append({"role": "user", "content": text})
    _prune_history()

def add_assistant_message(text: str) -> None:
    """Add assistant message to history."""
    conversation_history.append({"role": "assistant", "content": text})
    _prune_history()

def clear_history() -> None:
    """Clear conversation history."""
    conversation_history.clear()

def get_history() -> List[Dict[str, str]]:
    """Get current conversation history."""
    return conversation_history.copy()

def format_for_llm(provider: str) -> str:
    """Format conversation history for LLM provider."""
    if provider == "ollama":
        return _format_ollama_prompt()
    else:
        raise ValueError(f"Unknown provider: {provider}")

def is_conversation_ending() -> bool:
    """Detect if conversation should end."""
    if not conversation_history:
        return False

    last_message = conversation_history[-1]["content"].lower()
    ending_phrases = [
        "goodbye", "bye", "see you", "that's all",
        "nevermind", "stop", "quit", "exit"
    ]
    return any(phrase in last_message for phrase in ending_phrases)

def _prune_history() -> None:
    """Limit history to last N turns."""
    max_messages = config.MAX_HISTORY_TURNS * 2
    if len(conversation_history) > max_messages:
        conversation_history[:] = conversation_history[-max_messages:]

def _format_ollama_prompt() -> str:
    """Format history as Ollama prompt string."""
    prompt = "You are a helpful voice assistant. Keep responses brief (1-2 sentences).\n\n"

    for msg in conversation_history:
        role = msg["role"].capitalize()
        content = msg["content"]
        prompt += f"{role}: {content}\n"

    prompt += "Assistant:"
    return prompt
```

### VAD Function Template (add to stt.py)

```python
import time
import numpy as np
import pyaudio
import config

def has_voice_activity(timeout_seconds: float = 10.0) -> bool:
    """Simple VAD to detect if user is speaking.

    Args:
        timeout_seconds: How long to wait for speech

    Returns:
        True if voice detected within timeout, False otherwise
    """
    # Initialize audio stream
    audio = pyaudio.PyAudio()
    stream = audio.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=16000,
        input=True,
        frames_per_buffer=512
    )

    start_time = time.time()
    threshold = config.VAD_ENERGY_THRESHOLD

    try:
        while time.time() - start_time < timeout_seconds:
            # Read audio frame
            audio_data = stream.read(512, exception_on_overflow=False)

            # Calculate energy
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            energy = np.abs(audio_array).mean()

            # Check if above threshold
            if energy > threshold:
                print(f"Voice detected! Energy: {energy}")
                return True

            time.sleep(0.1)

        print(f"Timeout - no voice detected")
        return False

    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()
```

### Main Loop Template (new main.py)

```python
"""Main conversation loop - simple two-loop structure."""

import logging
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
import config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main conversation loop."""
    logger.info("Voice assistant starting...")

    try:
        while True:
            # OUTER LOOP: Wait for wake word
            logger.info("Listening for wake word...")
            wait_for_wake_word()
            logger.info("Wake word detected!")

            # Start new conversation
            clear_history()
            speak_text("Hello! How can I help?")

            conversation_active = True
            turn_count = 0

            # INNER LOOP: Conversation turns
            while conversation_active:
                turn_count += 1
                logger.info(f"Turn {turn_count}")

                # 1. Listen for user
                logger.info("Listening...")
                user_text = transcribe_audio()

                if not user_text:
                    logger.info("No speech detected")
                    break

                logger.info(f"User: {user_text}")
                add_user_message(user_text)

                # 2. Generate response
                try:
                    prompt = format_for_llm("ollama")  # Use default provider
                    response = generate_response(prompt)
                    logger.info(f"Assistant: {response}")
                    add_assistant_message(response)
                except Exception as e:
                    logger.error(f"Error: {e}")
                    response = "Sorry, I'm having trouble right now."
                    add_assistant_message(response)

                # 3. Speak response
                speak_text(response)

                # 4. Check if should end
                if is_conversation_ending():
                    logger.info("Goodbye detected")
                    break

                # 5. Wait for next turn
                logger.info(f"Waiting for next turn (timeout: {config.AWAITING_TIMEOUT}s)")
                if not has_voice_activity(timeout=config.AWAITING_TIMEOUT):
                    logger.info("Timeout")
                    break

            # Conversation ended
            logger.info(f"Conversation ended after {turn_count} turns")
            speak_text("Goodbye!")

    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)

if __name__ == "__main__":
    main()
```

---

## Testing Commands

### Test conversation.py
```python
python3 -c "
from components.conversation import *
add_user_message('Hello')
add_assistant_message('Hi there!')
add_user_message('How are you?')
print(get_history())
print(format_for_llm('ollama'))
print('Ending:', is_conversation_ending())
add_user_message('goodbye')
print('Ending:', is_conversation_ending())
"
```

### Test VAD
```python
python3 -c "
from components.stt import has_voice_activity
print('Speak now...')
result = has_voice_activity(5.0)
print('Voice detected:', result)
"
```

### Test main loop
```bash
# Run the assistant
python main.py

# Expected output:
# Voice assistant starting...
# Listening for wake word...
# (say wake word)
# Wake word detected!
# Hello! How can I help?
# Turn 1
# Listening...
# (speak)
# User: [your speech]
# Assistant: [response]
# (response spoken)
# Waiting for next turn...
```

---

## Common Issues & Fixes

### Issue: ModuleNotFoundError
```bash
# Make sure you're in the right directory
cd /Users/ravi/Documents/Projects/voice-assistant

# Verify Python can find modules
python3 -c "import sys; print(sys.path)"

# If components not found, check __init__.py exists
touch components/__init__.py
```

### Issue: VAD always returns False
```python
# Check threshold setting
python3 -c "import config; print(config.VAD_ENERGY_THRESHOLD)"

# Test with lower threshold
# Edit config.py: VAD_ENERGY_THRESHOLD = 300

# Or test with debug output
# Add print statements in has_voice_activity() to see energy levels
```

### Issue: Conversation history not working
```python
# Test directly
python3 -c "
from components import conversation
print('Initial:', conversation.conversation_history)
conversation.add_user_message('test')
print('After add:', conversation.conversation_history)
"
```

---

## Progress Checklist

### Week 1
- [ ] Day 1: TASK-001 (conversation.py) complete
- [ ] Day 2: TASK-002 (VAD) + TASK-003 (config) complete
- [ ] Day 3-4: TASK-004 (main.py) complete
- [ ] Day 5: TASK-005 (testing) complete
- [ ] ✓ Milestone 1: Multi-turn conversations working!

### Week 2
- [ ] Day 1-3: TASK-006, 007, 008 (provider routing) complete
- [ ] Day 4: TASK-009, 010, 011 complete
- [ ] Day 5: TASK-012 (Phase 2 testing) complete
- [ ] ✓ Milestone 2: Provider flexibility working!

### Week 3
- [ ] Day 1-2: TASK-013, 014, 015 complete
- [ ] Day 3-4: TASK-016, 017 complete
- [ ] Day 5: TASK-018 (final testing) complete
- [ ] ✓ Milestone 3: Production ready!

---

## Next Steps After Phase 1

Once Phase 1 is working:

1. **Test thoroughly** - Don't rush to Phase 2
2. **Document any issues** found during testing
3. **Measure performance** - latency, memory usage
4. **Demo to stakeholders** - get feedback
5. **Plan Phase 2** - which providers to prioritize

**Remember:** A working Phase 1 is better than a broken Phase 2!

---

## Getting Help

### Design Questions
- Reference: `DESIGN_CONVERSATIONAL_SYSTEM.md`
- Especially Section 4 (Component Specifications)

### Implementation Questions
- Reference: `IMPLEMENTATION_PLAN.md`
- Check "Implementation Notes" section of each issue

### Dependency Questions
- Reference: `DEPENDENCY_GRAPH.md`
- Check "Blocking Dependencies" section

### Task Questions
- Reference: `tasks.md`
- Shows all tasks with acceptance criteria

---

## Development Tips

1. **Start simple** - Get Phase 1 working before adding complexity
2. **Test incrementally** - Don't write all code then test
3. **Use logging** - Add print/log statements liberally
4. **Commit often** - Commit after each task completion
5. **Document issues** - Note any problems for later fixing
6. **Take breaks** - Complex conversation logic needs fresh eyes

---

**Ready to start? Begin with TASK-001 (conversation.py)!**

Open `IMPLEMENTATION_PLAN.md` and copy Issue #1 to GitHub, or start coding directly using the template above.

Good luck! 🚀
