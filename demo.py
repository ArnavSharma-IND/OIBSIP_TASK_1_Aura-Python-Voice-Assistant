"""
Live Interactive Demo Script for ArnavSharma_Task1 – Python Voice Assistant.
Executes an automated, real-time live demonstration of all Beginner and Advanced Tier features
with synchronized voice synthesis (TTS) playback and terminal output.
"""

import sys
import time
from modules.assistant import VoiceAssistant
from utils.logger import setup_logger

# Initialize logger
logger = setup_logger(name="LiveDemo", log_dir="logs", log_file="assistant.log")


def print_banner(text: str) -> None:
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_step(step_num: int, title: str) -> None:
    print(f"\n[DEMO STEP {step_num}] {title}")
    print("-" * 50)


def run_live_demo():
    print_banner("Aura – Python Voice Assistant (LIVE SYSTEM DEMO)")
    print("Initializing assistant core, audio speech engines, and NLP models...")

    assistant = VoiceAssistant(config_path="config.json")
    # Enable audio feedback
    assistant.tts.set_muted(False)

    time.sleep(1.0)

    # 1. Startup & Greeting
    print_step(1, "Startup & Time-Aware Personalized Greeting")
    greeting = assistant.get_initial_greeting()
    assistant.speak_and_log(greeting, wait=True)
    time.sleep(0.5)

    # 2. Beginner Tier: Current Time
    print_step(2, "Beginner Tier: Current Time Inquiry")
    q_time = "what time is it"
    print(f"👤 User: \"{q_time}\"")
    assistant.process_command(q_time)
    time.sleep(1.5)

    # 3. Beginner Tier: Current Date
    print_step(3, "Beginner Tier: Current Date Inquiry")
    q_date = "what is today's date"
    print(f"👤 User: \"{q_date}\"")
    assistant.process_command(q_date)
    time.sleep(1.5)

    # 4. Beginner Tier: Web Search Automation
    print_step(4, "Beginner Tier: Web Search & Browser Navigation")
    q_search = "search for Python machine learning tutorials"
    print(f"👤 User: \"{q_search}\"")
    assistant.process_command(q_search)
    time.sleep(2.0)

    # 5. Advanced Tier: Natural Language Understanding (Free-form request)
    print_step(5, "Advanced Tier: Free-Form Natural Language Understanding")
    q_freeform = "could you please let me know what the hour is right now"
    print(f"👤 User (Free-Form): \"{q_freeform}\"")
    assistant.process_command(q_freeform)
    time.sleep(1.5)

    # 6. Advanced Tier: Live Weather Forecasting
    print_step(6, "Advanced Tier: Live Weather Information")
    q_weather = "what is the weather in Kolkata"
    print(f"👤 User: \"{q_weather}\"")
    assistant.process_command(q_weather)
    time.sleep(2.5)

    # 7. Advanced Tier: Non-Blocking Background Thread Reminder (5-second live test)
    print_step(7, "Advanced Tier: Voice Reminders (Live 5-second countdown & chime)")
    q_rem = "remind me to check the project report in 5 seconds"
    print(f"👤 User: \"{q_rem}\"")
    assistant.process_command(q_rem)

    print("\n⏳ Assistant is non-blocking! Asking for active reminders while timer runs...")
    time.sleep(1.5)
    q_remlist = "what are my reminders"
    print(f"👤 User: \"{q_remlist}\"")
    assistant.process_command(q_remlist)

    print("\n⏳ Waiting for the 5-second reminder timer to fire...")
    time.sleep(4.5)  # Wait for background thread reminder to fire chime and voice alert

    # 8. Advanced Tier: General Knowledge QA (Local + Wikipedia)
    print_step(8, "Advanced Tier: General Knowledge QA (Offline Encyclopedia)")
    q_qa = "who is Albert Einstein"
    print(f"👤 User: \"{q_qa}\"")
    assistant.process_command(q_qa)
    time.sleep(3.0)

    # 9. Advanced Tier: Custom Commands from config.json
    print_step(9, "Advanced Tier: Custom Commands from config.json")
    q_custom = "who created you"
    print(f"👤 User: \"{q_custom}\"")
    assistant.process_command(q_custom)
    time.sleep(2.0)

    # 10. Advanced Tier: Desktop Application Launcher
    print_step(10, "Desktop Application Launcher")
    q_app = "open calculator"
    print(f"👤 User: \"{q_app}\"")
    assistant.process_command(q_app)
    time.sleep(2.0)

    # 11. Advanced Tier: Multi-turn Email Automation with Confirmation
    print_step(11, "Advanced Tier: Multi-Turn Email Automation & Confirmation")
    print("👤 User: \"send an email\"")
    assistant.process_command("send an email")
    time.sleep(1.5)

    print("👤 User: \"arnav\"")
    assistant.process_command("arnav")
    time.sleep(1.5)

    print("👤 User: \"Internship Task 1 Completion\"")
    assistant.process_command("Internship Task 1 Completion")
    time.sleep(1.5)

    print("👤 User: \"All requirements have been met and tested.\"")
    assistant.process_command("All requirements have been met and tested.")
    time.sleep(2.0)

    print("👤 User (Confirm): \"yes\"")
    assistant.process_command("yes")
    time.sleep(2.5)

    # 12. Graceful Voice Exit
    print_step(12, "Graceful Exit")
    q_exit = "goodbye"
    print(f"👤 User: \"{q_exit}\"")
    assistant.process_command(q_exit)
    time.sleep(1.5)

    assistant.shutdown()
    print_banner("LIVE DEMO COMPLETED SUCCESSFULLY")


if __name__ == "__main__":
    run_live_demo()

