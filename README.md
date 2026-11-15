
<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&height=220&color=0:090B1A,50:302060,100:00C6FF&text=AURA&fontSize=85&fontColor=FFFFFF&fontAlignY=38&desc=PYTHON%20VOICE%20ASSISTANT&descAlignY=60&descSize=18&animation=fadeIn" width="100%"/>

### 🎙️ An Intelligent Desktop Voice Assistant

**Listen · Understand · Respond · Automate**

<br/>

<img src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&weight=500&size=16&duration=3000&pause=1000&color=00D9FF&center=true&vCenter=true&width=650&lines=Your+Personal+Python+Voice+Assistant;Natural+Language+Understanding;Offline+Text-to-Speech+Engine;Smart+Reminders+%7C+Weather+%7C+Email+Automation" />

<br/>

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-9B59FF?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![Internship](https://img.shields.io/badge/Oasis-InfoTech-00C6FF?style=for-the-badge)](https://oasisinfobyte.com/)
[![Tests](https://img.shields.io/badge/Tests-22_Passed-2ECC71?style=for-the-badge)]()

<br/>

<img src="https://img.shields.io/badge/GUI-Tkinter-7B61FF?style=flat-square"/>
<img src="https://img.shields.io/badge/TTS-pyttsx3-00C6FF?style=flat-square"/>
<img src="https://img.shields.io/badge/NLU-Custom_Engine-9B59FF?style=flat-square"/>
<img src="https://img.shields.io/badge/Platform-Cross_Platform-FFFFFF?style=flat-square"/>

</div>

---

<div align="center">

## ✦ THE PROJECT

</div>

**Aura** is a modular Python-powered desktop voice assistant designed to bridge the gap between basic command-based automation and intelligent conversational interaction.

Built as part of the **Oasis InfoTech Python Programming Internship**, Aura combines speech recognition, Natural Language Understanding, offline text-to-speech, and practical desktop automation.

It supports both beginner and advanced project requirements through a modular, extensible architecture.

<div align="center">

| 🎙️ Voice | 🧠 Intelligence | ⚡ Automation |
|:---:|:---:|:---:|
| Speech Recognition | Intent Detection | Email Automation |
| Offline TTS | Entity Extraction | Smart Reminders |
| Typed Fallback | Conversational Flow | Desktop Launcher |

</div>

---

## ◈ 01 — FEATURES

<div align="center">

### Core Capabilities

</div>

| Feature | Description | Status |
|:---|:---|:---:|
| 🎙️ Speech Recognition | Microphone input using SpeechRecognition and PyAudio | ✅ |
| 🔊 Offline TTS | Natural spoken responses using pyttsx3 | ✅ |
| 🧠 NLU Engine | Token similarity, regex extraction and semantic scoring | ✅ |
| 📧 Email Automation | Multi-turn email drafting with confirmation | ✅ |
| ⏰ Voice Reminders | Non-blocking background reminder system | ✅ |
| 🌦️ Live Weather | OpenWeatherMap API integration | ✅ |
| 🌐 Web Search | Google, Bing, YouTube and GitHub search | ✅ |
| 📚 Knowledge QA | Offline knowledge base and Wikipedia integration | ✅ |
| 🖥️ Desktop Launcher | Opens native desktop applications | ✅ |
| ⚙️ Custom Commands | User-defined commands through config.json | ✅ |
| 🔍 Diagnostics | Automated self-test and system status | ✅ |
| 🪟 Desktop GUI | Dark-themed Tkinter interface | ✅ |

### Interface Highlights

- Interactive chat bubbles
- Quick-action command chips
- Microphone controls
- Typed command fallback
- Voice mute functionality
- Real-time assistant responses

---

## ◈ 02 — SYSTEM ARCHITECTURE

<div align="center">

### Modular Architecture

</div>

```text
                  ┌────────────────────────────┐
                  │        USER INPUT          │
                  │                            │
                  │   Voice / Keyboard / GUI   │
                  └──────────────┬─────────────┘
                                 │
                                 ▼
                  ┌────────────────────────────┐
                  │     ASSISTANT ENGINE       │
                  │                            │
                  │   Dialog State Management  │
                  │   Request Orchestration    │
                  └──────────────┬─────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
              ▼                  ▼                  ▼
      ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
      │  SPEECH I/O  │   │  NLU ENGINE  │   │  SERVICES    │
      │              │   │              │   │              │
      │ Speech-to-   │   │ Intent       │   │ Weather      │
      │ Text         │   │ Detection    │   │ Email        │
      │              │   │              │   │ Reminders    │
      │ Text-to-     │   │ Entity       │   │ Knowledge    │
      │ Speech       │   │ Extraction   │   │ Web Search   │
      └──────────────┘   └──────────────┘   └──────────────┘
                                 │
                                 ▼
                  ┌────────────────────────────┐
                  │      CONFIGURATION         │
                  │                            │
                  │   config.json              │
                  │   .env                     │
                  │   Sanitized Logs           │
                  └────────────────────────────┘
```

---

## ◈ 03 — TECHNOLOGY STACK

<div align="center">

### Built With

<img src="https://skillicons.dev/icons?i=python,git,github,vscode&theme=dark" />

</div>

| Component | Technology |
|:---|:---|
| Programming Language | Python 3.9+ |
| Speech Recognition | SpeechRecognition, PyAudio |
| Text-to-Speech | pyttsx3 |
| Desktop GUI | Tkinter, ttk |
| API Integration | Requests |
| Environment Management | python-dotenv |
| Knowledge Retrieval | Wikipedia API |
| Concurrency | Threading, Queue |
| Testing | Python unittest |

---

## ◈ 04 — PROJECT STRUCTURE

```text
ArnavSharma_Task1/
│
├── main.py
├── config.json
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
│
├── modules/
│   ├── __init__.py
│   ├── assistant.py
│   ├── speech.py
│   ├── intent.py
│   ├── weather.py
│   ├── email_service.py
│   ├── reminders.py
│   ├── web_search.py
│   ├── knowledge.py
│   ├── app_launcher.py
│   └── gui.py
│
├── utils/
│   ├── __init__.py
│   ├── helpers.py
│   └── logger.py
│
├── tests/
│   ├── __init__.py
│   └── test_assistant.py
│
└── assets/
    └── screenshots/
```

---

## ◈ 05 — INSTALLATION

### 1. Clone the Repository

```bash
git clone https://github.com/ArnavSharma-IND/ArnavSharma_Task1.git

cd ArnavSharma_Task1
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

### 3. Activate Environment

**Windows**

```powershell
.\.venv\Scripts\activate
```

**Linux / macOS**

```bash
source .venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## ◈ 06 — CONFIGURATION

### OpenWeatherMap API

1. Create an account at [OpenWeatherMap](https://home.openweathermap.org/users/sign_up).
2. Generate an API key.
3. Copy `.env.example` to `.env`.
4. Add your API key:

```env
OPENWEATHER_API_KEY=your_api_key
```

### Gmail SMTP Configuration

1. Enable Google 2-Step Verification.
2. Generate an App Password.
3. Configure your `.env`:

```env
SMTP_EMAIL=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=True
```

**Security:** Never commit your `.env` file or expose credentials in your repository.

---

## ◈ 07 — RUNNING AURA

| Mode | Command | Purpose |
|:---|:---|:---|
| Desktop GUI | `python main.py` | Launch graphical interface |
| CLI | `python main.py --cli` | Interactive voice console |
| Text Only | `python main.py --text-only` | Keyboard interaction |
| Diagnostics | `python main.py --test` | Run system tests |

---

## ◈ 08 — COMMAND SHOWCASE

<div align="center">

### Talk to Aura

</div>

| You Say | Aura Responds |
|:---|:---|
| "Hello Aura" | Personalized greeting |
| "What time is it?" | Current time |
| "What's today's date?" | Current date |
| "What's the weather in Kolkata?" | Live weather information |
| "Remind me to study after 10 minutes" | Creates a reminder |
| "What are my reminders?" | Lists active reminders |
| "Search Python tutorials" | Opens browser search |
| "Open Calculator" | Launches Calculator |
| "Who is Albert Einstein?" | General knowledge response |
| "Send an email to Arnav" | Starts guided email workflow |
| "Goodbye" | Terminates the assistant |

---

## ◈ 09 — USER INTERFACE

<div align="center">

### Desktop Experience

<!-- Add your actual screenshots inside assets/screenshots/ -->

<img src="https://placehold.co/900x480/101426/00D9FF?text=AURA+DESKTOP+INTERFACE" width="90%" alt="Aura Desktop GUI placeholder"/>

<sub>Replace the placeholder above with your actual application screenshot.</sub>

</div>

---

## ◈ 10 — PRIVACY & SECURITY

Aura incorporates several privacy-conscious design choices:

- **No persistent audio recordings:** Audio is processed in memory and discarded.
- **Environment-based secrets:** API keys and SMTP credentials are stored in `.env`.
- **Sanitized logs:** Sensitive information is redacted before logging.
- **Confirmation-based email:** Email transmission requires explicit user confirmation.
- **Graceful fallback:** Missing hardware and unavailable APIs are handled without crashing.

---

## ◈ 11 — TESTING & RELIABILITY

<div align="center">

<img src="https://img.shields.io/badge/Automated_Tests-22_Passed-2ECC71?style=for-the-badge&logo=pytest&logoColor=white"/>

</div>

Run the diagnostic suite:

```bash
python main.py --test
```

The project includes 22 unit tests covering the assistant's core functionality.

---

## ◈ 12 — FUTURE ROADMAP

| Enhancement | Status |
|:---|:---:|
| Offline Wake-Word Detection | 🔜 Planned |
| Local LLM Integration | 🔜 Planned |
| Smart Home Automation | 🔜 Planned |
| Google Calendar Synchronization | 🔜 Planned |

---

## ◈ 13 — DEVELOPER

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=rect&height=100&color=0:17142D,100:31215B&text=ARNAV%20SHARMA&fontSize=35&fontColor=FFFFFF&fontAlignY=55"/>

### Arnav Sharma

**Python Developer | Computer Science & Artificial Intelligence**

<br/>

[![GitHub](https://img.shields.io/badge/GitHub-ArnavSharma--IND-181717?style=for-the-badge&logo=github)](https://github.com/ArnavSharma-IND)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=for-the-badge&logo=linkedin)](https://www.linkedin.com/in/arnav-sharma-dev/)

<br/>

**Project:** Aura — Python Voice Assistant

**Internship:** Oasis InfoTech — Python Programming

**Submission:** Beginner & Advanced Tier Requirements

<br/>

<img src="https://capsule-render.vercel.app/api?type=waving&height=120&color=0:090B1A,50:302060,100:00C6FF&section=footer"/>

</div>
