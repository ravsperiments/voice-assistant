# Tasks

## Completed
- [x] Stabilized Orca text-to-speech playback by normalizing PCM buffers before streaming to PyAudio.
- [x] Updated wake word pipeline to support configurable keywords and set the built-in "jarvis" trigger.
- [x] Containerized the assistant and added a Raspberry Pi single-click bootstrap script.

---

## Conversational Voice Assistant - Implementation Roadmap

**Reference:** See `IMPLEMENTATION_PLAN.md` for complete GitHub-ready issue details

**Timeline:** 2-3 weeks | **Total Issues:** 18 | **New Code:** ~400-500 lines

---

## Epic 1: Core Conversation Loop (epic-core-conversation)

**Objective:** Enable multi-turn conversations with simple history management and voice activity detection
**Success Criteria:** Users can have multi-turn conversations after wake word, ending with timeout or goodbye phrase
**Estimated Effort:** 1 week (Week 1)
**Milestone:** Phase 1 - Core Conversation
**Priority:** P0 (Critical for MVP)

### Tasks

- [ ] **TASK-001:** Create conversation.py module (Complexity: S)
  - Dependencies: None
  - Estimate: 2-3 hours
  - Acceptance Criteria:
    - Module exists at `components/conversation.py`
    - Functions: `add_user_message()`, `add_assistant_message()`, `clear_history()`, `get_history()`
    - History stored as list of `{"role": str, "content": str}` dicts
    - History automatically pruned to MAX_HISTORY_TURNS
    - Goodbye phrase detection implemented
    - Ollama prompt formatting implemented
  - Testing: Manual REPL testing of all functions
  - Issue: #1

- [ ] **TASK-002:** Implement voice activity detection in stt.py (Complexity: S)
  - Dependencies: None
  - Estimate: 2-3 hours
  - Acceptance Criteria:
    - Function `has_voice_activity(timeout_seconds: float) -> bool` implemented
    - Energy-based VAD using PyAudio and numpy
    - Configurable threshold via config.VAD_ENERGY_THRESHOLD
    - Returns True if voice detected, False on timeout
    - Logging shows energy levels for debugging
  - Testing: Manual testing with speech and silence
  - Issue: #2

- [ ] **TASK-003:** Update config.py with conversation settings (Complexity: S)
  - Dependencies: None
  - Estimate: 1 hour
  - Acceptance Criteria:
    - Settings added: MAX_HISTORY_TURNS, AWAITING_TIMEOUT, MAX_RESPONSE_TOKENS, VAD_ENERGY_THRESHOLD
    - All settings have sensible defaults
    - Comments explain each setting
  - Testing: Import config and verify settings
  - Issue: #3

- [ ] **TASK-004:** Create main.py conversation loop (Complexity: M)
  - Dependencies: TASK-001, TASK-002, TASK-003
  - Estimate: 4-6 hours
  - Acceptance Criteria:
    - Two-loop structure: outer (wake word) + inner (conversation turns)
    - Multi-turn conversations work without wake word
    - Timeout ends conversation
    - Goodbye phrases end conversation
    - Comprehensive logging at each step
    - Graceful error handling
    - Total ~100-150 lines
  - Testing: End-to-end conversation flows
  - Issue: #4

- [ ] **TASK-005:** Integration testing for Phase 1 (Complexity: M)
  - Dependencies: TASK-004
  - Estimate: 3-4 hours
  - Acceptance Criteria:
    - All conversation flows tested
    - No memory leaks after 10+ conversations
    - VAD works reliably
    - Error handling tested
    - Ready for Phase 2
  - Testing: Comprehensive manual testing
  - Issue: #5

---

## Epic 2: Provider Abstractions (epic-provider-abstractions)

**Objective:** Add provider flexibility for LLM, STT, and TTS components
**Success Criteria:** Can switch between 9 providers (3 each) via configuration without code changes
**Estimated Effort:** 1 week (Week 2)
**Milestone:** Phase 2 - Provider Flexibility
**Priority:** P1 (High importance)

### Tasks

- [ ] **TASK-006:** Add LLM provider routing to llm.py (Complexity: M)
  - Dependencies: TASK-005
  - Estimate: 4-6 hours
  - Acceptance Criteria:
    - Support for Ollama, OpenAI, Anthropic
    - Provider selection via config.LLM_PROVIDER
    - Functions: `_call_ollama()`, `_call_openai()`, `_call_anthropic()`
    - Consistent response format across providers
    - Graceful error handling for all providers
  - Testing: Test each provider individually
  - Issue: #6

- [ ] **TASK-007:** Add STT provider routing to stt.py (Complexity: M)
  - Dependencies: TASK-005
  - Estimate: 4-6 hours
  - Acceptance Criteria:
    - Support for Vosk, Whisper, Deepgram
    - Provider selection via config.STT_PROVIDER
    - Functions: `_transcribe_vosk()`, `_transcribe_whisper()`, `_transcribe_deepgram()`
    - Consistent return format across providers
    - Graceful error handling
  - Testing: Test each provider individually
  - Issue: #7

- [ ] **TASK-008:** Add TTS provider routing to tts.py (Complexity: M)
  - Dependencies: TASK-005
  - Estimate: 4-6 hours
  - Acceptance Criteria:
    - Support for Orca, Piper, OpenAI
    - Provider selection via config.TTS_PROVIDER
    - Functions: `_speak_orca()`, `_speak_piper()`, `_speak_openai()`
    - Audio playback works for all providers
    - Graceful error handling
  - Testing: Test each provider individually
  - Issue: #8

