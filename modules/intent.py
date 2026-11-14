"""
Natural Language Understanding (NLU) and Intent Recognition Module for ArnavSharma_Task1.
Provides robust multi-strategy intent classification, entity extraction, and fuzzy matching
to understand free-form user speech beyond exact keyword matches.
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from utils.helpers import normalize_text, parse_duration_seconds
from utils.logger import get_logger

logger = get_logger("IntentEngine")


class IntentType(str, Enum):
    GREETING = "GREETING"
    TIME = "TIME"
    DATE = "DATE"
    WEATHER = "WEATHER"
    WEB_SEARCH = "WEB_SEARCH"
    SEND_EMAIL = "SEND_EMAIL"
    SET_REMINDER = "SET_REMINDER"
    LIST_REMINDERS = "LIST_REMINDERS"
    CANCEL_REMINDER = "CANCEL_REMINDER"
    KNOWLEDGE_QA = "KNOWLEDGE_QA"
    OPEN_APP = "OPEN_APP"
    CUSTOM_COMMAND = "CUSTOM_COMMAND"
    HELP = "HELP"
    STATUS = "STATUS"
    EXIT = "EXIT"
    UNKNOWN = "UNKNOWN"


@dataclass
class IntentResult:
    """Encapsulates the parsed intent, confidence score, and extracted entities."""
    intent: IntentType
    confidence: float
    raw_query: str
    entities: Dict[str, Any] = field(default_factory=dict)
    matched_custom_response: Optional[Any] = None


# Core utterance training bank for semantic scoring
UTTERANCE_BANK: Dict[IntentType, List[str]] = {
    IntentType.GREETING: [
        "hello", "hi", "hey", "hey assistant", "hello aura", "hi there", "good morning",
        "good afternoon", "good evening", "how are you", "what's up", "greetings",
    ],
    IntentType.TIME: [
        "what time is it", "tell me the time", "current time", "what is the time now",
        "could you tell me what the hour is", "time please", "check time",
    ],
    IntentType.DATE: [
        "what is today's date", "tell me the date", "what is the date today",
        "which day is it today", "current date", "what day is today", "calendar date",
    ],
    IntentType.WEATHER: [
        "what is the weather", "how is the weather outside", "check the weather forecast",
        "current temperature", "is it raining outside", "weather update", "what's the weather like",
    ],
    IntentType.WEB_SEARCH: [
        "search the web", "search online", "google something", "browse the internet",
        "find on web", "look up on google",
    ],
    IntentType.SEND_EMAIL: [
        "send an email", "send email", "write an email", "compose an email",
        "mail someone", "dispatch an email", "email my contact",
    ],
    IntentType.SET_REMINDER: [
        "set a reminder", "remind me later", "create a reminder", "schedule reminder",
        "remind me to do something", "notify me in some time",
    ],
    IntentType.LIST_REMINDERS: [
        "what are my reminders", "list my reminders", "show active reminders",
        "do i have any reminders", "view reminders", "check my reminders",
    ],
    IntentType.CANCEL_REMINDER: [
        "cancel my reminder", "clear all reminders", "delete reminder", "remove reminder",
    ],
    IntentType.KNOWLEDGE_QA: [
        "who is", "what is", "tell me about", "where is", "define", "explain",
        "why is", "how does", "what does", "give me information about",
    ],
    IntentType.OPEN_APP: [
        "open application", "launch program", "start application", "run software",
    ],
    IntentType.HELP: [
        "help", "what can you do", "show commands", "list capabilities",
        "how do i use you", "help menu", "features list",
    ],
    IntentType.STATUS: [
        "system status", "assistant status", "are you online", "how are you running",
        "battery status", "diagnostics",
    ],
    IntentType.EXIT: [
        "exit", "quit", "goodbye", "bye", "shutdown", "stop listening",
        "close assistant", "terminate", "see you later", "sleep now",
    ],
}


class IntentEngine:
    """
    NLP Intent Classifier and Entity Extraction Engine.
    Employs regex patterns, custom command lookups, and token-based similarity.
    """

    def __init__(self, custom_commands: Optional[Dict[str, Any]] = None):
        self.custom_commands = custom_commands or {}

    def update_custom_commands(self, custom_commands: Dict[str, Any]) -> None:
        """Dynamically reloads custom commands dictionary."""
        self.custom_commands = custom_commands

    def _tokenize(self, text: str) -> List[str]:
        """Tokenizes text into words, stripping punctuation."""
        return re.findall(r"\b\w+\b", text.lower())

    def _jaccard_similarity(self, tokens1: List[str], tokens2: List[str]) -> float:
        """Calculates token overlap (Jaccard similarity) between two token lists."""
        set1 = set(tokens1)
        set2 = set(tokens2)
        if not set1 or not set2:
            return 0.0
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        return intersection / union

    def classify(self, text: str) -> IntentResult:
        """
        Classifies user utterance into structured IntentResult.

        Evaluation order:
        1. Custom command dictionary exact/fuzzy match
        2. Exit commands
        3. Parameterized regex pattern extraction (Weather, Reminder, Search, App, Email)
        4. Rule-based entity extraction
        5. Semantic token similarity across Utterance Bank
        6. General knowledge trigger patterns
        7. Fallback to UNKNOWN
        """
        raw = text.strip()
        norm = normalize_text(raw)
        if not norm:
            return IntentResult(IntentType.UNKNOWN, 0.0, raw)

        # 1. Custom Commands Match
        for cmd_trigger, cmd_val in self.custom_commands.items():
            norm_trigger = normalize_text(cmd_trigger)
            if norm == norm_trigger or norm.startswith(norm_trigger):
                return IntentResult(
                    intent=IntentType.CUSTOM_COMMAND,
                    confidence=1.0,
                    raw_query=raw,
                    entities={"command": cmd_trigger},
                    matched_custom_response=cmd_val,
                )

        # 2. Exit Commands Match
        exit_tokens = {"exit", "quit", "goodbye", "bye", "shutdown", "terminate", "stop listening"}
        if norm in exit_tokens or norm.startswith("exit") or norm.startswith("quit") or norm.startswith("shut down"):
            return IntentResult(IntentType.EXIT, 1.0, raw)

        # 3. Help Command Match
        help_phrases = {"help", "what can you do", "commands", "show commands", "list features", "help me"}
        if norm in help_phrases:
            return IntentResult(IntentType.HELP, 1.0, raw)

        # 4. Reminder Commands: Check Cancel / List first
        if any(p in norm for p in ["cancel reminder", "clear reminder", "delete reminder", "clear all reminders"]):
            return IntentResult(IntentType.CANCEL_REMINDER, 0.95, raw)

        if any(p in norm for p in ["what are my reminders", "list reminders", "show reminders", "active reminders", "do i have reminders"]):
            return IntentResult(IntentType.LIST_REMINDERS, 0.95, raw)

        # Check Set Reminder Pattern
        reminder_match = self._extract_reminder(raw)
        if reminder_match:
            return IntentResult(
                intent=IntentType.SET_REMINDER,
                confidence=0.95,
                raw_query=raw,
                entities=reminder_match,
            )

        # 5. Email Automation Match
        email_match = self._extract_email(raw)
        if email_match or norm.startswith("send email") or norm.startswith("write email") or norm.startswith("compose email"):
            return IntentResult(
                intent=IntentType.SEND_EMAIL,
                confidence=0.90,
                raw_query=raw,
                entities=email_match or {},
            )

        # 6. Live Weather Match
        weather_match = self._extract_weather(raw)
        if weather_match:
            return IntentResult(
                intent=IntentType.WEATHER,
                confidence=0.95,
                raw_query=raw,
                entities=weather_match,
            )

        # 7. Web Search Match
        search_match = self._extract_web_search(raw)
        if search_match:
            return IntentResult(
                intent=IntentType.WEB_SEARCH,
                confidence=0.95,
                raw_query=raw,
                entities=search_match,
            )

        # 8. Open Desktop Application Match
        app_match = self._extract_app_launch(raw)
        if app_match:
            return IntentResult(
                intent=IntentType.OPEN_APP,
                confidence=0.90,
                raw_query=raw,
                entities=app_match,
            )

        # 9. Time and Date Inquiries
        if any(p in norm for p in ["time is it", "current time", "what's the time", "tell me the time", "time now"]):
            return IntentResult(IntentType.TIME, 0.95, raw)

        if any(p in norm for p in ["today's date", "current date", "what is the date", "tell me the date", "which day is it", "what day is today"]):
            return IntentResult(IntentType.DATE, 0.95, raw)

        # 10. Greetings
        if any(norm == g or norm.startswith(g + " ") for g in ["hello", "hi", "hey", "good morning", "good afternoon", "good evening", "greetings"]):
            return IntentResult(IntentType.GREETING, 0.90, raw)

        # 11. General Knowledge QA patterns (who is, what is, tell me about)
        qa_match = self._extract_knowledge_qa(raw)
        if qa_match:
            return IntentResult(
                intent=IntentType.KNOWLEDGE_QA,
                confidence=0.85,
                raw_query=raw,
                entities=qa_match,
            )

        # 12. Utterance Bank Semantic Similarity Fallback
        query_tokens = self._tokenize(norm)
        best_intent = IntentType.UNKNOWN
        best_score = 0.0

        for itype, samples in UTTERANCE_BANK.items():
            for sample in samples:
                sample_tokens = self._tokenize(sample)
                score = self._jaccard_similarity(query_tokens, sample_tokens)
                if score > best_score:
                    best_score = score
                    best_intent = itype

        if best_score >= 0.40:
            return IntentResult(best_intent, round(best_score, 2), raw)

        # If user asks a general question starting with who/what/why/how/where, treat as QA
        if any(norm.startswith(q) for q in ["who", "what", "where", "why", "how", "when", "tell me"]):
            return IntentResult(
                intent=IntentType.KNOWLEDGE_QA,
                confidence=0.60,
                raw_query=raw,
                entities={"topic": raw},
            )

        return IntentResult(IntentType.UNKNOWN, 0.0, raw)

    def _extract_weather(self, text: str) -> Optional[Dict[str, Any]]:
        """Extracts city from weather inquiries."""
        norm = normalize_text(text)
        patterns = [
            r"(?:what(?:'s| is) the weather (?:like )?in|weather (?:in|for|at)|temperature (?:in|for|at))\s+([a-zA-Z\s]+)",
            r"(?:how is the weather in)\s+([a-zA-Z\s]+)",
            r"([a-zA-Z\s]+)\s+weather forecast",
        ]
        for pat in patterns:
            m = re.search(pat, norm, re.IGNORECASE)
            if m:
                city = m.group(1).strip()
                # Clean filler words
                city = re.sub(r"\b(today|now|please|outside|currently)\b", "", city).strip()
                if city:
                    return {"city": city.title()}

        # General weather query without explicit city
        if "weather" in norm or "temperature" in norm:
            return {"city": None}

        return None

    def _extract_reminder(self, text: str) -> Optional[Dict[str, Any]]:
        """Extracts reminder task and duration."""
        norm = normalize_text(text)
        if not ("remind" in norm or "reminder" in norm):
            return None

        # Pattern: remind me to [task] in/after [duration]
        m = re.search(r"remind\s+(?:me\s+)?to\s+(.+?)\s+(?:in|after|for)\s+(.+)$", norm)
        if m:
            task = m.group(1).strip()
            duration_str = m.group(2).strip()
            seconds = parse_duration_seconds(duration_str)
            if seconds:
                return {"task": task, "seconds": seconds, "duration_phrase": duration_str}

        # Pattern: remind me in/after [duration] to [task]
        m = re.search(r"remind\s+(?:me\s+)?(?:in|after|for)\s+(.+?)\s+to\s+(.+)$", norm)
        if m:
            duration_str = m.group(1).strip()
            task = m.group(2).strip()
            seconds = parse_duration_seconds(duration_str)
            if seconds:
                return {"task": task, "seconds": seconds, "duration_phrase": duration_str}

        # Pattern: set a reminder for [duration] to [task]
        m = re.search(r"(?:set\s+a\s+reminder|reminder)\s+(?:for|in|after)\s+(.+?)\s+(?:to\s+(.+)|$)", norm)
        if m:
            duration_str = m.group(1).strip()
            task = m.group(2).strip() if m.group(2) else "general task"
            seconds = parse_duration_seconds(duration_str)
            if seconds:
                return {"task": task, "seconds": seconds, "duration_phrase": duration_str}

        # General duration extraction if "remind" keyword present
        seconds = parse_duration_seconds(norm)
        if seconds:
            # Strip duration words to find task
            clean_task = re.sub(r"\b(remind|me|to|after|in|for|set|a|reminder)\b", " ", norm).strip()
            return {"task": clean_task or "your scheduled task", "seconds": seconds, "duration_phrase": f"{seconds} seconds"}

        return None

    def _extract_web_search(self, text: str) -> Optional[Dict[str, Any]]:
        """Extracts search query from web search requests."""
        norm = normalize_text(text)
        patterns = [
            r"^(?:search(?:\s+the\s+web|\s+online|\s+for|\s+google)?|google|look\s+up|find\s+online)\s+(?:for\s+)?(.+)$",
            r"^what\s+is\s+the\s+meaning\s+of\s+(.+)$",
        ]
        for pat in patterns:
            m = re.search(pat, norm)
            if m:
                query = m.group(1).strip()
                if query:
                    return {"query": query}
        return None

    def _extract_email(self, text: str) -> Optional[Dict[str, Any]]:
        """Extracts email parameters (recipient, subject) if spoken in query."""
        norm = normalize_text(text)
        if not ("email" in norm or "mail" in norm):
            return None

        entities: Dict[str, Any] = {}
        # Recipient extraction: "send email to [recipient]"
        m_recip = re.search(r"(?:email|mail)\s+(?:to\s+)?([a-zA-Z0-9_.-]+(?:@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)?|[a-zA-Z]+)", norm)
        if m_recip:
            candidate = m_recip.group(1).strip()
            if candidate not in {"someone", "an", "the", "a"}:
                entities["recipient"] = candidate

        # Subject extraction: "with subject [subject]"
        m_subj = re.search(r"(?:with\s+subject|subject(?:\s+is)?)\s+([a-zA-Z0-9\s]+?)(?:\s+(?:saying|and\s+message)|$)", norm)
        if m_subj:
            entities["subject"] = m_subj.group(1).strip()

        # Body extraction: "saying [body]" or "message is [body]"
        m_body = re.search(r"(?:saying|message\s+(?:is|to)\s+)(.+)$", norm)
        if m_body:
            entities["body"] = m_body.group(1).strip()

        return entities

    def _extract_app_launch(self, text: str) -> Optional[Dict[str, Any]]:
        """Extracts desktop application name."""
        norm = normalize_text(text)
        m = re.search(r"^(?:open|launch|start|run)\s+(?:app|application|the\s+)?([a-zA-Z0-9\s]+)$", norm)
        if m:
            app = m.group(1).strip()
            # Exclude web searches or knowledge topics
            if app not in {"the web", "google", "browser", "internet", "website", "wikipedia"}:
                return {"app_name": app}
        return None

    def _extract_knowledge_qa(self, text: str) -> Optional[Dict[str, Any]]:
        """Extracts topic from knowledge queries."""
        norm = normalize_text(text)
        patterns = [
            r"^(?:who\s+is|who\s+was)\s+(.+)$",
            r"^(?:what\s+is|what\s+was|what\s+are)\s+(.+)$",
            r"^(?:tell\s+me\s+about|information\s+about|explain)\s+(.+)$",
            r"^(?:where\s+is|where\s+was)\s+(.+)$",
            r"^(?:define)\s+(.+)$",
        ]
        for pat in patterns:
            m = re.search(pat, norm)
            if m:
                topic = m.group(1).strip()
                # Exclude time/date/weather
                if topic not in {"the time", "time", "the date", "date", "the weather", "weather"}:
                    return {"topic": topic}
        return None

