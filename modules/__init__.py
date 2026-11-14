"""
Package initialization for ArnavSharma_Task1 Voice Assistant Modules.
"""

from .speech import SpeechRecognizer, TTSManager
from .intent import IntentEngine, IntentResult, IntentType
from .weather import WeatherService
from .email_service import EmailService
from .reminders import ReminderManager, ReminderItem
from .web_search import WebSearchService
from .knowledge import KnowledgeService
from .app_launcher import AppLauncher
from .assistant import VoiceAssistant

__all__ = [
    "SpeechRecognizer",
    "TTSManager",
    "IntentEngine",
    "IntentResult",
    "IntentType",
    "WeatherService",
    "EmailService",
    "ReminderManager",
    "ReminderItem",
    "WebSearchService",
    "KnowledgeService",
    "AppLauncher",
    "VoiceAssistant",
]

