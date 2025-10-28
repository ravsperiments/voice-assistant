
# main.py

import logging
import config
from components.wake_word import wait_for_wake_word
from components.stt import transcribe_audio, has_voice_activity
from components.llm import generate_response
from components.tts import speak_text
from components import conversation

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_conversation() -> None:
    """
    Run a multi-turn conversation loop.

    Handles conversation turns until:
    - User says goodbye/quit/exit
    - Timeout waiting for next turn (no voice activity)
    - LLM error
    """
    logger.info("Starting new conversation")
    conversation.clear_history()
    turn_count = 0

    # Initial greeting
    greeting = "Hello! I'm ready to talk. What would you like to know?"
    logger.info(f"Assistant: {greeting}")
    speak_text(greeting)
    conversation.add_assistant_message(greeting)

    while True:
        turn_count += 1
        logger.info(f"Conversation turn {turn_count}: Waiting for user input...")

        # Wait for voice activity with timeout
        has_activity = has_voice_activity(
            timeout_seconds=config.AWAITING_TIMEOUT,
            energy_threshold=config.VAD_ENERGY_THRESHOLD
        )

        if not has_activity:
            logger.info("No voice activity detected - ending conversation")
            farewell = "It seems you're not saying anything. Goodbye!"
            logger.info(f"Assistant: {farewell}")
            speak_text(farewell)
            break

        # Transcribe user input
        try:
            user_input = transcribe_audio()
            if not user_input:
                logger.warning("Transcription returned empty - skipping turn")
                continue

            logger.info(f"User (turn {turn_count}): {user_input}")
            conversation.add_user_message(user_input)

            # Check if user wants to end conversation
            if conversation.is_conversation_ending():
                logger.info("User requested conversation end")
                farewell = "Goodbye! Thanks for chatting!"
                logger.info(f"Assistant: {farewell}")
                speak_text(farewell)
                break

            # Generate response from LLM
            logger.info("Generating LLM response...")
            prompt = conversation.format_for_llm()
            llm_response = generate_response(prompt)

            if not llm_response:
                logger.error("LLM returned empty response")
                error_msg = "Sorry, I couldn't generate a response. Please try again."
                speak_text(error_msg)
                continue

            logger.info(f"Assistant (turn {turn_count}): {llm_response}")
            conversation.add_assistant_message(llm_response)
            speak_text(llm_response)

        except KeyboardInterrupt:
            logger.info("Conversation interrupted by user (Ctrl+C)")
            farewell = "Goodbye!"
            speak_text(farewell)
            break
        except Exception as e:
            logger.error(f"Error in conversation turn {turn_count}: {e}", exc_info=True)
            error_msg = "Sorry, something went wrong. Let's try again."
            speak_text(error_msg)
            continue

    logger.info(f"Conversation ended after {turn_count} turns")


def main():
    """
    The main loop of the voice assistant.

    Two-loop structure:
    - Outer loop: Wait for wake word
    - Inner loop: Run conversation turns
    """
    logger.info("Voice Assistant starting...")
    logger.info(f"Configuration: MAX_HISTORY_TURNS={config.MAX_HISTORY_TURNS}, "
                f"AWAITING_TIMEOUT={config.AWAITING_TIMEOUT}s, "
                f"VAD_ENERGY_THRESHOLD={config.VAD_ENERGY_THRESHOLD}")

    try:
        while True:
            logger.info("Waiting for wake word...")
            wait_for_wake_word()
            logger.info(f"Wake word '{config.WAKE_WORD_NAME}' detected!")
            run_conversation()
            logger.info("Returned to wake word detection")

    except KeyboardInterrupt:
        logger.info("Voice Assistant shutting down (Ctrl+C)")
    except Exception as e:
        logger.error(f"Fatal error in main loop: {e}", exc_info=True)
    finally:
        logger.info("Voice Assistant stopped")


if __name__ == "__main__":
    main()
