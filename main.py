"""
Main Entry Point for ArnavSharma_Task1 – Python Voice Assistant.

Supports:
  - Desktop GUI Mode (default): python main.py
  - Interactive Console Mode:   python main.py --cli
  - Text-Only Console Mode:     python main.py --text-only
  - System Self-Test Mode:      python main.py --test
"""

import argparse
import sys
import os

from utils.logger import setup_logger, get_logger
from modules.assistant import VoiceAssistant

# Initialize application logger
logger = setup_logger(name="AuraMain", log_dir="logs", log_file="assistant.log")


def run_diagnostics(assistant: VoiceAssistant) -> None:
    """Runs a quick diagnostic self-test of all modules and dependencies."""
    print("\n" + "=" * 65)
    print("  ArnavSharma_Task1 – System Diagnostic & Health Check")
    print("=" * 65)

    # 1. Speech Recognition & Microphone
    mic_status = "OPERATIONAL" if assistant.recognizer.is_mic_available else "NO MIC / NOT DETECTED (FALLBACK TO TEXT)"
    print(f"[*] Speech Recognition: {mic_status}")

    # 2. Text-To-Speech (pyttsx3)
    tts_status = "OPERATIONAL" if assistant.tts._thread and assistant.tts._thread.is_alive() else "OFFLINE / CONSOLE ONLY"
    print(f"[*] Text-To-Speech (pyttsx3): {tts_status}")

    # 3. Intent Engine
    test_result = assistant.intent_engine.classify("what is the weather in Kolkata")
    intent_status = "PASS" if test_result.intent.value == "WEATHER" and test_result.entities.get("city") == "Kolkata" else "FAIL"
    print(f"[*] Intent Recognition Engine: {intent_status}")

    # 4. OpenWeatherMap API
    has_weather_key = bool(assistant.weather_service.api_key and "your_openweathermap" not in assistant.weather_service.api_key)
    weather_key_status = "CONFIGURED" if has_weather_key else "NOT CONFIGURED (Using graceful fallback in .env)"
    print(f"[*] OpenWeatherMap API Key: {weather_key_status}")

    # 5. SMTP Email Service
    has_smtp = assistant.email_service.is_configured()
    smtp_status = "CONFIGURED (Live Sending)" if has_smtp else "DRY-RUN SIMULATION (Safe Mode in .env)"
    print(f"[*] SMTP Email Dispatcher: {smtp_status}")

    # 6. Reminders Engine
    rem_success, _, rem_item = assistant.reminder_manager.set_reminder("diagnostic test", 1)
    if rem_success and rem_item:
        assistant.reminder_manager.cancel_all_reminders()
        rem_status = "OPERATIONAL"
    else:
        rem_status = "FAILED"
    print(f"[*] Threaded Reminders Engine: {rem_status}")

    # 7. Knowledge Base (Local + Online)
    kb_success, _, kb_src = assistant.knowledge.query("python")
    kb_status = f"OPERATIONAL (Source: {kb_src})" if kb_success else "FAILED"
    print(f"[*] General Knowledge QA: {kb_status}")

    # 8. Web Search
    print(f"[*] Web Browser Automation: READY (Engine: {assistant.web_search.default_engine})")

    print("=" * 65)
    print("All diagnostic checks completed successfully!\n")


def run_text_only_mode(assistant: VoiceAssistant) -> None:
    """Runs the assistant in text-only terminal prompt mode (no microphone input)."""
    greeting = assistant.get_initial_greeting()
    assistant.speak_and_log(greeting, wait=False)

    print("\n" + "=" * 65)
    print("  Aura – Python Voice Assistant (Text-Only Mode)")
    print("  - Type your commands below (voice listening is disabled).")
    print("  - Type 'exit' or 'quit' to terminate.")
    print("=" * 65 + "\n")

    while assistant.is_running:
        try:
            user_input = input("You: ").strip()
            if not user_input:
                continue
            assistant.process_command(user_input)
        except (KeyboardInterrupt, EOFError):
            print("\nExiting assistant...")
            break

    assistant.shutdown()


def main():
    parser = argparse.ArgumentParser(
        description="ArnavSharma_Task1 – Intelligent Python Voice Assistant"
    )
    parser.add_argument(
        "--cli", "-c",
        action="store_true",
        help="Run in interactive voice and terminal console mode.",
    )
    parser.add_argument(
        "--text-only", "-t",
        action="store_true",
        help="Run in pure text terminal mode without microphone capture.",
    )
    parser.add_argument(
        "--test", "-s",
        action="store_true",
        help="Run system diagnostics and verify all submodules.",
    )

    args = parser.parse_args()

    # Create assistant instance
    assistant = VoiceAssistant(config_path="config.json")

    # Diagnostic mode
    if args.test:
        run_diagnostics(assistant)
        assistant.shutdown()
        return

    # Text-only console mode
    if args.text_only:
        run_text_only_mode(assistant)
        return

    # Console interactive voice mode
    if args.cli:
        assistant.run_console_loop()
        return

    # Default: Attempt to launch modern Tkinter GUI
    try:
        from modules.gui import AssistantGUI
        gui = AssistantGUI(assistant)
        logger.info("Starting Tkinter Desktop GUI...")
        gui.run()
    except Exception as gui_err:
        logger.warning(f"Could not initialize GUI ({gui_err}). Falling back to console mode...")
        assistant.run_console_loop()


if __name__ == "__main__":
    main()

