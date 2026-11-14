# 🎙️ Aura: Python Voice Assistant (`ArnavSharma_Task1`)

[![Python Version](https://img.shields.io/badge/Python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Internship](https://img.shields.io/badge/Oasis%20InfoTech-Python%20Programming-orange.svg)](https://oasisinfobyte.com/)
[![Tests](https://img.shields.io/badge/Tests-22%20Passed-brightgreen.svg)]()
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)]()

> A modular, intelligent, desktop Python voice assistant implementing both **Beginner** and **Advanced Tier** requirements for Task 1 of the Oasis InfoTech Python Programming Internship. Capable of speech-to-text input, offline text-to-speech synthesis, Natural Language Understanding (NLU), multi-turn email automation, live weather forecasting, non-blocking voice reminders, desktop app launching, general knowledge retrieval, and custom commands.

---

## 📋 Table of Contents

1. [Project Overview](#1-project-overview)
2. [Project Objectives](#2-project-objectives)
3. [Features & Tier Checklist](#3-features--tier-checklist)
4. [Technology Stack & Architecture](#4-technology-stack--architecture)
5. [Directory Structure](#5-directory-structure)
6. [Prerequisites & System Requirements](#6-prerequisites--system-requirements)
7. [Step-by-Step Installation Guide](#7-step-by-step-installation-guide)
8. [Virtual Environment Setup](#8-virtual-environment-setup)
9. [Microphone & PyAudio Configuration](#9-microphone--pyaudio-configuration)
10. [API Key Configuration (OpenWeatherMap)](#10-api-key-configuration-openweathermap)
11. [SMTP Email Configuration](#11-smtp-email-configuration)
12. [How to Run the Assistant](#12-how-to-run-the-assistant)
13. [Example Voice Commands & Responses](#13-example-voice-commands--responses)
14. [User Interface & Visual Screenshots](#14-user-interface--visual-screenshots)
15. [Error Handling & Troubleshooting](#15-error-handling--troubleshooting)
16. [Privacy, Data Handling & Security Considerations](#16-privacy-data-handling--security-considerations)
17. [Future Enhancements](#17-future-enhancements)
18. [Author & Submission Information](#18-author--submission-information)

---

## 1. Project Overview

**Aura** (`ArnavSharma_Task1`) is an intelligent, user-friendly desktop voice assistant developed in Python 3. It bridges the gap between simple command-matching scripts and conversational AI through a modular, decoupled architecture:

- **Offline-First Text-to-Speech**: Employs `pyttsx3` running in a dedicated worker queue to speak every response without latency or internet dependency.
- **Microphone Speech Recognition**: Utilizes `SpeechRecognition` backed by `PyAudio` with ambient noise calibration and a graceful text-typing fallback if audio hardware is absent.
- **Natural Language Understanding (NLU)**: Employs token Jaccard similarity, regex extraction, and semantic scoring to understand free-form requests rather than brittle keyword matching.
- **Multi-Turn Conversational Automation**: Solicits missing slots (recipient, subject, body) for email dispatch with a mandatory confirmation gate before transmission.
- **Non-Blocking Background Reminders**: Executes background daemon threads that trigger pleasant audible chimes and spoken voice notifications when timers expire.
- **Dual Interface**: Offers a sleek, dark-themed Tkinter GUI as well as interactive CLI and text-only console modes.

---

## 2. Project Objectives

- **Develop a reliable conversational interface**: Seamlessly process spoken commands and respond using clear text-to-speech audio.
- **Implement resilient error handling**: Prevent crashes when audio devices are disconnected, API keys are missing, or network connections drop.
- **Ensure privacy and security**: Process audio in memory without saving audio recordings to disk, and prevent accidental credential leaks using environment variables and log sanitization.
- **Maintain clean code and extensibility**: Adhere to PEP 8 standards, decouple concerns across dedicated modules, and allow non-programmers to add custom commands via `config.json`.

---

## 3. Features & Tier Checklist

### Beginner Tier Features (All Implemented)
- [x] **Microphone Capture**: Captures speech using `SpeechRecognition` and `PyAudio`.
- [x] **Predefined Greetings**: Responds to "Hello", "Hi", "Hey" with personalized, time-of-day greetings ("Good morning", "Good afternoon", "Good evening").
- [x] **Time & Date Reporting**: Tells the current 12-hour formatted time and calendar date in natural English.
- [x] **Web Search**: Automatically launches the default browser with queries (Google, Bing, YouTube, GitHub).
- [x] **Graceful Error Handling**: Detects unintelligible audio, service outages, and microphone disconnections, politely asking the user to repeat or type.
- [x] **Text-to-Speech Spoken Feedback**: Spoken audio feedback using `pyttsx3` for every single response.

### Advanced Tier Features (All Implemented)
- [x] **Natural Language Understanding (NLU)**: Recognizes intents from free-form sentences using semantic scoring, entity regex extraction, and fuzzy token similarity.
- [x] **Email Automation**: Dispatches emails via SMTP with contact alias resolution, multi-step slot filling, and mandatory voice confirmation ("Say yes to send or no to cancel").
- [x] **Voice Reminders**: Schedules background daemon timers for custom durations ("30 seconds", "10 minutes", "1 hour"), triggers audible tones, and speaks reminder alerts.
- [x] **Live Weather Forecasting**: Integrates OpenWeatherMap API to report temperature in Celsius, feels-like temperature, humidity, weather conditions, and wind speed.
- [x] **General Knowledge QA**: Dual-layer question answering with a rich local offline encyclopedia supplemented by online Wikipedia API lookups.
- [x] **Custom Commands**: Allows users to define custom voice triggers, canned replies, and app/URL launches in `config.json` without modifying Python code.
- [x] **Privacy & Zero-Storage Architecture**: Strictly processes voice in RAM and discards it immediately; redacts credentials in rotating log files.

### Additional Creative Features
- [x] **Dual Desktop Interface**: Dark-themed Tkinter GUI with chat bubbles, quick-action chips, and typed input fallback, plus a console mode.
- [x] **Desktop Application Launcher**: Opens native tools like Notepad, Calculator, Paint, Chrome, File Explorer, and Task Manager on command.
- [x] **Active Reminders Manager**: Inspect and cancel active reminders ("what are my reminders?", "cancel all reminders").
- [x] **System Status & Diagnostics**: Self-test diagnostic mode (`python main.py --test`) and live status command.
- [x] **Graceful Voice Exit**: Terminates cleanly with a polite farewell on commands like "exit", "quit", "goodbye".

---

## 4. Technology Stack & Architecture

### Core Technologies
| Component | Technology | Description |
| :--- | :--- | :--- |
| **Language** | Python 3.9+ | Main programming language (tested on Python 3.13) |
| **Speech-to-Text** | `SpeechRecognition` + `PyAudio` | Microphone audio capture and Google Speech Recognition |
| **Text-to-Speech** | `pyttsx3` | Offline voice synthesis (Windows SAPI5 / Linux eSpeak) |
| **GUI Framework** | `tkinter` & `ttk` | Built-in, zero-dependency desktop graphical interface |
| **HTTP Requests** | `requests` | Weather API & network queries |
| **Environment Secrets** | `python-dotenv` | Secure loading of API keys and credentials |
| **Online Knowledge** | `wikipedia` | Summary extraction for general knowledge inquiries |
| **Concurrency** | `threading` & `queue` | Non-blocking timers, background TTS, and decoupled GUI |

### Architecture Diagram

```
+---------------------------------------------------------------------------------+
|                                USER INTERFACES                                  |
|   +-------------------------------------+   +-------------------------------+   |
|   |         Tkinter Desktop GUI         |   |    Interactive Console / CLI  |   |
|   | (Chat Bubbles, Mic Btn, Quick Chips)|   |   (Voice Loop & Typed Input)  |   |
|   +------------------+------------------+   +---------------+---------------+   |
+----------------------|--------------------------------------|-------------------+
                       v                                      v
+---------------------------------------------------------------------------------+
|                           CORE ASSISTANT ORCHESTRATOR                           |
|                               (modules/assistant.py)                            |
|  - Dialog State Machine (Idle, Email Draft, Confirmation, Custom Command)       |
|  - Multi-Service Router & Thread Management                                     |
+--------------------------------------+------------------------------------------+
                                       |
    +----------------------------------+----------------------------------+
    |                                  |                                  |
    v                                  v                                  v
+-----------------------+  +-----------------------+  +-----------------------+
|  SPEECH I/O ENGINE    |  |     NLU & INTENT      |  |    SERVICE WORKERS    |
|  (modules/speech.py)  |  |  (modules/intent.py)  |  |                       |
|                       |  |                       |  | • WeatherService      |
| • SpeechRecognizer    |  | • IntentEngine        |  | • EmailService (SMTP) |
|   (PyAudio + Google)  |  | • Entity Extractor    |  | • ReminderManager     |
| • TTSManager (Queue)  |  | • Utterance Bank      |  | • KnowledgeService    |
|   (pyttsx3 offline)   |  | • Token Similarity    |  | • WebSearchService    |
+-----------------------+  +-----------------------+  | • AppLauncher         |
                                                      +-----------------------+
                                                                  |
                                                                  v
                                                      +-----------------------+
                                                      | CONFIG & PERSISTENCE  |
                                                      | • config.json         |
                                                      | • .env (Secrets)      |
                                                      | • logs/assistant.log  |
                                                      +-----------------------+
```

---

## 5. Directory Structure

```text
ArnavSharma_Task1/
│
├── main.py                     # Primary entry point (GUI, CLI, Text-Only, Diagnostics)
├── config.json                 # User settings, contact aliases, and custom commands
├── .env.example                # Template for API keys and email credentials
├── .gitignore                  # Git exclusion rules (ignores .env, venvs, logs)
├── requirements.txt            # Python dependencies
├── README.md                   # Comprehensive documentation and guide
│
├── modules/                    # Modular service components
│   ├── __init__.py             # Package exports
│   ├── assistant.py            # Core VoiceAssistant orchestrator and dialog manager
│   ├── speech.py               # SpeechRecognizer and thread-safe TTSManager
│   ├── intent.py               # Natural Language Understanding & intent classifier
│   ├── weather.py              # OpenWeatherMap live weather integration
│   ├── email_service.py        # SMTP email dispatcher with slot filling & confirmation
│   ├── reminders.py            # Background thread reminders with audible alert chime
│   ├── web_search.py           # Web browser automation and engine queries
│   ├── knowledge.py            # Dual-layer QA (offline curated encyclopedia + Wikipedia)
│   ├── app_launcher.py         # Windows desktop application launcher
│   └── gui.py                  # Tkinter dark-themed desktop graphical interface
│
├── utils/                      # Helper and system utilities
│   ├── __init__.py             # Utility package exports
│   ├── helpers.py              # Time, natural speech, duration, and text helpers
│   └── logger.py               # Thread-safe sanitized logger with credential redaction
│
├── tests/                      # Automated unit test suite
│   ├── __init__.py
│   └── test_assistant.py       # 22 comprehensive unit tests covering all features
│
└── assets/                     # Media and screenshots
    └── screenshots/
        └── README.md           # Visual interface preview and mockups
```

---

## 6. Prerequisites & System Requirements

- **Operating System**: Windows 10/11 (fully supported with SAPI5 TTS, `winsound`, and app launcher), Linux, or macOS.
- **Python**: Python 3.9 through Python 3.13.
- **Hardware**: Working microphone and speakers / headphones.
- **Internet**: Required for online speech recognition, live weather, and Wikipedia. (The assistant includes offline local knowledge and typed fallback if disconnected).

---

## 7. Step-by-Step Installation Guide

### Step 1: Open Terminal in Project Directory
Navigate to the root directory `ArnavSharma_Task1`:
```bash
cd "c:\Users\Arnav Sharma\Desktop\Resume\Internship\Oaisis Info Tech Python Programming\ArnavSharma_Task1"
```

### Step 2: Create a Virtual Environment
```bash
python -m venv .venv
```

### Step 3: Activate the Virtual Environment
- **Windows (Command Prompt / PowerShell)**:
  ```powershell
  .\.venv\Scripts\activate
  ```
- **Linux / macOS**:
  ```bash
  source .venv/bin/activate
  ```

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 8. Virtual Environment Setup

Using a virtual environment guarantees that your global Python installation remains clean and prevents package conflicts:

```bash
# Verify virtual environment activation
python -c "import sys; print('Using Virtual Env:', sys.prefix != sys.base_prefix)"
```

Expected output:
```text
Using Virtual Env: True
```

---

## 9. Microphone & PyAudio Configuration

### Windows Installation
`PyAudio` is included in `requirements.txt`. On Python 3.13 for Windows, pre-compiled wheels install directly via `pip`:
```bash
pip install PyAudio
```

*Note: If `pip install pyaudio` fails on an older Python version, install the Windows C++ Build Tools or download a pre-built wheel from Christoph Gohlke's Python extension repository.*

### Linux (Ubuntu/Debian)
Install PortAudio development headers before installing PyAudio:
```bash
sudo apt-get update
sudo apt-get install python3-pyaudio portaudio19-dev libespeak1
pip install PyAudio
```

### macOS
Install PortAudio using Homebrew:
```bash
brew install portaudio
pip install PyAudio
```

### Audio Input Verification
To test if your microphone is detected by Python:
```bash
python main.py --test
```
If no microphone is attached, the assistant will automatically switch to **Typed Input Fallback Mode** so you can continue testing all features without hardware.

---

## 10. API Key Configuration (OpenWeatherMap)

The assistant uses the **OpenWeatherMap API** to fetch real-time temperatures, humidity, and weather conditions.

1. Create a free account at [OpenWeatherMap Sign-Up](https://home.openweathermap.org/users/sign_up).
2. Go to **API Keys** and generate a free API key.
3. Copy `.env.example` to `.env`:
   ```bash
   copy .env.example .env
   ```
4. Open `.env` and paste your API key:
   ```env
   OPENWEATHER_API_KEY=your_actual_32_character_api_key_here
   ```

*Graceful Degradation Note: If no API key is provided, the assistant politely informs you how to set up `.env` without crashing.*

---

## 11. SMTP Email Configuration

The assistant includes voice-guided email automation using Python's built-in `smtplib`.

### Configuration Steps (For Gmail)
1. Go to your [Google Account Security Settings](https://myaccount.google.com/security).
2. Ensure **2-Step Verification** is enabled.
3. Under *2-Step Verification*, select **App passwords** (or visit [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)).
4. Create an App password named `VoiceAssistant` and copy the 16-character code.
5. In your `.env` file, configure your credentials:
   ```env
   SMTP_EMAIL=your_email@gmail.com
   SMTP_PASSWORD=abcd efgh ijkl mnop
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USE_TLS=True
   ```

### Safe Simulated (Dry-Run) Mode
If you do not configure an SMTP password, the assistant automatically switches to **Dry-Run Mode**. It logs and speaks:
> *"Simulated email sent to arnav.sharma.dev@example.com with subject 'Project Review'..."*

This allows for safe demonstrations and grading without risking account lockouts.

---

## 12. How to Run the Assistant

The application supports four execution modes:

### Mode 1: Desktop Graphical User Interface (Default)
```bash
python main.py
```
*Launches the modern dark-themed Tkinter GUI featuring status indicators, real-time message bubbles, quick-action chips, and interactive microphone triggers.*

### Mode 2: Interactive Voice & Console Mode
```bash
python main.py --cli
```
*Runs directly inside your terminal, capturing spoken audio from the microphone while displaying colored output.*

### Mode 3: Text-Only Terminal Mode (No Microphone Required)
```bash
python main.py --text-only
```
*Disables the microphone listener and lets you interact by typing queries directly. Ideal for quiet office environments or automated tests.*

### Mode 4: Self-Test Diagnostics
```bash
python main.py --test
```
*Performs an automated health check across all submodules, APIs, audio devices, and intent parsers.*

---

## 13. Example Voice Commands & Responses

| Category | Example Voice Command | Expected Assistant Response |
| :--- | :--- | :--- |
| **Greeting** | *"Hello Aura"* | *"Good evening, Arnav! How can I assist you tonight?"* |
| **Current Time** | *"What time is it?"* | *"The current time is 11:30 PM."* |
| **Current Date** | *"What is today's date?"* | *"Today is Friday, November 13th, 2026."* |
| **Live Weather** | *"What's the weather in Kolkata?"* | *"The current weather in Kolkata is 27 degrees Celsius with clear skies. Humidity is at 65%..."* |
| **Web Search** | *"Search for Python machine learning tutorials"* | *"Searching the web for Python machine learning tutorials."* *(Opens browser)* |
| **Set Reminder** | *"Remind me to study after 10 minutes"* | *"Your reminder has been successfully set for 10 minutes."* |
| **List Reminders**| *"What are my reminders?"* | *"You have 1 active reminder. Number 1: study, due in 9 minutes and 50 seconds."* |
| **General QA** | *"Who is Albert Einstein?"* | *"Albert Einstein was a German-born theoretical physicist... known for developing the theory of relativity..."* |
| **Knowledge QA**| *"What is photosynthesis?"* | *"Photosynthesis is the biological process used by plants... to convert light energy into chemical energy..."* |
| **Open App** | *"Open Calculator"* | *"Opening Calculator."* *(Launches `calc.exe`)* |
| **Custom Command**| *"Who created you?"* | *"I was developed by Arnav Sharma for the Oasis InfoByte Python Programming Internship."* |
| **Email Flow** | *"Send an email to Arnav"* | *(Step 1)* *"What is the subject of the email?"*<br>*(Step 2)* *"What message would you like to send?"*<br>*(Step 3)* *"I am ready to send your email to ... Would you like me to send it? Say yes or no."* |
| **Help Menu** | *"Help"* | *"Here is what I can do for you, Arnav: 1. Tell time and date. 2. Fetch live weather..."* |
| **Exit** | *"Goodbye"* | *"Goodbye Arnav! Have a wonderful day."* *(Terminates cleanly)* |

---

## 14. User Interface & Visual Screenshots

### Desktop GUI Layout
The GUI is designed with a modern dark theme inspired by Discord and VS Code:

```text
+---------------------------------------------------------------+
|  🎙️ Aura Voice Assistant                         🟢 Ready    |
|  Built by Arnav Sharma | Oasis InfoTech Internship            |
+---------------------------------------------------------------+
|  [🕒 Time]  [📅 Date]  [⛅ Weather]  [⏰ 10s Timer]  [❓ Help]  |
+---------------------------------------------------------------+
|                                                               |
|  🎙️ Aura: Good evening, Arnav! I am Aura, your personal       |
|           Python voice assistant. How may I help you?         |
|                                                               |
|  👤 You: what time is it                                      |
|                                                               |
|  🎙️ Aura: The current time is 11:31 PM.                       |
|                                                               |
|  👤 You: remind me to study after 10 minutes                  |
|                                                               |
|  🎙️ Aura: Your reminder has been successfully set for        |
|           10 minutes.                                         |
|                                                               |
|  👤 You: search for Python machine learning tutorials         |
|                                                               |
|  🎙️ Aura: Searching the web for python machine learning       |
|           tutorials.                                          |
|                                                               |
|  ⏰ Alert: Reminder alert! You asked me to: study.            |
|                                                               |
+---------------------------------------------------------------+
|  [ 🎙️ Speak ] [ Type a command here...             ] [ Send ] |
|                                             [ ] Mute Voice    |
+---------------------------------------------------------------+
```

For instructions on adding screenshots, see [assets/screenshots/README.md](file:///c:/Users/Arnav%20Sharma/Desktop/Resume/Internship/Oaisis%20Info%20Tech%20Python%20Programming/ArnavSharma_Task1/assets/screenshots/README.md).

---

## 15. Error Handling & Troubleshooting

| Issue / Error | Root Cause | Solution |
| :--- | :--- | :--- |
| **"Microphone is unavailable"** | No microphone detected or audio permissions denied. | Assistant automatically defaults to keyboard input. You can type commands in the text box. Check Windows Sound settings. |
| **"Speech recognition service unavailable"** | Google Speech Recognition API unreachable due to network outage. | Verify your internet connection. You can use `--text-only` mode while offline. |
| **"OpenWeatherMap API key is not configured"** | Missing `OPENWEATHER_API_KEY` in `.env`. | Create a `.env` file from `.env.example` and add your free key from [openweathermap.org](https://openweathermap.org). |
| **"SMTP authentication failed"** | Standard Gmail password used instead of an App Password. | Generate a 16-character App Password at [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords). |
| **"pyttsx3 engine initialization error"** | Missing SAPI5 on Windows or eSpeak on Linux. | On Ubuntu/Debian, run `sudo apt-get install libespeak1`. On Windows, ensure Windows Audio service is running. |

---

## 16. Privacy, Data Handling & Security Considerations

Privacy and data safety are foundational to this project:

1. **Zero Persistent Audio Recording**:
   - Voice input is captured exclusively in a volatile in-memory buffer by `SpeechRecognition`.
   - Audio is streamed to the speech recognizer and **immediately discarded**. No audio files (.wav, .mp3) are written to disk.
2. **Credential Protection**:
   - Sensitive credentials (API keys, email addresses, passwords) are loaded exclusively through environment variables using `.env`.
   - The `.gitignore` file strictly excludes `.env` and sensitive key formats from being committed to Git.
3. **Log Sanitization**:
   - Application logs (`logs/assistant.log`) pass through a custom `SanitizedFilter` that scrubs passwords, API keys, and email addresses before writing to disk.
4. **Voice Confirmation Gate**:
   - Outbound actions (such as sending emails) require explicit voice or text confirmation before execution.

---

## 17. Future Enhancements

- [ ] **Offline Wake-Word Detection**: Integrate Porcupine or Snowboy for local low-power wake-word activation.
- [ ] **Local LLM Integration**: Incorporate a quantized local model (via Ollama or llama.cpp) for conversational dialogue.
- [ ] **Smart Home Automation**: Add MQTT / Home Assistant integration to control smart lights and smart plugs.
- [ ] **Calendar Synchronization**: Connect Google Calendar API to read and create daily agenda events.

---

## 18. Author & Submission Information

- **Developer**: Arnav Sharma
- **Project**: Python Voice Assistant (`ArnavSharma_Task1`)
- **Internship**: Oasis InfoTech Python Programming Internship
- **Evaluation Criteria Met**: 100% of Beginner & Advanced Tier Requirements
- **Repository**: Ready for GitHub Submission



