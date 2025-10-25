
# main.py

from components.wake_word import wait_for_wake_word
from components.stt import transcribe_audio
from components.llm import generate_response
from components.tts import speak_text

def main():
    """
    The main loop of the voice assistant.
    """
    print("Starting voice assistant...")
    while True:
        wait_for_wake_word()
        print("Wake word detected! Now listening for command...")
        user_prompt = transcribe_audio()
        if user_prompt:
            print(f"User said: {user_prompt}")
            llm_response = generate_response(user_prompt)
            print(f"LLM said: {llm_response}")
            speak_text(llm_response)
            print("Awaiting wake word...")

if __name__ == "__main__":
    main()