- [ ] **TASK-009:** Update conversation.py for multi-provider formatting (Complexity: S)
  - Dependencies: TASK-006
  - Estimate: 2-3 hours
  - Acceptance Criteria:
    - `format_for_llm()` handles Ollama (string), OpenAI (messages), Anthropic (messages)
    - System message included for all providers
    - Correct format for each provider type
  - Testing: Test formatting for each provider
  - Issue: #9

- [ ] **TASK-010:** Update config.py with all provider settings (Complexity: S)
  - Dependencies: TASK-006, TASK-007, TASK-008
  - Estimate: 2-3 hours
  - Acceptance Criteria:
    - Provider selection settings: LLM_PROVIDER, STT_PROVIDER, TTS_PROVIDER
    - All provider-specific settings (API keys, models, etc.)
    - Well-organized sections with comments
    - Total ~50 lines added
  - Testing: Verify all settings load correctly
  - Issue: #10

- [ ] **TASK-011:** Update requirements.txt with new dependencies (Complexity: S)
  - Dependencies: None
  - Estimate: 1 hour
  - Acceptance Criteria:
    - Added: openai, anthropic, openai-whisper, deepgram-sdk, python-dotenv
    - Organized by category with comments
    - Version pins appropriate
  - Testing: Fresh install in virtual environment
  - Issue: #11

- [ ] **TASK-012:** Integration testing for Phase 2 (Complexity: M)
  - Dependencies: TASK-006, TASK-007, TASK-008, TASK-009, TASK-010, TASK-011
  - Estimate: 4-6 hours
  - Acceptance Criteria:
    - All 9 providers tested individually
    - At least 6 provider combinations tested
    - Error handling tested (invalid keys, network errors)
    - Performance documented for each provider
    - No regressions from Phase 1
  - Testing: Comprehensive provider testing matrix
  - Issue: #12

---

## Epic 3: Polish & Production Ready (epic-polish)

**Objective:** Production readiness with error handling, documentation, and validation
**Success Criteria:** System is stable, well-documented, and ready for deployment
**Estimated Effort:** 1 week (Week 3)
**Milestone:** Phase 3 - Production Ready
**Priority:** P1 (High importance)

### Tasks

- [ ] **TASK-013:** Improve error handling and logging (Complexity: S)
  - Dependencies: TASK-012
  - Estimate: 3-4 hours
  - Acceptance Criteria:
    - Structured logging with appropriate levels
    - Clear, actionable error messages
    - Debug mode configuration
    - No uncaught exceptions
  - Testing: Trigger various errors, verify messages
  - Issue: #13

- [ ] **TASK-014:** Optimize VAD parameters (Complexity: S)
  - Dependencies: TASK-012
  - Estimate: 2-3 hours
  - Acceptance Criteria:
    - VAD tested in quiet and noisy environments
    - Optimal threshold documented
    - False positives/negatives minimized
    - Tuning process documented
  - Testing: Empirical testing with various thresholds
  - Issue: #14

- [ ] **TASK-015:** Create .env.example file (Complexity: S)
  - Dependencies: TASK-010
  - Estimate: 1 hour
  - Acceptance Criteria:
    - All API keys documented with placeholders
    - Comments explain each variable
    - Links to sign-up pages
    - Organized by provider
  - Testing: Copy to .env and verify works
  - Issue: #15

- [ ] **TASK-016:** Update README documentation (Complexity: M)
  - Dependencies: TASK-012
  - Estimate: 3-4 hours
  - Acceptance Criteria:
    - Complete setup instructions
    - Provider comparison table
    - Configuration examples
    - Troubleshooting section
    - Users can set up from scratch
  - Testing: Fresh setup following README
  - Issue: #16

- [ ] **TASK-017:** Create provider comparison guide (Complexity: S)
  - Dependencies: TASK-012
  - Estimate: 2-3 hours
  - Acceptance Criteria:
    - All 9 providers documented
    - Performance data from testing
    - Cost comparison
    - Use case recommendations
  - Testing: Verify data accuracy
  - Issue: #17

- [ ] **TASK-018:** Final testing and validation (Complexity: M)
  - Dependencies: TASK-013, TASK-014, TASK-015, TASK-016, TASK-017
  - Estimate: 4-6 hours
  - Acceptance Criteria:
    - All features tested end-to-end
    - All provider combinations tested
    - Performance targets met
    - No memory leaks (1 hour stability test)
    - Documentation validated
    - Production-ready
  - Testing: Comprehensive final validation
  - Issue: #18

---

## Summary

**Phase 1 (Week 1):** Core Conversation Loop
- 5 tasks, ~12-15 hours total
- Deliverable: Working multi-turn conversation with default providers

**Phase 2 (Week 2):** Provider Abstractions
- 7 tasks, ~22-30 hours total
- Deliverable: Full provider flexibility via configuration

**Phase 3 (Week 3):** Polish & Production Ready
- 6 tasks, ~15-21 hours total
- Deliverable: Production-ready system

**Total Estimated Effort:** ~49-66 hours (2-3 weeks at sustainable pace)

---

## Additional Tasks (Lower Priority)

- [ ] Fine-tune wake word sensitivity and overall conversational flow for production readiness
- [ ] Add unit tests for critical functions (optional for MVP)
- [ ] Create demo video showing multi-turn conversation
- [ ] Set up CI/CD pipeline for automated testing
- [ ] Add metrics collection for conversation quality
