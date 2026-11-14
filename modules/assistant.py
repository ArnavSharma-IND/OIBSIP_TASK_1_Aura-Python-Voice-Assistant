"""
Core Assistant Orchestrator Module for ArnavSharma_Task1.
Coordinates speech recognition, natural language intent classification,
dialog state management, and multi-service execution.
"""

import json
import os
import sys
from datetime import datetime
from typing import Any, Callable, Dict, Optional, Tuple

from dotenv import load_dotenv

from utils.helpers import (
    format_natural_date,
    format_natural_time,
    get_time_of_day_greeting,
    normalize_text,
)
from utils.logger import get_logger

from .app_launcher import AppLauncher
from .email_service import EmailService
from .intent import IntentEngine, IntentResult, IntentType
from .knowledge import KnowledgeService
from .reminders import ReminderManager
from .speech import SpeechRecognizer, TTSManager
from .weather import WeatherService
from .web_search import WebSearchService

logger = get_logger("VoiceAssistant")


# Dialog States for multi-turn conversations
STATE_IDLE = "IDLE"
STATE_EMAIL_RECIPIENT = "AWAITING_EMAIL_RECIPIENT"
STATE_EMAIL_SUBJECT = "AWAITING_EMAIL_SUBJECT"
STATE_EMAIL_BODY = "AWAITING_EMAIL_BODY"
STATE_EMAIL_CONFIRM = "AWAITING_EMAIL_CONFIRM"
STATE_ADD_COMMAND_RESPONSE = "AWAITING_COMMAND_RESPONSE"


