
import requests
import json
import sys
import os

# Add the parent directory to sys.path for module discovery
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import OLLAMA_API_URL, OLLAMA_MODEL_NAME

def generate_response(prompt):
    """
    Generates a response from the local Ollama LLM.
    """
    try:
        payload = {
            "model": OLLAMA_MODEL_NAME,
            "prompt": prompt,
            "stream": False
        }
        print(f"Sending payload to Ollama: {payload}")
        response = requests.post(OLLAMA_API_URL, json=payload)
        print(f"Ollama response status code: {response.status_code}")
        print(f"Ollama response text: {response.text}")
        response.raise_for_status()  # Raise an exception for bad status codes

        # The response from Ollama is a JSON object, with the response in the 'response' key
        response_data = response.json()
        return response_data.get("response", "Sorry, I couldn't generate a response.")

    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Ollama: {e}")
        return "Sorry, I'm having trouble connecting to the language model."
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return "Sorry, an unexpected error occurred."
