# Voice Assistant Implementation Plan

**Project:** Conversational Voice Assistant System
**Version:** 2.0 (Simplified Architecture)
**Target:** Raspberry Pi 5
**Timeline:** 2-3 weeks
**Total Issues:** 18

---

## Table of Contents

1. [Overview](#overview)
2. [Epic Breakdown](#epic-breakdown)
3. [Dependency Graph](#dependency-graph)
4. [Timeline & Milestones](#timeline--milestones)
5. [Risk Assessment](#risk-assessment)
6. [GitHub Issues](#github-issues)

---

## Overview

This implementation plan evolves the existing single-turn voice assistant into a multi-turn conversational system using a simplified architecture based on the design document (`DESIGN_CONVERSATIONAL_SYSTEM.md`).

**Current State:**
- Simple single-turn: wake word → listen → respond → repeat
- Using: Ollama (LLM), Vosk (STT), Orca (TTS)
- Files: main.py (27 lines), wake_word.py, stt.py, llm.py, tts.py

**Target State:**
- Multi-turn conversations without wake word repetition
- Provider flexibility (9 providers: 3 LLM, 3 STT, 3 TTS)
- Simple two-loop architecture
- ~400-500 lines of new code

**Key Principles:**
- **Simple over complex**: Two-loop structure instead of state machines
- **Functions over classes**: Minimal abstraction, maximum clarity
- **Flexible where needed**: Provider abstractions for LLM/STT/TTS switching

---

## Epic Breakdown

### Epic 1: Core Conversation Loop (Phase 1)
**Objective:** Enable multi-turn conversations with simple history management and voice activity detection
**Success Criteria:** Users can have multi-turn conversations after wake word, ending with timeout or goodbye phrase
**Estimated Effort:** 1 week (5 issues)
**Milestone:** Phase 1 - Core Conversation
**Priority:** P0 (Critical for MVP)

**Stories:**
- Story 1.1: Conversation history management
- Story 1.2: Voice activity detection
- Story 1.3: Two-loop conversation flow

### Epic 2: Provider Abstractions (Phase 2)
**Objective:** Add provider flexibility for LLM, STT, and TTS components
**Success Criteria:** Can switch between 9 providers (3 each) via configuration without code changes
**Estimated Effort:** 1 week (7 issues)
**Milestone:** Phase 2 - Provider Flexibility
**Priority:** P1 (High importance)

**Stories:**
- Story 2.1: LLM provider abstraction (Ollama, OpenAI, Anthropic)
- Story 2.2: STT provider abstraction (Vosk, Whisper, Deepgram)
- Story 2.3: TTS provider abstraction (Orca, Piper, OpenAI)
- Story 2.4: Configuration management

### Epic 3: Polish & Production Ready (Phase 3)
**Objective:** Production readiness with error handling, documentation, and validation
**Success Criteria:** System is stable, well-documented, and ready for deployment
**Estimated Effort:** 1 week (6 issues)
**Milestone:** Phase 3 - Production Ready
**Priority:** P1 (High importance)

**Stories:**
- Story 3.1: Error handling & logging
- Story 3.2: Configuration & documentation
- Story 3.3: Testing & validation

---

## Dependency Graph

```
Phase 1: Core Conversation Loop
├─ Issue #1: Create conversation.py module [No dependencies]
├─ Issue #2: Implement VAD in stt.py [No dependencies]
├─ Issue #3: Update config.py (Phase 1) [No dependencies]
├─ Issue #4: Create main.py conversation loop [Depends on: #1, #2, #3]
└─ Issue #5: Integration testing Phase 1 [Depends on: #4]

Phase 2: Provider Abstractions
├─ Issue #6: Add LLM provider routing [Depends on: #5]
├─ Issue #7: Add STT provider routing [Depends on: #5]
├─ Issue #8: Add TTS provider routing [Depends on: #5]
├─ Issue #9: Update conversation.py formatting [Depends on: #6]
├─ Issue #10: Update config.py (Phase 2) [Depends on: #6, #7, #8]
├─ Issue #11: Add requirements.txt dependencies [No dependencies]
└─ Issue #12: Integration testing Phase 2 [Depends on: #6, #7, #8, #9, #10, #11]

Phase 3: Polish & Production
├─ Issue #13: Improve error handling & logging [Depends on: #12]
├─ Issue #14: Optimize VAD parameters [Depends on: #12]
├─ Issue #15: Create .env.example [Depends on: #10]
├─ Issue #16: Update README documentation [Depends on: #12]
├─ Issue #17: Create provider comparison guide [Depends on: #12]
└─ Issue #18: Final testing & validation [Depends on: #13, #14, #15, #16, #17]
```

---

## Timeline & Milestones

### Week 1: Phase 1 - Core Conversation Loop
- **Days 1-2:** Issues #1, #2, #3 (parallel development)
- **Days 3-4:** Issue #4 (main conversation loop)
- **Day 5:** Issue #5 (integration testing)
- **Deliverable:** Working multi-turn conversation with default providers

### Week 2: Phase 2 - Provider Abstractions
- **Days 1-3:** Issues #6, #7, #8 (parallel development)
- **Day 4:** Issues #9, #10, #11
- **Day 5:** Issue #12 (integration testing)
- **Deliverable:** Full provider flexibility via configuration

### Week 3: Phase 3 - Polish & Production Ready
- **Days 1-2:** Issues #13, #14 (improvements)
- **Days 3-4:** Issues #15, #16, #17 (documentation)
- **Day 5:** Issue #18 (final validation)
- **Deliverable:** Production-ready system

---

## Risk Assessment

### Epic 1: Core Conversation Loop
**Risks:**
- VAD accuracy may not be sufficient → **Mitigation:** Make energy threshold configurable, test in various environments
- Conversation ending detection may miss edge cases → **Mitigation:** Start with common phrases, can expand list later

**Confidence Level:** High (straightforward implementation)

### Epic 2: Provider Abstractions
**Risks:**
- API changes from cloud providers → **Mitigation:** Pin dependency versions, isolate provider implementations
- Network latency affects cloud providers → **Mitigation:** Always have offline fallback
- API key costs for testing → **Mitigation:** Test locally first, minimal cloud testing

**Confidence Level:** Medium (external dependencies)

### Epic 3: Polish & Production
**Risks:**
- Scope creep (adding features) → **Mitigation:** Stick to documented tasks, defer enhancements
- Testing all provider combinations takes time → **Mitigation:** Prioritize common combinations, manual testing acceptable

**Confidence Level:** High (polish work)

---

## GitHub Issues

All issues below are formatted for direct copy-paste into GitHub Issues.

---

# PHASE 1: CORE CONVERSATION LOOP

---

### Issue #1: Create conversation.py module

**Epic:** Core Conversation Loop
**Story:** Conversation history management
**Labels:** `epic:core-conversation`, `type:feature`, `P0:critical`, `component:conversation`
**Estimate:** 2-3 hours
**Dependencies:** None
**Milestone:** Phase 1 - Core Conversation

**Description:**

Create a new `components/conversation.py` module to manage conversation history as a simple list of dictionaries. This module will track user and assistant messages, limit history size, detect conversation endings, and format history for LLM consumption.

**Tasks:**
- [ ] Create `components/conversation.py` file
- [ ] Implement global `conversation_history` list
- [ ] Add `add_user_message(text: str)` function
- [ ] Add `add_assistant_message(text: str)` function
- [ ] Add `clear_history()` function
- [ ] Add `get_history()` function returning list copy
- [ ] Add `_prune_history()` internal function for size limiting
- [ ] Add `is_conversation_ending()` function for goodbye detection
- [ ] Add `format_for_llm(provider: str)` function (Ollama format only for Phase 1)
- [ ] Add docstrings for all functions

**Acceptance Criteria:**
- [ ] Module exists at `components/conversation.py`
- [ ] All functions implemented and documented
- [ ] History stored as list of `{"role": str, "content": str}` dicts
- [ ] Can add user and assistant messages
- [ ] Clear function empties the list
- [ ] History automatically pruned to MAX_HISTORY_TURNS (10 turns = 20 messages)
- [ ] Goodbye phrases detected: "goodbye", "bye", "see you", "that's all", "nevermind", "stop", "quit", "exit"
- [ ] Ollama prompt format includes system message and conversation history

**Files to Create:**
- `components/conversation.py`

**Testing:**
Manual testing:
1. Import module in Python REPL
2. Add user message, verify in history
3. Add assistant message, verify in history
4. Add 25 messages, verify only last 20 kept
5. Add goodbye message, verify ending detected
6. Call format_for_llm, verify Ollama prompt format correct

**Implementation Notes:**
- Use simple list of dicts, no dataclasses
- Pruning should preserve last N exchanges (user+assistant pairs)
- Ending detection checks last message content (case-insensitive)
- Ollama format: system prompt + "User: ...\nAssistant: ...\nUser: ...\nAssistant:"

---

### Issue #2: Implement voice activity detection in stt.py

**Epic:** Core Conversation Loop
**Story:** Voice activity detection
**Labels:** `epic:core-conversation`, `type:feature`, `P0:critical`, `component:stt`
**Estimate:** 2-3 hours
**Dependencies:** None
**Milestone:** Phase 1 - Core Conversation

**Description:**

Add a simple energy-based Voice Activity Detection (VAD) function to `components/stt.py` to detect when the user is speaking vs. silence. This enables the conversation loop to wait for the next user turn with a timeout.

**Tasks:**
- [ ] Add `has_voice_activity(timeout_seconds: float = 10.0) -> bool` function to `stt.py`
- [ ] Implement energy-based VAD using numpy and PyAudio
- [ ] Use configurable `VAD_ENERGY_THRESHOLD` from config
- [ ] Read audio frames in chunks and calculate RMS energy
- [ ] Return True if energy exceeds threshold within timeout
- [ ] Return False if timeout expires without detecting voice
- [ ] Add appropriate logging for debugging

**Acceptance Criteria:**
- [ ] Function `has_voice_activity()` implemented in `stt.py`
- [ ] Detects voice activity when user speaks
- [ ] Returns False after timeout if no speech detected
- [ ] Energy threshold configurable via config.py
- [ ] Uses existing PyAudio stream setup
- [ ] Logging shows energy levels for debugging
- [ ] Works with timeout range 5-30 seconds

**Files to Modify:**
- `components/stt.py`

**Testing:**
Manual testing:
1. Call function with 10s timeout, speak within 5s → should return True
2. Call function with 5s timeout, stay silent → should return False after 5s
3. Adjust VAD_ENERGY_THRESHOLD, verify threshold affects detection
4. Test in quiet room vs. noisy environment

**Implementation Notes:**
- Use `np.frombuffer(audio_data, dtype=np.int16)` to convert audio
- Energy calculation: `np.abs(audio_array).mean()`
- Chunk size: 512 samples (existing constant)
- Sample rate: 16000 Hz (existing constant)
- Consider using same audio stream as transcribe_audio() if possible

---

### Issue #3: Update config.py with conversation settings

**Epic:** Core Conversation Loop
**Story:** Configuration management
**Labels:** `epic:core-conversation`, `type:feature`, `P0:critical`, `component:config`
**Estimate:** 1 hour
**Dependencies:** None
**Milestone:** Phase 1 - Core Conversation

**Description:**

Add conversation-related configuration settings to `config.py` for Phase 1. These settings control conversation history size, timeouts, and VAD parameters.

**Tasks:**
- [ ] Add `MAX_HISTORY_TURNS = 10` setting (last N user+assistant exchanges)
- [ ] Add `AWAITING_TIMEOUT = 10.0` setting (seconds to wait for next turn)
- [ ] Add `MAX_RESPONSE_TOKENS = 100` setting (~15-20 seconds of speech)
- [ ] Add `VAD_ENERGY_THRESHOLD = 500` setting (energy level for voice detection)
- [ ] Add comments explaining each setting
- [ ] Ensure settings work with existing _env() helper

**Acceptance Criteria:**
- [ ] All four settings added to config.py
- [ ] Settings have sensible defaults
- [ ] Each setting has explanatory comment
- [ ] Can override via environment variables if needed
- [ ] No breaking changes to existing config

**Files to Modify:**
- `config.py`

**Testing:**
1. Import config, verify all new settings exist
2. Verify default values match specification
3. Test environment variable override if applicable

**Implementation Notes:**
- Place new settings in a "Conversation Settings" section
- MAX_HISTORY_TURNS: 10 turns = 20 messages (10 user + 10 assistant)
- AWAITING_TIMEOUT: 10 seconds is good default, can be adjusted later
- MAX_RESPONSE_TOKENS: 100 tokens ≈ 60-80 words ≈ 15-20 sec TTS
- VAD_ENERGY_THRESHOLD: 500 is starting point, may need tuning

---

### Issue #4: Create main.py conversation loop

**Epic:** Core Conversation Loop
**Story:** Two-loop conversation flow
**Labels:** `epic:core-conversation`, `type:feature`, `P0:critical`, `component:conversation`
**Estimate:** 4-6 hours
**Dependencies:** #1, #2, #3
**Milestone:** Phase 1 - Core Conversation

**Description:**

Implement the new `main.py` with a simple two-loop structure: outer loop waits for wake word, inner loop handles conversation turns. This replaces the existing single-turn implementation.

**Tasks:**
- [ ] Backup existing `main.py` (create `main_old.py`)
- [ ] Create new `main.py` with two-loop structure
- [ ] Implement outer loop: wait for wake word → start conversation
- [ ] Implement inner loop: transcribe → generate → speak → check continuation
- [ ] Integrate conversation history functions
- [ ] Integrate VAD function for turn detection
- [ ] Add conversation ending detection (goodbye phrases)
- [ ] Add timeout handling (no voice activity)
- [ ] Add comprehensive logging at each step
- [ ] Add error handling with try/except blocks
- [ ] Add graceful shutdown on Ctrl+C

**Acceptance Criteria:**
- [ ] Wake word triggers new conversation
- [ ] Conversation history cleared at start of each conversation
- [ ] Initial greeting spoken after wake word
- [ ] Multiple turns work without wake word repetition
- [ ] Conversation ends on timeout (no voice detected)
- [ ] Conversation ends on goodbye phrase
- [ ] Farewell message spoken at end
- [ ] Returns to wake word listening after conversation
- [ ] Logging shows clear conversation flow
- [ ] Graceful handling of Ctrl+C
- [ ] Total code ~100-150 lines

**Files to Modify:**
- `main.py` (complete rewrite)

**Testing:**
End-to-end manual testing:
1. Start assistant → wake word → greeting spoken
2. Ask question → answer received → stay silent 10s → farewell + back to wake word
3. Wake word → ask question → answer → say "goodbye" → farewell + back to wake word
4. Wake word → multi-turn conversation (3-5 exchanges) → timeout → farewell
5. Wake word → no speech → timeout → farewell
6. Verify logging shows all steps clearly
7. Test Ctrl+C shutdown

**Implementation Notes:**
- Follow structure from design doc Section 3.3
- Outer loop: `while True:` wait for wake word
- Inner loop: `while conversation_active:` conversation turns
- Use existing components: wait_for_wake_word(), transcribe_audio(), generate_response(), speak_text()
- Add new imports: conversation functions, has_voice_activity()
- Log turn count, user input, assistant response
- Break conditions: timeout, ending detected, no speech, errors

---

### Issue #5: Integration testing for Phase 1

**Epic:** Core Conversation Loop
**Story:** Phase 1 validation
**Labels:** `epic:core-conversation`, `type:testing`, `P0:critical`
**Estimate:** 3-4 hours
**Dependencies:** #4
**Milestone:** Phase 1 - Core Conversation

**Description:**

Comprehensive integration testing of Phase 1 to ensure all conversation flows work correctly with the default providers (Ollama, Vosk, Orca).

**Tasks:**
- [ ] Test single-turn conversation (wake → ask → answer → timeout)
- [ ] Test multi-turn conversation (wake → 5 turns → timeout)
- [ ] Test goodbye phrase ending ("goodbye", "that's all", "stop")
- [ ] Test timeout behavior (10s silence)
- [ ] Test conversation history management (verify last N turns kept)
- [ ] Test history formatting for Ollama
- [ ] Test VAD sensitivity in quiet environment
- [ ] Test VAD sensitivity in noisy environment
- [ ] Test error handling (disconnect Ollama, verify graceful handling)
- [ ] Test memory stability (10+ conversations in a row)
- [ ] Document any issues found

**Acceptance Criteria:**
- [ ] All conversation flows work as expected
- [ ] No memory leaks after multiple conversations
- [ ] Graceful error handling when LLM unavailable
- [ ] VAD works reliably in normal conditions
- [ ] Conversation history correctly limited
- [ ] Logging provides useful debugging information
- [ ] Performance acceptable (response latency <5s for Ollama)
- [ ] Ready to proceed to Phase 2

**Files to Test:**
- `main.py`
- `components/conversation.py`
- `components/stt.py` (VAD function)

**Testing Checklist:**

**Conversation Flows:**
- [ ] Wake word → question → answer → 10s silence → "Goodbye!" → wake word mode
- [ ] Wake word → Q1 → A1 → Q2 → A2 → Q3 → A3 → timeout → farewell
- [ ] Wake word → question → answer → "goodbye" → farewell immediately
- [ ] Wake word → question → answer → "that's all" → farewell immediately
- [ ] Wake word → question → answer → "stop" → farewell immediately

**Edge Cases:**
- [ ] Wake word → silence (no speech) → timeout → farewell
- [ ] Wake word → 15 turn conversation → verify only last 10 in history
- [ ] Disconnect Ollama mid-conversation → graceful error message

**Performance:**
- [ ] Measure time from user speech end to response start (<5s)
- [ ] Run 10 conversations back-to-back → verify no memory growth

**Bugs/Issues:**
- Document any bugs found in this issue's comments for fixing

---

# PHASE 2: PROVIDER ABSTRACTIONS

---

### Issue #6: Add LLM provider routing to llm.py

**Epic:** Provider Abstractions
**Story:** LLM provider flexibility
**Labels:** `epic:provider-abstractions`, `type:feature`, `P1:high`, `component:llm`
**Estimate:** 4-6 hours
**Dependencies:** #5
**Milestone:** Phase 2 - Provider Flexibility

**Description:**

Refactor `components/llm.py` to support multiple LLM providers (Ollama, OpenAI, Anthropic) with a unified interface. Add provider routing based on configuration.

**Tasks:**
- [ ] Refactor existing code to `_call_ollama(prompt: str) -> str`
- [ ] Update `generate_response()` signature to accept provider parameter
- [ ] Add provider routing logic in `generate_response()`
- [ ] Implement `_call_openai(prompt: str) -> str` function
- [ ] Implement `_call_anthropic(prompt: str) -> str` function
- [ ] Add `_prompt_to_messages(prompt: str) -> List[Dict]` helper
- [ ] Add error handling for unknown providers
- [ ] Add error handling for connection errors
- [ ] Add error handling for API errors (invalid keys, etc.)
- [ ] Update imports (openai, anthropic SDKs)

**Acceptance Criteria:**
- [ ] Can call Ollama LLM (existing functionality preserved)
- [ ] Can call OpenAI LLM with valid API key
- [ ] Can call Anthropic LLM with valid API key
- [ ] Provider selected via config.LLM_PROVIDER
- [ ] Graceful error for unknown provider
- [ ] Graceful error for connection failures
- [ ] Graceful error for invalid API keys
- [ ] Response format consistent across all providers
- [ ] Ollama prompt format converted to messages for OpenAI/Anthropic
- [ ] Total additions ~100-150 lines

**Files to Modify:**
- `components/llm.py`

**Testing:**
1. Set LLM_PROVIDER="ollama" → test conversation → verify works
2. Set LLM_PROVIDER="openai", add OPENAI_API_KEY → test → verify works
3. Set LLM_PROVIDER="anthropic", add ANTHROPIC_API_KEY → test → verify works
4. Set LLM_PROVIDER="invalid" → verify error handling
5. Set valid provider but wrong API key → verify graceful error
6. Disconnect network → test cloud provider → verify error message

**Implementation Notes:**
- Use OpenAI SDK: `from openai import OpenAI`
- Use Anthropic SDK: `from anthropic import Anthropic`
- OpenAI model: `gpt-4o-mini` (config.OPENAI_MODEL_NAME)
- Anthropic model: `claude-3-5-haiku-20241022` (config.ANTHROPIC_MODEL_NAME)
- max_tokens: config.MAX_RESPONSE_TOKENS (100)
- temperature: 0.7 for all providers
- Convert Ollama prompt string to messages list for OpenAI/Anthropic
- Handle both streaming and non-streaming responses

---

### Issue #7: Add STT provider routing to stt.py

**Epic:** Provider Abstractions
**Story:** STT provider flexibility
**Labels:** `epic:provider-abstractions`, `type:feature`, `P1:high`, `component:stt`
**Estimate:** 4-6 hours
**Dependencies:** #5
**Milestone:** Phase 2 - Provider Flexibility

**Description:**

Refactor `components/stt.py` to support multiple STT providers (Vosk, Whisper, Deepgram) with a unified interface. Add provider routing based on configuration.

**Tasks:**
- [ ] Refactor existing code to `_transcribe_vosk() -> Optional[str]`
- [ ] Update `transcribe_audio()` signature to accept provider parameter
- [ ] Add provider routing logic in `transcribe_audio()`
- [ ] Implement `_transcribe_whisper() -> Optional[str]` function
- [ ] Implement `_transcribe_deepgram() -> Optional[str]` function
- [ ] Add `_record_to_file()` helper for Whisper (saves to temp WAV)
- [ ] Add `_record_to_buffer()` helper for Deepgram (in-memory buffer)
- [ ] Add error handling for unknown providers
- [ ] Add error handling for API errors
- [ ] Update imports (whisper, deepgram SDKs)

**Acceptance Criteria:**
- [ ] Can use Vosk STT (existing functionality preserved)
- [ ] Can use Whisper STT (local model)
- [ ] Can use Deepgram STT with valid API key
- [ ] Provider selected via config.STT_PROVIDER
- [ ] Graceful error for unknown provider
- [ ] Returns None on transcription failure
- [ ] Transcription quality acceptable for each provider
- [ ] Latency acceptable for each provider
- [ ] Total additions ~100-150 lines

**Files to Modify:**
- `components/stt.py`

**Testing:**
1. Set STT_PROVIDER="vosk" → test → verify works
2. Set STT_PROVIDER="whisper" → test → verify works (may be slow)
3. Set STT_PROVIDER="deepgram", add API key → test → verify works
4. Set STT_PROVIDER="invalid" → verify error handling
5. Compare transcription accuracy across providers
6. Measure latency for each provider

**Implementation Notes:**
- Whisper: Use openai-whisper library, model="base" for Pi
- Deepgram: Use deepgram-sdk, language="en-US"
- Vosk: Keep existing implementation
- Recording duration: 5-10 seconds max for single turn
- Detect silence to end recording (use VAD logic)
- Whisper model lazy loading (don't load until first use)
- Deepgram uses streaming or pre-recorded API

---

### Issue #8: Add TTS provider routing to tts.py

**Epic:** Provider Abstractions
**Story:** TTS provider flexibility
**Labels:** `epic:provider-abstractions`, `type:feature`, `P1:high`, `component:tts`
**Estimate:** 4-6 hours
**Dependencies:** #5
**Milestone:** Phase 2 - Provider Flexibility

**Description:**

Refactor `components/tts.py` to support multiple TTS providers (Orca, Piper, OpenAI) with a unified interface. Add provider routing based on configuration.

**Tasks:**
- [ ] Refactor existing code to `_speak_orca(text: str) -> bool`
- [ ] Update `speak_text()` signature to accept provider parameter
- [ ] Add provider routing logic in `speak_text()`
- [ ] Implement `_speak_piper(text: str) -> bool` function
- [ ] Implement `_speak_openai(text: str) -> bool` function
- [ ] Add `_play_audio_file(filepath: str)` helper (plays WAV/MP3)
- [ ] Add error handling for unknown providers
- [ ] Add error handling for TTS failures
- [ ] Update imports as needed

**Acceptance Criteria:**
- [ ] Can use Orca TTS (existing functionality preserved)
- [ ] Can use Piper TTS (local, free)
- [ ] Can use OpenAI TTS with valid API key
- [ ] Provider selected via config.TTS_PROVIDER
- [ ] Graceful error for unknown provider
- [ ] Returns False on TTS failure
- [ ] Audio quality acceptable for each provider
- [ ] Latency acceptable for each provider
- [ ] Total additions ~100-150 lines

**Files to Modify:**
- `components/tts.py`

**Testing:**
1. Set TTS_PROVIDER="orca" → test → verify works
2. Set TTS_PROVIDER="piper" → test → verify works (requires Piper installed)
3. Set TTS_PROVIDER="openai", add API key → test → verify works
4. Set TTS_PROVIDER="invalid" → verify error handling
5. Compare audio quality across providers
6. Measure latency for each provider

**Implementation Notes:**
- Piper: Call via subprocess, save to /tmp/piper_output.wav
- OpenAI: Use openai SDK audio.speech.create(), model="tts-1", voice from config
- Orca: Keep existing implementation
- Audio playback: Use PyAudio or subprocess (aplay/afplay)
- OpenAI saves to /tmp/openai_tts.mp3
- Cleanup temp files after playback

---

### Issue #9: Update conversation.py for multi-provider formatting

**Epic:** Provider Abstractions
**Story:** LLM provider flexibility
**Labels:** `epic:provider-abstractions`, `type:feature`, `P1:high`, `component:conversation`
**Estimate:** 2-3 hours
**Dependencies:** #6
**Milestone:** Phase 2 - Provider Flexibility

**Description:**

Update `format_for_llm()` in `components/conversation.py` to handle formatting for all LLM providers (Ollama, OpenAI, Anthropic). Ollama uses prompt strings, while OpenAI/Anthropic use messages lists.

**Tasks:**
- [ ] Update `format_for_llm(provider: str)` to handle "ollama", "openai", "anthropic"
- [ ] Keep existing Ollama prompt formatting (string)
- [ ] Return messages list directly for OpenAI/Anthropic
- [ ] Ensure messages include system message at start
- [ ] Add error handling for unknown provider
- [ ] Update docstring with format details

**Acceptance Criteria:**
- [ ] Ollama receives formatted prompt string (as before)
- [ ] OpenAI receives list of message dicts
- [ ] Anthropic receives list of message dicts
- [ ] System message included for all providers
- [ ] Conversation history correctly included
- [ ] Unknown provider raises ValueError
- [ ] Works correctly with conversation history pruning

**Files to Modify:**
- `components/conversation.py`

**Testing:**
1. Add conversation history → format_for_llm("ollama") → verify prompt string format
2. Add conversation history → format_for_llm("openai") → verify messages list format
3. Add conversation history → format_for_llm("anthropic") → verify messages list format
4. format_for_llm("invalid") → verify ValueError raised

**Implementation Notes:**
- Ollama format (existing): "You are...\n\nUser: ...\nAssistant: ...\nUser: ...\nAssistant:"
- OpenAI/Anthropic format: `[{"role": "system", "content": "..."}, {"role": "user", "content": "..."}, ...]`
- System message: "You are a helpful voice assistant. Keep responses brief (1-2 sentences)."
- Return conversation_history directly for OpenAI/Anthropic (already in correct format)
- llm.py will handle conversion if needed

---

### Issue #10: Update config.py with all provider settings

**Epic:** Provider Abstractions
**Story:** Configuration management
**Labels:** `epic:provider-abstractions`, `type:feature`, `P1:high`, `component:config`
**Estimate:** 2-3 hours
**Dependencies:** #6, #7, #8
**Milestone:** Phase 2 - Provider Flexibility

**Description:**

Add all provider selection and provider-specific configuration settings to `config.py`. This includes API keys, model names, and provider-specific parameters.

**Tasks:**
- [ ] Add provider selection settings (LLM_PROVIDER, STT_PROVIDER, TTS_PROVIDER)
- [ ] Add OpenAI settings (API key, model name)
- [ ] Add Anthropic settings (API key, model name)
- [ ] Add Whisper settings (model size)
- [ ] Add Deepgram settings (API key)
- [ ] Add Piper settings (model path)
- [ ] Add OpenAI TTS settings (voice selection)
- [ ] Organize into sections with clear comments
- [ ] Use _env() helper for API keys
- [ ] Add validation or warnings for missing API keys

**Acceptance Criteria:**
- [ ] All provider selection settings added
- [ ] All provider-specific settings added
- [ ] API keys loaded from environment variables
- [ ] Sensible defaults for all settings
- [ ] Clear section organization
- [ ] Comments explain each setting
- [ ] No breaking changes to existing settings
- [ ] Total additions ~50 lines

**Files to Modify:**
- `config.py`

**Testing:**
1. Import config, verify all new settings exist
2. Test with .env file containing API keys
3. Test with missing API keys (should use defaults or None)
4. Verify provider switching by changing LLM_PROVIDER/STT_PROVIDER/TTS_PROVIDER

**Implementation Notes:**
- Section structure:
  - Provider Selection
  - LLM Provider Settings (Ollama, OpenAI, Anthropic)
  - STT Provider Settings (Vosk, Whisper, Deepgram)
  - TTS Provider Settings (Orca, Piper, OpenAI)
- Default providers: Ollama, Vosk, Orca (existing setup)
- API keys: Use _env() to load from environment
- Model names: Set sensible defaults

**Settings to Add:**
```python
# Provider Selection
LLM_PROVIDER = "ollama"  # ollama, openai, anthropic
STT_PROVIDER = "vosk"     # vosk, whisper, deepgram
TTS_PROVIDER = "orca"     # orca, piper, openai

# OpenAI
OPENAI_API_KEY = _env("OPENAI_API_KEY")
OPENAI_MODEL_NAME = "gpt-4o-mini"

# Anthropic
ANTHROPIC_API_KEY = _env("ANTHROPIC_API_KEY")
ANTHROPIC_MODEL_NAME = "claude-3-5-haiku-20241022"

# Whisper
WHISPER_MODEL = "base"  # tiny, base, small

# Deepgram
DEEPGRAM_API_KEY = _env("DEEPGRAM_API_KEY")

# Piper
PIPER_MODEL_PATH = "models/en_US-lessac-medium.onnx"

# OpenAI TTS
OPENAI_TTS_VOICE = "alloy"  # alloy, echo, fable, onyx, nova, shimmer
```

---

### Issue #11: Update requirements.txt with new dependencies

**Epic:** Provider Abstractions
**Story:** Dependency management
**Labels:** `epic:provider-abstractions`, `type:feature`, `P1:high`
**Estimate:** 1 hour
**Dependencies:** None
**Milestone:** Phase 2 - Provider Flexibility

**Description:**

Update `requirements.txt` to include all new dependencies for the additional LLM, STT, and TTS providers.

**Tasks:**
- [ ] Add OpenAI SDK: `openai>=1.12.0`
- [ ] Add Anthropic SDK: `anthropic>=0.18.0`
- [ ] Add Whisper: `openai-whisper>=20231117`
- [ ] Add Deepgram SDK: `deepgram-sdk>=3.0.0`
- [ ] Add python-dotenv: `python-dotenv>=1.0.0`
- [ ] Add numpy if not already present: `numpy>=1.24.0`
- [ ] Organize dependencies by category with comments
- [ ] Pin versions appropriately

**Acceptance Criteria:**
- [ ] All new dependencies added
- [ ] Version pins appropriate (not too strict, not too loose)
- [ ] File organized with comments
- [ ] Can `pip install -r requirements.txt` successfully
- [ ] No conflicts with existing dependencies

**Files to Modify:**
- `requirements.txt`

**Testing:**
1. Create fresh virtual environment
2. Run `pip install -r requirements.txt`
3. Verify all packages install successfully
4. Run `python -c "import openai, anthropic, whisper, deepgram"` to verify imports

**Implementation Notes:**
- Organize by category: Core, LLM, STT, TTS, Utilities
- Use `>=` for minor version flexibility
- Piper TTS installed via system package manager (apt), not pip
- Add comment about Piper installation

**Example Structure:**
```txt
# Core dependencies (existing)
pvporcupine==3.0.0
vosk==0.3.45
pyaudio==0.2.14
requests==2.31.0

# LLM providers
openai>=1.12.0
anthropic>=0.18.0

# STT providers
openai-whisper>=20231117
deepgram-sdk>=3.0.0

# TTS providers
# Piper: Install via system package manager (apt-get install piper-tts)
# OpenAI TTS included in openai package above

# Utilities
python-dotenv>=1.0.0
numpy>=1.24.0
```

---

### Issue #12: Integration testing for Phase 2

**Epic:** Provider Abstractions
**Story:** Phase 2 validation
**Labels:** `epic:provider-abstractions`, `type:testing`, `P1:high`
**Estimate:** 4-6 hours
**Dependencies:** #6, #7, #8, #9, #10, #11
**Milestone:** Phase 2 - Provider Flexibility

**Description:**

Comprehensive integration testing of all provider combinations to ensure flexibility works correctly. Test provider switching, error handling, and performance differences.

**Tasks:**
- [ ] Install all new dependencies (`pip install -r requirements.txt`)
- [ ] Set up .env file with all API keys
- [ ] Test LLM provider switching (Ollama, OpenAI, Anthropic)
- [ ] Test STT provider switching (Vosk, Whisper, Deepgram)
- [ ] Test TTS provider switching (Orca, Piper, OpenAI)
- [ ] Test key provider combinations (see test matrix below)
- [ ] Test error handling (invalid API keys, network errors)
- [ ] Test fallback behavior when cloud services unavailable
- [ ] Measure and document performance for each provider
- [ ] Document any issues or limitations found

**Acceptance Criteria:**
- [ ] All 9 providers work individually
- [ ] Can switch providers via config without code changes
- [ ] At least 4 provider combinations tested successfully
- [ ] Error handling works for invalid API keys
- [ ] Error handling works for network failures
- [ ] Performance documented for each provider
- [ ] No regressions from Phase 1
- [ ] Ready to proceed to Phase 3

**Files to Test:**
- All provider combinations

**Test Matrix:**

| Test | LLM      | STT      | TTS    | Expected Result              |
|------|----------|----------|--------|------------------------------|
| 1    | Ollama   | Vosk     | Orca   | Full offline mode works      |
| 2    | OpenAI   | Vosk     | Orca   | Cloud LLM + local STT/TTS    |
| 3    | Ollama   | Deepgram | Orca   | Cloud STT + local LLM/TTS    |
| 4    | OpenAI   | Deepgram | OpenAI | Full cloud mode works        |
| 5    | Anthropic| Vosk     | Orca   | Anthropic LLM + local        |
| 6    | Ollama   | Whisper  | Piper  | All free/local providers     |

**Error Handling Tests:**
- [ ] Invalid OPENAI_API_KEY → graceful error message
- [ ] Invalid ANTHROPIC_API_KEY → graceful error message
- [ ] Invalid DEEPGRAM_API_KEY → graceful error message
- [ ] Disconnect network during cloud provider call → graceful error
- [ ] Unknown provider name in config → clear error message

**Performance Documentation:**
For each provider, document:
- Transcription latency (STT)
- Response generation latency (LLM)
- Speech synthesis latency (TTS)
- Total end-to-end latency

**Testing Notes:**
- Some providers may not be available (no API key) - skip those tests
- Whisper may be very slow on Pi - document this
- Deepgram/OpenAI require internet - skip if offline
- Focus on most common combinations (Ollama+Vosk+Orca, OpenAI+Deepgram+OpenAI)

---

# PHASE 3: POLISH & PRODUCTION READY

---

### Issue #13: Improve error handling and logging

**Epic:** Polish & Production Ready
**Story:** Error handling & logging
**Labels:** `epic:polish`, `type:enhancement`, `P1:high`
**Estimate:** 3-4 hours
**Dependencies:** #12
**Milestone:** Phase 3 - Production Ready

**Description:**

Improve error handling and logging throughout the codebase to make debugging easier and provide better user feedback when things go wrong.

**Tasks:**
- [ ] Add structured logging with appropriate levels (INFO, WARNING, ERROR)
- [ ] Improve error messages in llm.py (provider-specific messages)
- [ ] Improve error messages in stt.py (microphone, transcription errors)
- [ ] Improve error messages in tts.py (audio playback errors)
- [ ] Add debug mode configuration (verbose logging)
- [ ] Add logging configuration in main.py
- [ ] Log provider selection at startup
- [ ] Log conversation metrics (turn count, duration)
- [ ] Add error recovery hints in error messages
- [ ] Ensure all exceptions are caught and logged appropriately

**Acceptance Criteria:**
- [ ] Logging uses appropriate levels throughout
- [ ] Error messages are clear and actionable
- [ ] Debug mode provides detailed logging
- [ ] Provider errors include recovery hints
- [ ] No uncaught exceptions crash the program
- [ ] Logs help diagnose issues quickly
- [ ] Performance impact of logging is minimal

**Files to Modify:**
- `main.py`
- `components/llm.py`
- `components/stt.py`
- `components/tts.py`
- `components/conversation.py`
- `config.py` (add DEBUG_MODE setting)

**Testing:**
1. Enable debug mode, run conversation, verify detailed logs
2. Trigger various errors, verify error messages are helpful
3. Test error recovery (e.g., LLM failure → user can retry)
4. Review logs for clarity and usefulness

**Implementation Notes:**
- Use Python's logging module
- Add DEBUG_MODE config setting (default False)
- Logging format: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
- Example error message: "OpenAI API error: Invalid API key. Please check OPENAI_API_KEY in .env file."
- Log conversation start/end, turn count, provider selection

---

### Issue #14: Optimize VAD parameters

**Epic:** Polish & Production Ready
**Story:** Voice activity detection tuning
**Labels:** `epic:polish`, `type:enhancement`, `P1:high`, `component:stt`
**Estimate:** 2-3 hours
**Dependencies:** #12
**Milestone:** Phase 3 - Production Ready

**Description:**

Tune Voice Activity Detection (VAD) parameters to minimize false positives and false negatives in various environments. Document recommended settings.

**Tasks:**
- [ ] Test VAD in quiet room, document optimal threshold
- [ ] Test VAD in noisy environment, document optimal threshold
- [ ] Test different timeout values (5s, 10s, 15s, 20s)
- [ ] Add adaptive threshold adjustment if needed
- [ ] Document recommended VAD_ENERGY_THRESHOLD range
- [ ] Document recommended AWAITING_TIMEOUT settings
- [ ] Add comments in config.py explaining tuning
- [ ] Consider adding calibration function (optional)

**Acceptance Criteria:**
- [ ] VAD works reliably in quiet environments
- [ ] VAD works acceptably in moderate noise
- [ ] False positives minimized (doesn't trigger on silence)
- [ ] False negatives minimized (doesn't miss user speech)
- [ ] Recommended settings documented
- [ ] Tuning process documented for users
- [ ] Performance acceptable (no lag)

**Files to Modify:**
- `config.py` (update VAD_ENERGY_THRESHOLD if needed)
- Documentation (add VAD tuning guide)

**Testing:**
1. Quiet room: Test thresholds 300, 500, 700, 1000
2. Noisy room (TV, music): Test same thresholds
3. For each threshold, test: silent pause, soft speech, normal speech, loud speech
4. Document results in table format
5. Determine optimal default threshold
6. Test timeout values: 5s, 10s, 15s - measure user experience

**Implementation Notes:**
- Energy calculation: RMS (root mean square) of audio samples
- Consider adding moving average for stability
- Threshold too low → false positives (noise triggers)
- Threshold too high → false negatives (misses soft speech)
- Current default: 500 (starting point)
- Typical range: 300-1000
- Optional: Add calibration function that measures background noise

---

### Issue #15: Create .env.example file

**Epic:** Polish & Production Ready
**Story:** Configuration & documentation
**Labels:** `epic:polish`, `type:docs`, `P1:high`
**Estimate:** 1 hour
**Dependencies:** #10
**Milestone:** Phase 3 - Production Ready

**Description:**

Create a `.env.example` file showing all available environment variables with placeholder values and helpful comments.

**Tasks:**
- [ ] Create `.env.example` file in project root
- [ ] Add all API key variables with placeholder values
- [ ] Add comments explaining each variable
- [ ] Add section for each provider
- [ ] Add notes about which keys are required vs. optional
- [ ] Add links to sign up for API keys
- [ ] Add example values where applicable

**Acceptance Criteria:**
- [ ] File exists at `.env.example`
- [ ] All API keys documented
- [ ] Clear comments for each variable
- [ ] Organized by provider
- [ ] Links to API key sign-up pages
- [ ] Instructions for creating .env file
- [ ] No actual API keys in example file

**Files to Create:**
- `.env.example`

**Testing:**
1. Copy .env.example to .env
2. Fill in actual values
3. Verify config.py loads values correctly
4. Verify assistant works with .env configuration

**Implementation Notes:**

Example content:
```bash
# Voice Assistant Environment Variables
# Copy this file to .env and fill in your actual API keys

# Picovoice (required for wake word detection)
PICOVOICE_ACCESS_KEY=your_picovoice_access_key_here
# Sign up at: https://console.picovoice.ai/

# OpenAI (optional - for GPT models and TTS)
OPENAI_API_KEY=sk-your_openai_api_key_here
# Sign up at: https://platform.openai.com/signup

# Anthropic (optional - for Claude models)
ANTHROPIC_API_KEY=sk-ant-your_anthropic_api_key_here
# Sign up at: https://console.anthropic.com/

# Deepgram (optional - for cloud STT)
DEEPGRAM_API_KEY=your_deepgram_api_key_here
# Sign up at: https://console.deepgram.com/

# Notes:
# - Required: PICOVOICE_ACCESS_KEY (for wake word)
# - Optional: Other keys only needed if using those specific providers
# - Default providers (Ollama, Vosk, Orca/Piper) work without API keys
```

---

### Issue #16: Update README documentation

**Epic:** Polish & Production Ready
**Story:** Configuration & documentation
**Labels:** `epic:polish`, `type:docs`, `P1:high`
**Estimate:** 3-4 hours
**Dependencies:** #12
**Milestone:** Phase 3 - Production Ready

**Description:**

Update the README.md file with complete setup instructions, usage guide, provider information, and troubleshooting tips.

**Tasks:**
- [ ] Add project overview and features
- [ ] Add architecture diagram or description
- [ ] Add complete setup instructions (dependencies, installation)
- [ ] Add configuration instructions (providers, .env file)
- [ ] Add usage instructions (running the assistant)
- [ ] Add provider comparison table
- [ ] Add troubleshooting section
- [ ] Add examples of conversations
- [ ] Add development/contribution guidelines
- [ ] Add license information

**Acceptance Criteria:**
- [ ] Users can set up from scratch following README
- [ ] Provider options clearly explained
- [ ] Configuration examples provided
- [ ] Common issues documented with solutions
- [ ] Code examples where helpful
- [ ] Clear, well-organized structure
- [ ] Links to relevant resources

**Files to Modify:**
- `README.md`

**Testing:**
1. Have someone unfamiliar with the project try to set it up using only the README
2. Verify all links work
3. Verify all commands are correct
4. Test on fresh Raspberry Pi if possible

**Implementation Notes:**

**README Structure:**
1. Title and Description
2. Features
3. Architecture Overview
4. Requirements
5. Installation
   - System dependencies
   - Python dependencies
   - Model downloads
   - Optional providers
6. Configuration
   - Provider selection
   - API keys setup
   - .env file
7. Usage
   - Running the assistant
   - Conversation examples
8. Provider Comparison
   - LLM providers
   - STT providers
   - TTS providers
9. Troubleshooting
   - Common issues
   - Audio device errors
   - Provider errors
10. Development
11. License

**Key Sections:**

**Installation Example:**
```bash
# Clone repository
git clone <repo-url>
cd voice-assistant

# Install system dependencies (Raspberry Pi)
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv portaudio19-dev

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Configure API keys
cp .env.example .env
nano .env  # Add your API keys
```

**Usage Example:**
```bash
# Activate virtual environment
source venv/bin/activate

# Run the assistant
python main.py

# Say wake word ("Jarvis"), then ask questions
# Have a multi-turn conversation
# Say "goodbye" to end conversation
```

---

### Issue #17: Create provider comparison guide

**Epic:** Polish & Production Ready
**Story:** Configuration & documentation
**Labels:** `epic:polish`, `type:docs`, `P2:nice-to-have`
**Estimate:** 2-3 hours
**Dependencies:** #12
**Milestone:** Phase 3 - Production Ready

**Description:**

Create a detailed provider comparison guide to help users choose the right providers for their use case. Include performance data, cost comparison, and recommendations.

**Tasks:**
- [ ] Create `PROVIDER_COMPARISON.md` file
- [ ] Document each LLM provider (features, cost, latency, quality)
- [ ] Document each STT provider (features, cost, latency, accuracy)
- [ ] Document each TTS provider (features, cost, latency, quality)
- [ ] Add performance comparison table with measured data
- [ ] Add cost comparison table
- [ ] Add use case recommendations
- [ ] Add provider switching examples
- [ ] Include links to provider documentation

**Acceptance Criteria:**
- [ ] All 9 providers documented
- [ ] Performance data from actual testing
- [ ] Cost estimates accurate
- [ ] Clear recommendations for different scenarios
- [ ] Examples of provider switching
- [ ] Well-organized and easy to navigate

**Files to Create:**
- `PROVIDER_COMPARISON.md`

**Testing:**
1. Verify all performance numbers match actual testing
2. Verify cost information is current
3. Test provider switching examples
4. Get feedback on clarity and usefulness

**Implementation Notes:**

**Structure:**
1. Introduction
2. LLM Providers
   - Ollama
   - OpenAI
   - Anthropic
3. STT Providers
   - Vosk
   - Whisper
   - Deepgram
4. TTS Providers
   - Orca
   - Piper
   - OpenAI
5. Performance Comparison
6. Cost Comparison
7. Use Case Recommendations
8. Switching Providers

**Use Case Recommendations:**

**Scenario: Full Privacy (All Local)**
```python
LLM_PROVIDER = "ollama"
STT_PROVIDER = "vosk"
TTS_PROVIDER = "piper"  # or "orca"
```
Best for: Home use, privacy-conscious users, offline operation

**Scenario: Best Performance (Cloud)**
```python
LLM_PROVIDER = "openai"
STT_PROVIDER = "deepgram"
TTS_PROVIDER = "openai"
```
Best for: Commercial deployments, best quality, low latency

**Scenario: Hybrid (Privacy + Quality)**
```python
LLM_PROVIDER = "openai"  # Quality responses
STT_PROVIDER = "vosk"    # Privacy for audio
TTS_PROVIDER = "orca"    # Privacy for audio
```
Best for: Good balance of quality and privacy

---

### Issue #18: Final testing and validation

**Epic:** Polish & Production Ready
**Story:** Final validation
**Labels:** `epic:polish`, `type:testing`, `P1:high`
**Estimate:** 4-6 hours
**Dependencies:** #13, #14, #15, #16, #17
**Milestone:** Phase 3 - Production Ready

**Description:**

Comprehensive final testing and validation of the complete system. Ensure all features work, documentation is accurate, and the system is production-ready.

**Tasks:**
- [ ] Test all conversation flows end-to-end
- [ ] Test all provider combinations (at least 6 combinations)
- [ ] Test all error conditions
- [ ] Performance testing (latency measurements)
- [ ] Stability testing (long-running session)
- [ ] Memory leak testing (monitor memory over time)
- [ ] Documentation validation (follow README from scratch)
- [ ] Code review (check for issues, TODOs, cleanup)
- [ ] Create release checklist
- [ ] Tag release version if applicable

**Acceptance Criteria:**
- [ ] All features work as specified
- [ ] All provider combinations tested successfully
- [ ] No critical bugs or issues
- [ ] Performance meets requirements (<5s local, <2s cloud)
- [ ] No memory leaks in 1-hour test
- [ ] Documentation complete and accurate
- [ ] Code is clean and well-commented
- [ ] Ready for production deployment

**Files to Test:**
- All files

**Testing Checklist:**

**Feature Testing:**
- [ ] Wake word detection
- [ ] Multi-turn conversation (5+ turns)
- [ ] Conversation timeout (10s silence)
- [ ] Goodbye phrase ending
- [ ] Conversation history management
- [ ] VAD (voice activity detection)
- [ ] All 9 providers individually

**Provider Combination Testing:**
- [ ] Ollama + Vosk + Orca (default)
- [ ] OpenAI + Vosk + Orca
- [ ] Ollama + Deepgram + Orca
- [ ] OpenAI + Deepgram + OpenAI
- [ ] Anthropic + Vosk + Orca
- [ ] Ollama + Whisper + Piper

**Error Testing:**
- [ ] Invalid API key handling
- [ ] Network disconnection handling
- [ ] Ollama service down
- [ ] Microphone unavailable
- [ ] Speaker unavailable
- [ ] Unknown provider in config

**Performance Testing:**
- [ ] Measure end-to-end latency for each provider combo
- [ ] Verify <500ms for cloud providers
- [ ] Verify <5s for local providers
- [ ] CPU usage acceptable (<30% average)
- [ ] Memory usage acceptable (<500MB)

**Stability Testing:**
- [ ] Run assistant for 1 hour continuously
- [ ] Monitor memory usage (should be stable, no growth)
- [ ] Complete 20+ conversations
- [ ] Verify no degradation over time

**Documentation Testing:**
- [ ] Follow README setup on fresh system
- [ ] Verify all links work
- [ ] Verify all commands are correct
- [ ] Test provider switching examples

**Code Quality:**
- [ ] Review all code for TODOs or FIXMEs
- [ ] Check for commented-out code
- [ ] Verify all functions have docstrings
- [ ] Check for consistent style
- [ ] Remove debug print statements

**Release Checklist:**
- [ ] All tests passing
- [ ] Documentation complete
- [ ] .env.example up to date
- [ ] requirements.txt accurate
- [ ] CHANGELOG.md updated (if exists)
- [ ] Git commits clean and organized
- [ ] Tag release version
- [ ] Create release notes

**Success Metrics:**
- Total new code: ~400-500 lines ✓
- Implementation time: 2-3 weeks ✓
- All 9 providers working ✓
- Multi-turn conversations working ✓
- Response latency targets met ✓
- Memory usage targets met ✓
- Production-ready ✓

---

## Appendix A: Label Definitions

**Epic Labels:**
- `epic:core-conversation` - Issues related to conversation loop and history
- `epic:provider-abstractions` - Issues related to provider flexibility
- `epic:polish` - Issues related to production readiness

**Type Labels:**
- `type:feature` - New feature implementation
- `type:refactor` - Code refactoring
- `type:docs` - Documentation
- `type:testing` - Testing tasks
- `type:enhancement` - Improvements to existing features

**Priority Labels:**
- `P0:critical` - Must have for MVP
- `P1:high` - Important for usability
- `P2:nice-to-have` - Can defer if needed

**Component Labels:**
- `component:llm` - LLM-related issues
- `component:stt` - STT-related issues
- `component:tts` - TTS-related issues
- `component:conversation` - Conversation management
- `component:config` - Configuration

---

## Appendix B: Quick Reference

**Total Issues:** 18
- Phase 1: 5 issues
- Phase 2: 7 issues
- Phase 3: 6 issues

**Estimated Timeline:**
- Week 1: Phase 1 (Issues #1-5)
- Week 2: Phase 2 (Issues #6-12)
- Week 3: Phase 3 (Issues #13-18)

**Critical Path:**
1. Issue #1 (conversation.py) → Issue #4 (main.py)
2. Issue #2 (VAD) → Issue #4 (main.py)
3. Issue #4 (main.py) → Issue #5 (Phase 1 testing)
4. Issue #5 → Issues #6, #7, #8 (provider routing)
5. Issue #6 → Issue #9 (formatting)
6. Issues #6, #7, #8 → Issue #12 (Phase 2 testing)
7. Issue #12 → Issues #13, #14 (improvements)
8. All → Issue #18 (final testing)

**Parallelizable Work:**
- Issues #1, #2, #3 can be done in parallel
- Issues #6, #7, #8 can be done in parallel
- Issues #13, #14, #15 can be done in parallel
- Issues #16, #17 can be done in parallel

---

**End of Implementation Plan**
