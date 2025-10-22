# components/llm.py

import requests
import json
import sys
import os

# Add the parent directory to sys.path for module discovery when run directly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import OLLAMA_API_URL, OLLAMA_MODEL_NAME

def generate_response(prompt: str) -> str:
    """
    Sends a prompt to the local Ollama server and returns the generated response.

    Args:
        prompt (str): The text prompt to send to the LLM.

    Returns:
        str: The generated text response from the LLM, or an error message if something goes wrong.
    """
    headers = {"Content-Type": "application/json"}
    data = {
        "model": OLLAMA_MODEL_NAME,
        "prompt": prompt,
        "stream": False # We want a single response, not a stream of tokens
    }

    try:
        response = requests.post(OLLAMA_API_URL, headers=headers, data=json.dumps(data))
        response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)

        response_data = response.json()
        # Ollama's /api/generate endpoint returns a JSON object with a 'response' field
        if "response" in response_data:
            return response_data["response"].strip()
        else:
            return f"Error: 'response' field not found in Ollama's reply: {response_data}"

    except requests.exceptions.ConnectionError:
        return "Error: Could not connect to Ollama server. Is it running?"
    except requests.exceptions.Timeout:
        return "Error: Ollama server connection timed out."
    except requests.exceptions.RequestException as e:
        return f"Error during request to Ollama server: {e}"
    except json.JSONDecodeError:
        return f"Error: Could not decode JSON response from Ollama server: {response.text}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

if __name__ == "__main__":
    # Simple test for the LLM component
    print("Testing LLM component with a sample prompt...")
    test_prompt = "What is the capital of France?"
    llm_response = generate_response(test_prompt)
    print(f"Prompt: {test_prompt}")
    print(f"LLM Response: {llm_response}")

    test_prompt_2 = "Tell me a short story about a robot."
    llm_response_2 = generate_response(test_prompt_2)
    print(f"Prompt: {test_prompt_2}")
    print(f"LLM Response: {llm_response_2}")
