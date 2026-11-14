"""
Comprehensive Unit Test Suite for ArnavSharma_Task1 Voice Assistant.
Tests Beginner and Advanced Tier features including Intent Classification,
Reminders, Natural Language Understanding, Weather, Knowledge, Email, and Helpers.
"""

import os
import unittest
from datetime import datetime

from modules.app_launcher import AppLauncher
from modules.email_service import EmailService
from modules.intent import IntentEngine, IntentType
from modules.knowledge import KnowledgeService
from modules.reminders import ReminderManager
from modules.weather import WeatherService
from utils.helpers import (
    format_duration_readable,
    format_natural_date,
    format_natural_time,
    get_time_of_day_greeting,
    is_valid_email,
    normalize_text,
    parse_duration_seconds,
)
from utils.logger import setup_logger


class TestHelpers(unittest.TestCase):
    """Tests utility functions in utils/helpers.py."""

    def test_normalize_text(self):
        self.assertEqual(normalize_text("  Hello, World!  "), "hello world")
        self.assertEqual(normalize_text("What's the weather???"), "what's the weather")

    def test_natural_time_and_date(self):
        t_str = format_natural_time()
        self.assertTrue("AM" in t_str or "PM" in t_str)

        d_str = format_natural_date()
        self.assertTrue(any(month in d_str for month in [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]))

    def test_time_of_day_greeting(self):
        greeting = get_time_of_day_greeting("Arnav")
        self.assertTrue("Arnav" in greeting)
        self.assertTrue(any(word in greeting for word in ["morning", "afternoon", "evening", "night", "Hello"]))

    def test_parse_duration_seconds(self):
        # Numeric seconds
        self.assertEqual(parse_duration_seconds("30 seconds"), 30)
        self.assertEqual(parse_duration_seconds("1 second"), 1)
        # Minutes
        self.assertEqual(parse_duration_seconds("5 minutes"), 300)
        self.assertEqual(parse_duration_seconds("ten minutes"), 600)
        # Hours
        self.assertEqual(parse_duration_seconds("1 hour"), 3600)
        self.assertEqual(parse_duration_seconds("half an hour"), 1800)
        # Compound
        self.assertEqual(parse_duration_seconds("2 minutes and 30 seconds"), 150)

    def test_format_duration_readable(self):
        self.assertEqual(format_duration_readable(30), "30 seconds")
        self.assertEqual(format_duration_readable(60), "1 minute")
        self.assertEqual(format_duration_readable(300), "5 minutes")
        self.assertEqual(format_duration_readable(3600), "1 hour")

    def test_is_valid_email(self):
        self.assertTrue(is_valid_email("arnav@example.com"))
        self.assertTrue(is_valid_email("john.doe+test@gmail.com"))
        self.assertFalse(is_valid_email("plainaddress"))
        self.assertFalse(is_valid_email("missing@domain"))


