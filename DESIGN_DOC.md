# Design Document: Offline Voice Assistant for Raspberry Pi (MVP)

## 1. Overview

This document outlines the design for a Minimum Viable Product (MVP) of a voice assistant that runs entirely offline on a Raspberry Pi. The assistant will be activated by a wake word, convert spoken language to text, generate a response using a local large language model, and speak the response back to the user.

## 2. Goals

*   Create a functional, end-to-end voice assistant pipeline.
*   Ensure all components run without an internet connection.
*   The system should be responsive enough for a basic conversational experience.
*   The core functionality will be: Wake Word -> Speech-to-Text -> LLM Response -> Text-to-Speech.

## 3. Non-Goals

*   Internet-dependent features (e.g., weather forecasts, web searches, smart home control).
*   Advanced conversational memory or user context awareness.
*   Support for multiple languages (MVP will focus on English).
*   A graphical user interface (GUI).
*   Commercial-grade accuracy and speed.

## 4. Architecture

The system will be composed of four main components running in a sequential pipeline on the Raspberry Pi.

```
[User Speaks] -> (1. Wake Word Engine) -> [Audio Stream] -> (2. Speech-to-Text Engine) -> [Text] -> (3. LLM Engine) -> [Response Text] -> (4. Text-to-Speech Engine) -> [Audio Output]
```

*   **1. Wake Word Engine:** Continuously listens to the microphone input for a specific wake word. When detected, it passes the subsequent audio stream to the STT engine.
*   **2. Speech-to-Text (STT) Engine:** Transcribes the user's speech from the audio stream into a text string.
*   **3. LLM Engine:** Takes the transcribed text as a prompt for the Granite model running via Ollama to generate a text-based response.
*   **4. Text-to-Speech (TTS) Engine:** Converts the generated text response into audible speech and plays it through the speakers.

## 5. Components & Technology Stack

### 5.1. Wake Word Detection

*   **Technology:** **Picovoice Porcupine**
*   **Reasoning:** Porcupine is highly efficient and has a generous free tier. It's designed for low-power devices like the Raspberry Pi and is easy to integrate using its Python SDK.
*   **Implementation:** A Python script will initialize the Porcupine engine with a chosen wake word model (e.g., "Hey, Raspberry"). It will continuously read audio from the microphone and, upon wake word detection, trigger the next stage.

### 5.2. Speech-to-Text (STT)

*   **Technology:** **Vosk**
*   **Reasoning:** Vosk offers excellent offline speech recognition with good accuracy. It supports multiple languages (though we'll use English) and has pre-trained models that are lightweight enough to run on a Raspberry Pi.
*   **Implementation:** Once triggered, the STT component will capture a few seconds of audio, convert it to the required format (e.g., 16kHz mono WAV), and pass it to the Vosk recognizer to get the transcribed text.

### 5.3. Response Generation (LLM)

*   **Technology:** **Ollama with Granite**
*   **Reasoning:** The user has specified this stack. Ollama provides a simple way to serve and query LLMs locally. The Granite model will be used for generating responses.
*   **Caveat:** Running a large model like Granite on a Raspberry Pi will be resource-intensive. A Raspberry Pi 4 with 8GB RAM or a Raspberry Pi 5 is strongly recommended. The response time might be slow. For better performance, a smaller, instruction-tuned model could be considered as an alternative.
*   **Implementation:** A Python script will make an HTTP request to the local Ollama server's API (`/api/generate`) with the text from the STT engine as the prompt. The response from the API will be parsed to extract the generated text.

### 5.4. Text-to-Speech (TTS)

*   **Technology:** **Piper**
*   **Reasoning:** Piper is a fast, local neural text-to-speech system that produces natural-sounding voices. It is well-optimized for the Raspberry Pi.
*   **Implementation:** The text response from the LLM will be passed to the Piper engine, which will generate a WAV file. This audio file will then be played using a standard audio player (like `aplay`).

## 6. Hardware Requirements

*   **Raspberry Pi:** Raspberry Pi 4 (4GB+, 8GB recommended) or Raspberry Pi 5.
*   **Microphone:** A USB microphone or a microphone array HAT (e.g., ReSpeaker).
*   **Speaker:** Any standard speaker that can be connected to the Raspberry Pi (via 3.5mm jack, USB, or HDMI).
*   **SD Card:** A high-speed microSD card (32GB+ recommended) to store the OS, models, and software.

## 7. High-Level Implementation Plan

1.  **Setup Raspberry Pi:** Install Raspberry Pi OS, update the system, and configure audio devices (microphone and speaker).
2.  **Install Ollama:** Download and install Ollama on the Raspberry Pi. Pull the Granite model: `ollama pull granite`.
3.  **Install Dependencies:** Install Python and the necessary libraries for each component:
    *   `pvporcupine` for wake word.
    *   `vosk` for STT.
    *   `requests` for communicating with Ollama.
    *   `piper-tts` for TTS.
4.  **Develop Components:**
    *   Write a Python script for the wake word engine.
    *   Write a function/module for STT.
    *   Write a function/module to query the Ollama API.
    *   Write a function/module for TTS.
5.  **Integrate Pipeline:** Create a main script that orchestrates the flow between the components. This script will handle the state transitions (e.g., from listening for wake word to listening for command).

## 8. Future Work (Post-MVP)

*   **Improved NLU:** Use a smaller, dedicated NLU model to understand user intent (e.g., "what time is it?") and trigger specific actions instead of just conversational responses.
*   **Skill/Action Framework:** Implement a system to perform actions like reading the time, date, or system status.
*   **Performance Optimization:** Investigate smaller, faster models for STT, LLM, and TTS to reduce latency.
*   **Contextual Conversation:** Add a mechanism to remember the last few turns of the conversation.