class VoiceAssistant:
    """
    Main controller for the Python Voice Assistant.
    Coordinates all submodules, speech, dialog states, and execution loops.
    """

    def __init__(
        self,
        config_path: str = "config.json",
        ui_callback: Optional[Callable[[str, str], None]] = None,
    ):
        # Load environment variables
        load_dotenv()

        self.config_path = config_path
        self.ui_callback = ui_callback  # Callback: (sender: "User"|"Assistant", text: str)
        self.config = self._load_config()

        self.assistant_name = os.getenv("ASSISTANT_NAME", self.config.get("assistant_name", "Aura"))
        self.user_name = os.getenv("ASSISTANT_USER_NAME", self.config.get("user_name", "Arnav"))
        self.wake_word = self.config.get("wake_word", "hey assistant").lower()
        self.wake_word_enabled = self.config.get("wake_word_enabled", False)

        # Dialog state tracking
        self.state = STATE_IDLE
        self.pending_email: Dict[str, str] = {}
        self.pending_command_trigger: Optional[str] = None
        self.is_running = True

        # Initialize Sub-services
        self._init_services()

    def _load_config(self) -> Dict[str, Any]:
        """Loads assistant configuration from config.json."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as err:
                logger.error(f"Failed to parse config file '{self.config_path}': {err}")
        return {}

    def _save_config(self) -> None:
        """Saves current configuration back to config.json."""
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)
            logger.info("Configuration successfully written to disk.")
        except Exception as err:
            logger.error(f"Failed to save configuration: {err}")

    def _init_services(self) -> None:
        """Initializes all service modules with configuration parameters."""
        speech_cfg = self.config.get("speech", {})
        weather_cfg = self.config.get("weather", {})
        email_cfg = self.config.get("email", {})

        # 1. Text-To-Speech Manager
        self.tts = TTSManager(
            voice_index=speech_cfg.get("voice_index", 0),
            rate=speech_cfg.get("speech_rate", 180),
            volume=speech_cfg.get("speech_volume", 1.0),
        )

        # 2. Speech Recognizer
        self.recognizer = SpeechRecognizer(
            energy_threshold=speech_cfg.get("mic_energy_threshold", 300),
            dynamic_energy_threshold=speech_cfg.get("mic_dynamic_energy_threshold", True),
            listen_timeout=speech_cfg.get("listen_timeout", 5),
            phrase_time_limit=speech_cfg.get("phrase_time_limit", 8),
        )

        # 3. Intent Engine
        custom_cmds = self.config.get("custom_commands", {})
        self.intent_engine = IntentEngine(custom_commands=custom_cmds)

        # 4. Live Weather Service
        self.weather_service = WeatherService(
            default_city=weather_cfg.get("default_city", "Kolkata"),
            units=weather_cfg.get("units", "metric"),
        )

        # 5. Email Automation Service
        self.email_service = EmailService(
            smtp_server=email_cfg.get("smtp_server", "smtp.gmail.com"),
            smtp_port=email_cfg.get("smtp_port", 587),
            use_tls=email_cfg.get("use_tls", True),
            contacts=email_cfg.get("contacts", {}),
        )

        # 6. Reminder Manager
        self.reminder_manager = ReminderManager(
            alert_callback=self._handle_reminder_alert,
            sound_enabled=True,
        )

        # 7. Web Search Service
        self.web_search = WebSearchService(
            default_engine=self.config.get("web_search", {}).get("default_engine", "google")
        )

        # 8. Knowledge QA Service
        self.knowledge = KnowledgeService(use_online=True)

        # 9. Desktop App Launcher
        self.app_launcher = AppLauncher()

    def _handle_reminder_alert(self, alert_text: str) -> None:
        """Invoked asynchronously when a reminder timer fires."""
        print(f"\n[ALERT] {alert_text}")
        if self.ui_callback:
            self.ui_callback("Assistant", f"⏰ {alert_text}")
        self.tts.speak(alert_text, wait=False)

    def speak_and_log(self, text: str, wait: bool = False) -> None:
        """Sends response to UI callback and TTS synthesizer."""
        if self.ui_callback:
            self.ui_callback("Assistant", text)
        self.tts.speak(text, wait=wait)

    def get_initial_greeting(self) -> str:
        """Generates startup greeting and onboarding prompt."""
        time_greeting = get_time_of_day_greeting(self.user_name)
        welcome = (
            f"{time_greeting} I am {self.assistant_name}, your personal Python voice assistant. "
            f"You can talk to me or type your request below. Try asking 'what time is it', "
            f"'weather in Kolkata', 'remind me to study in 10 minutes', or say 'help' for more options."
        )
        return welcome

    def add_custom_command(self, trigger: str, response: str) -> str:
        """Adds a custom spoken command and persists it in config.json."""
        clean_trig = trigger.strip().lower()
        if not clean_trig or not response.strip():
            return "Command trigger and response cannot be empty."

        customs = self.config.get("custom_commands", {})
        customs[clean_trig] = response.strip()
        self.config["custom_commands"] = customs
        self._save_config()
        self.intent_engine.update_custom_commands(customs)
        msg = f"Custom command '{clean_trig}' has been successfully added."
        logger.info(msg)
        return msg

    def process_command(self, query: str) -> str:
        """
        Processes a single user input string (spoken or typed).
        Handles multi-turn dialog states and invokes appropriate services.

        Returns:
            Assistant's spoken response string.
        """
        clean_query = query.strip()
        if not clean_query:
            return ""

        logger.info(f"Processing command: '{clean_query}' in state: {self.state}")

        # Post user query to UI if callback present
        if self.ui_callback:
            self.ui_callback("User", clean_query)

        # Check wake-word filter if enabled and idle
        if self.wake_word_enabled and self.state == STATE_IDLE:
            q_norm = normalize_text(clean_query)
            if self.wake_word in q_norm:
                # Strip wake-word and proceed
                clean_query = re.sub(re.escape(self.wake_word), "", q_norm).strip()
                if not clean_query:
                    resp = f"Yes {self.user_name}, I am listening!"
                    self.speak_and_log(resp)
                    return resp
            else:
                # Wake word required but missing
                return ""

        # ----------------------------------------------------------------------
        # Multi-turn Dialog State Machine
        # ----------------------------------------------------------------------
        if self.state == STATE_EMAIL_RECIPIENT:
            recipient = self.email_service.resolve_recipient(clean_query)
            if not recipient:
                resp = f"I could not resolve '{clean_query}'. Please state a valid email address or contact name."
                self.speak_and_log(resp)
                return resp
            self.pending_email["recipient"] = recipient
            self.state = STATE_EMAIL_SUBJECT
            resp = f"Got it, sending to {recipient}. What is the subject of the email?"
            self.speak_and_log(resp)
            return resp

        elif self.state == STATE_EMAIL_SUBJECT:
            self.pending_email["subject"] = clean_query
            self.state = STATE_EMAIL_BODY
            resp = f"Subject set to '{clean_query}'. What message would you like to send?"
            self.speak_and_log(resp)
            return resp

        elif self.state == STATE_EMAIL_BODY:
            self.pending_email["body"] = clean_query
            self.state = STATE_EMAIL_CONFIRM
            recip = self.pending_email.get("recipient", "")
            subj = self.pending_email.get("subject", "")
            resp = (
                f"I am ready to send your email to {recip} with subject '{subj}'. "
                f"The message is: '{clean_query}'. Would you like me to send it? Please say 'yes' to send or 'no' to cancel."
            )
            self.speak_and_log(resp)
            return resp

        elif self.state == STATE_EMAIL_CONFIRM:
            norm_ans = normalize_text(clean_query)
            if any(y in norm_ans for y in ["yes", "send", "sure", "confirm", "go ahead"]):
                recip = self.pending_email.get("recipient", "")
                subj = self.pending_email.get("subject", "")
                body = self.pending_email.get("body", "")
                self.state = STATE_IDLE
                self.pending_email = {}
                success, feedback = self.email_service.send_email(recip, subj, body)
                self.speak_and_log(feedback)
                return feedback
            else:
                self.state = STATE_IDLE
                self.pending_email = {}
                resp = "Email draft has been cancelled."
                self.speak_and_log(resp)
                return resp

        elif self.state == STATE_ADD_COMMAND_RESPONSE:
            trigger = self.pending_command_trigger or "custom command"
            resp = self.add_custom_command(trigger, clean_query)
            self.state = STATE_IDLE
            self.pending_command_trigger = None
            self.speak_and_log(resp)
            return resp

        # ----------------------------------------------------------------------
        # Single-turn Intent Classification & Execution
        # ----------------------------------------------------------------------
        result: IntentResult = self.intent_engine.classify(clean_query)
        logger.info(f"Classified Intent: {result.intent.value} (confidence: {result.confidence})")

        response_text = ""

        # 1. Custom Command
        if result.intent == IntentType.CUSTOM_COMMAND:
            custom_val = result.matched_custom_response
            if isinstance(custom_val, dict):
                act = custom_val.get("action", "")
                target = custom_val.get("target", "")
                resp_msg = custom_val.get("response", "Executing custom command.")
                if act == "open_url" and target:
                    self.web_search.open_url(target)
                elif act == "launch_app" and target:
                    self.app_launcher.launch(target)
                response_text = resp_msg
            else:
                response_text = str(custom_val)

        # 2. Exit
        elif result.intent == IntentType.EXIT:
            response_text = f"Goodbye {self.user_name}! Have a wonderful day."
            self.is_running = False
            self.speak_and_log(response_text, wait=True)
            return response_text

        # 3. Greeting
        elif result.intent == IntentType.GREETING:
            response_text = get_time_of_day_greeting(self.user_name)

        # 4. Time Inquiry
        elif result.intent == IntentType.TIME:
            current_time = format_natural_time()
            response_text = f"The current time is {current_time}."

        # 5. Date Inquiry
        elif result.intent == IntentType.DATE:
            current_date = format_natural_date()
            response_text = f"Today is {current_date}."

        # 6. Live Weather Inquiry
        elif result.intent == IntentType.WEATHER:
            city = result.entities.get("city")
            success, speech_out, _ = self.weather_service.get_weather(city)
            response_text = speech_out

        # 7. Web Search
        elif result.intent == IntentType.WEB_SEARCH:
            query_term = result.entities.get("query", clean_query)
            success, speech_out = self.web_search.search(query_term)
            response_text = speech_out

        # 8. Email Automation
        elif result.intent == IntentType.SEND_EMAIL:
            recip = result.entities.get("recipient")
            subj = result.entities.get("subject")
            body = result.entities.get("body")

            self.pending_email = {}
            if recip:
                resolved = self.email_service.resolve_recipient(recip)
                if resolved:
                    self.pending_email["recipient"] = resolved
            if subj:
                self.pending_email["subject"] = subj
            if body:
                self.pending_email["body"] = body

            # Determine next missing slot
            if "recipient" not in self.pending_email:
                self.state = STATE_EMAIL_RECIPIENT
                response_text = "Who would you like to send this email to? You can say a contact name or email address."
            elif "subject" not in self.pending_email:
                self.state = STATE_EMAIL_SUBJECT
                response_text = f"Sending email to {self.pending_email['recipient']}. What is the subject?"
            elif "body" not in self.pending_email:
                self.state = STATE_EMAIL_BODY
                response_text = f"Subject is '{self.pending_email['subject']}'. What message would you like to send?"
            else:
                self.state = STATE_EMAIL_CONFIRM
                r = self.pending_email['recipient']
                s = self.pending_email['subject']
                b = self.pending_email['body']
                response_text = (
                    f"I am ready to send your email to {r} with subject '{s}'. "
                    f"The message is: '{b}'. Would you like me to send it? Say yes or no."
                )

        # 9. Set Voice Reminder
        elif result.intent == IntentType.SET_REMINDER:
            task = result.entities.get("task", "general reminder")
            secs = result.entities.get("seconds", 60)
            success, speech_out, _ = self.reminder_manager.set_reminder(task, secs)
            response_text = speech_out

        # 10. List Active Reminders
        elif result.intent == IntentType.LIST_REMINDERS:
            _, speech_out = self.reminder_manager.list_active_reminders()
            response_text = speech_out

        # 11. Cancel Reminders
        elif result.intent == IntentType.CANCEL_REMINDER:
            response_text = self.reminder_manager.cancel_all_reminders()

        # 12. Desktop App Launcher
        elif result.intent == IntentType.OPEN_APP:
            app_name = result.entities.get("app_name", "")
            success, speech_out = self.app_launcher.launch(app_name)
            response_text = speech_out

        # 13. General Knowledge QA
        elif result.intent == IntentType.KNOWLEDGE_QA:
            topic = result.entities.get("topic", clean_query)
            success, speech_out, _ = self.knowledge.query(topic)
            response_text = speech_out

        # 14. Help Menu
        elif result.intent == IntentType.HELP:
            response_text = (
                f"Here is what I can do for you, {self.user_name}: "
                f"1. Tell time and date. "
                f"2. Fetch live weather updates. "
                f"3. Set voice reminders and timers. "
                f"4. Search the web and open websites. "
                f"5. Send automated emails via SMTP. "
                f"6. Answer general knowledge questions. "
                f"7. Open desktop applications like Calculator or Notepad. "
                f"8. Run your custom commands from config.json. "
                f"Say 'exit' anytime to quit."
            )

        # 15. System Status
        elif result.intent == IntentType.STATUS:
            active_rems, _ = self.reminder_manager.list_active_reminders()
            mic_status = "Available" if self.recognizer.is_mic_available else "Not Detected"
            response_text = (
                f"Assistant Status: Active and healthy. "
                f"Microphone input is {mic_status}. "
                f"You currently have {active_rems} active reminders."
            )

        # 16. Fallback / Unknown
        else:
            response_text = (
                "I'm sorry, I didn't quite catch that. You can ask for the time, weather, "
                "set a reminder, search the web, or say 'help' to see what I can do."
            )

        self.speak_and_log(response_text)
        return response_text

    def run_console_loop(self) -> None:
        """
        Runs an interactive voice and terminal input loop in the console.
        Listens to microphone; allows fallback to typing if mic is silent or unavailable.
        """
        initial_greeting = self.get_initial_greeting()
        self.speak_and_log(initial_greeting, wait=True)

        print("\n" + "=" * 65)
        print("  Aura – Python Voice Assistant (Console Interactive Mode)")
        print("  - Speak into your microphone, or type your query below.")
        print("  - Type 'exit' or say 'goodbye' to quit.")
        print("=" * 65 + "\n")

        # Calibrate ambient noise on start if mic available
        if self.recognizer.is_mic_available:
            self.recognizer.calibrate_noise(duration=1.0)

        while self.is_running:
            try:
                user_input = None

                # 1. Attempt voice capture if microphone is operational
                if self.recognizer.is_mic_available:
                    print("\n[Listening... Speak now or press Enter to type]")
                    text, err_code, err_msg = self.recognizer.listen(timeout=5, phrase_time_limit=8)

                    if text:
                        user_input = text
                    elif err_code == "UNKNOWN":
                        self.speak_and_log(err_msg)
                        continue
                    elif err_code == "REQUEST_ERROR":
                        self.speak_and_log(err_msg)
                    # TIMEOUT: silent timeout, proceed to prompt

                # 2. Text input prompt fallback
                if not user_input:
                    try:
                        user_input = input("\nYou (Type or press Enter to listen): ").strip()
                    except (EOFError, KeyboardInterrupt):
                        print("\nExiting assistant...")
                        break

                if not user_input:
                    continue

                # Process the input
                self.process_command(user_input)

            except KeyboardInterrupt:
                print("\nAssistant stopped by user.")
                break
            except Exception as loop_err:
                logger.error(f"Error in assistant interaction loop: {loop_err}")

        self.shutdown()

    def shutdown(self) -> None:
        """Shuts down all threads, audio engines, and schedulers."""
        logger.info("Shutting down Voice Assistant...")
        self.is_running = False
        try:
            self.reminder_manager.shutdown()
            self.tts.shutdown()
        except Exception as err:
            logger.debug(f"Error during shutdown: {err}")