class TestIntentRecognition(unittest.TestCase):
    """Tests Natural Language Understanding and Intent Classification."""

    def setUp(self):
        self.engine = IntentEngine(custom_commands={
            "who made you": "Arnav Sharma created me.",
            "secret mission": "Top secret voice automation."
        })

    def test_greetings(self):
        res = self.engine.classify("hello")
        self.assertEqual(res.intent, IntentType.GREETING)

        res2 = self.engine.classify("good morning aura")
        self.assertEqual(res2.intent, IntentType.GREETING)

    def test_time_and_date(self):
        res_time = self.engine.classify("what time is it right now")
        self.assertEqual(res_time.intent, IntentType.TIME)

        res_date = self.engine.classify("what is today's date")
        self.assertEqual(res_date.intent, IntentType.DATE)

    def test_weather_extraction(self):
        res = self.engine.classify("what is the weather in Kolkata")
        self.assertEqual(res.intent, IntentType.WEATHER)
        self.assertEqual(res.entities.get("city"), "Kolkata")

        res_london = self.engine.classify("how is the weather in London")
        self.assertEqual(res_london.intent, IntentType.WEATHER)
        self.assertEqual(res_london.entities.get("city"), "London")

    def test_web_search_extraction(self):
        res = self.engine.classify("search for Python machine learning tutorials")
        self.assertEqual(res.intent, IntentType.WEB_SEARCH)
        self.assertEqual(res.entities.get("query"), "python machine learning tutorials")

        res_google = self.engine.classify("google latest scientific discoveries")
        self.assertEqual(res_google.intent, IntentType.WEB_SEARCH)
        self.assertEqual(res_google.entities.get("query"), "latest scientific discoveries")

    def test_reminder_extraction(self):
        res = self.engine.classify("remind me to study after 10 minutes")
        self.assertEqual(res.intent, IntentType.SET_REMINDER)
        self.assertEqual(res.entities.get("task"), "study")
        self.assertEqual(res.entities.get("seconds"), 600)

        res_short = self.engine.classify("set a reminder for 30 seconds to check the oven")
        self.assertEqual(res_short.intent, IntentType.SET_REMINDER)
        self.assertEqual(res_short.entities.get("seconds"), 30)

    def test_email_extraction(self):
        res = self.engine.classify("send an email to arnav with subject project update")
        self.assertEqual(res.intent, IntentType.SEND_EMAIL)
        self.assertEqual(res.entities.get("recipient"), "arnav")
        self.assertEqual(res.entities.get("subject"), "project update")

    def test_knowledge_qa(self):
        res = self.engine.classify("who is Albert Einstein")
        self.assertEqual(res.intent, IntentType.KNOWLEDGE_QA)
        self.assertIn("albert einstein", res.entities.get("topic", "").lower())

        res_what = self.engine.classify("what is photosynthesis")
        self.assertEqual(res_what.intent, IntentType.KNOWLEDGE_QA)
        self.assertIn("photosynthesis", res_what.entities.get("topic", "").lower())

    def test_app_launch(self):
        res = self.engine.classify("open calculator")
        self.assertEqual(res.intent, IntentType.OPEN_APP)
        self.assertEqual(res.entities.get("app_name"), "calculator")

        res_note = self.engine.classify("launch notepad")
        self.assertEqual(res_note.intent, IntentType.OPEN_APP)
        self.assertEqual(res_note.entities.get("app_name"), "notepad")

    def test_custom_command(self):
        res = self.engine.classify("who made you")
        self.assertEqual(res.intent, IntentType.CUSTOM_COMMAND)
        self.assertEqual(res.matched_custom_response, "Arnav Sharma created me.")

    def test_exit(self):
        res = self.engine.classify("exit")
        self.assertEqual(res.intent, IntentType.EXIT)

        res_bye = self.engine.classify("goodbye")
        self.assertEqual(res_bye.intent, IntentType.EXIT)


class TestReminders(unittest.TestCase):
    """Tests Voice Reminders thread scheduling and listing."""

    def setUp(self):
        self.manager = ReminderManager(sound_enabled=False)

    def tearDown(self):
        self.manager.shutdown()

    def test_set_and_list_reminder(self):
        success, speech, item = self.manager.set_reminder("drink water", 60)
        self.assertTrue(success)
        self.assertIsNotNone(item)
        self.assertIn("1 minute", speech)

        count, list_speech = self.manager.list_active_reminders()
        self.assertEqual(count, 1)
        self.assertIn("drink water", list_speech)

    def test_cancel_reminders(self):
        self.manager.set_reminder("task one", 100)
        self.manager.set_reminder("task two", 200)

        cancel_msg = self.manager.cancel_all_reminders()
        self.assertIn("cancelled", cancel_msg.lower())

        count, _ = self.manager.list_active_reminders()
        self.assertEqual(count, 0)


class TestKnowledgeService(unittest.TestCase):
    """Tests general knowledge answers via local offline database."""

    def setUp(self):
        # Test offline knowledge only
        self.service = KnowledgeService(use_online=False)

    def test_offline_answers(self):
        success, ans, src = self.service.query("python")
        self.assertTrue(success)
        self.assertEqual(src, "offline_kb")
        self.assertIn("Guido van Rossum", ans)

        success2, ans2, src2 = self.service.query("who is Albert Einstein")
        self.assertTrue(success2)
        self.assertEqual(src2, "offline_kb")
        self.assertIn("relativity", ans2.lower())


class TestEmailService(unittest.TestCase):
    """Tests email alias resolution and dry-run dispatch."""

    def setUp(self):
        self.service = EmailService(
            contacts={"arnav": "arnav.sharma.dev@example.com", "mentor": "mentor@example.com"}
        )

    def test_resolve_recipient(self):
        self.assertEqual(self.service.resolve_recipient("arnav"), "arnav.sharma.dev@example.com")
        self.assertEqual(self.service.resolve_recipient("user@test.com"), "user@test.com")
        self.assertIsNone(self.service.resolve_recipient("unknown_user"))

    def test_simulated_send_without_credentials(self):
        # When unconfigured, should succeed with dry-run notice
        success, msg = self.service.send_email("arnav", "Project Review", "Here is the completed task.")
        self.assertTrue(success)
        self.assertIn("Simulated email sent", msg)


class TestWeatherService(unittest.TestCase):
    """Tests weather service handling with missing and placeholder keys."""

    def test_missing_api_key_graceful_response(self):
        service = WeatherService(api_key="your_openweathermap_api_key_here")
        success, speech, data = service.get_weather("Kolkata")
        self.assertFalse(success)
        self.assertIn("OPENWEATHER_API_KEY", speech)


if __name__ == "__main__":
    unittest.main()
