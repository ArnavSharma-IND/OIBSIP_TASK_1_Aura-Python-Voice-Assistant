"""
General helper functions for ArnavSharma_Task1 Voice Assistant.
Provides time formatting, natural speech conversion, duration parsing,
and text normalization utilities.
"""

import re
from datetime import datetime
from typing import Optional, Tuple


# Word-to-number mapping for conversational durations
WORD_TO_NUM = {
    "zero": 0, "a": 1, "an": 1, "one": 1, "two": 2, "three": 3, "four": 4,
    "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
    "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20,
    "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "half": 0.5, "quarter": 0.25
}


def normalize_text(text: str) -> str:
    """
    Normalizes a text string by converting to lowercase, removing extraneous
    punctuation, and collapsing multiple whitespace characters.
    """
    if not text:
        return ""
    # Strip leading/trailing spaces, lowercase
    text = text.lower().strip()
    # Replace non-alphanumeric (except basic punctuation needed for context) with spaces
    text = re.sub(r"[^\w\s\':@.-]", " ", text)
    # Collapse multiple spaces
    text = re.sub(r"\s+", " ", text).strip()
    return text


def format_natural_time(dt: Optional[datetime] = None) -> str:
    """
    Returns the current time formatted for natural conversational speech.
    Example: '10:30 PM' or '4:05 PM'.
    """
    if dt is None:
        dt = datetime.now()
    # Format as 12-hour clock with AM/PM
    time_str = dt.strftime("%I:%M %p")
    # Strip leading zero on hour if present (e.g. '04:15 PM' -> '4:15 PM')
    if time_str.startswith("0"):
        time_str = time_str[1:]
    return time_str


def format_natural_date(dt: Optional[datetime] = None) -> str:
    """
    Returns the current date formatted for natural conversational speech.
    Example: 'Friday, November 13, 2026'.
    """
    if dt is None:
        dt = datetime.now()
    day_num = dt.day
    # Determine ordinal suffix (1st, 2nd, 3rd, 4th, etc.)
    if 11 <= day_num <= 13:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(day_num % 10, "th")

    weekday = dt.strftime("%A")
    month = dt.strftime("%B")
    year = dt.year
    return f"{weekday}, {month} {day_num}{suffix}, {year}"


def get_time_of_day_greeting(user_name: str = "Arnav") -> str:
    """
    Returns a personalized greeting appropriate for the current hour of the day.
    """
    hour = datetime.now().hour
    name_str = f", {user_name}" if user_name else ""

    if 5 <= hour < 12:
        return f"Good morning{name_str}! How may I help you today?"
    elif 12 <= hour < 17:
        return f"Good afternoon{name_str}! What can I do for you?"
    elif 17 <= hour < 22:
        return f"Good evening{name_str}! How can I assist you tonight?"
    else:
        return f"Hello{name_str}! Hope you are having a pleasant night. How can I help?"


def parse_duration_seconds(phrase: str) -> Optional[int]:
    """
    Parses conversational duration phrases into total seconds.
    Examples handled:
      - '30 seconds' -> 30
      - '5 minutes' -> 300
      - 'ten minutes' -> 600
      - '1 hour' -> 3600
      - 'half an hour' -> 1800
      - 'a minute' -> 60
      - '2 hours and 15 minutes' -> 8100

    Returns total seconds as an integer, or None if no valid duration found.
    """
    if not phrase:
        return None

    cleaned = phrase.lower().strip()
    total_seconds = 0.0
    matched_any = False

    # Handle special idioms first
    if "half an hour" in cleaned or "half hour" in cleaned:
        total_seconds += 1800
        matched_any = True
        cleaned = re.sub(r"half (an )?hour", "", cleaned)

    if "quarter of an hour" in cleaned or "quarter hour" in cleaned:
        total_seconds += 900
        matched_any = True
        cleaned = re.sub(r"quarter (of an )?hour", "", cleaned)

    # Regex to capture numeric or word-based units: (number) (unit)
    pattern = re.compile(
        r"(\d+(?:\.\d+)?|[a-z]+)\s*(seconds?|secs?|minutes?|mins?|hours?|hrs?)",
        re.IGNORECASE,
    )

    for match in pattern.finditer(cleaned):
        raw_val, unit = match.groups()
        unit = unit.lower()

        # Convert raw_val to numeric float
        val: Optional[float] = None
        if raw_val.isdigit() or re.match(r"^\d+\.\d+$", raw_val):
            val = float(raw_val)
        elif raw_val in WORD_TO_NUM:
            val = float(WORD_TO_NUM[raw_val])
        elif "-" in raw_val:
            parts = raw_val.split("-")
            if len(parts) == 2 and parts[0] in WORD_TO_NUM and parts[1] in WORD_TO_NUM:
                val = float(WORD_TO_NUM[parts[0]] + WORD_TO_NUM[parts[1]])

        if val is None or val <= 0:
            continue

        matched_any = True
        if unit.startswith("sec"):
            total_seconds += val
        elif unit.startswith("min"):
            total_seconds += val * 60
        elif unit.startswith("hour") or unit.startswith("hr"):
            total_seconds += val * 3600

    if matched_any and total_seconds > 0:
        return int(round(total_seconds))
    return None


def format_duration_readable(seconds: int) -> str:
    """
    Formats a duration in seconds into natural spoken words.
    Example: 300 -> '5 minutes', 3660 -> '1 hour and 1 minute'.
    """
    if seconds < 60:
        return f"{seconds} second" if seconds == 1 else f"{seconds} seconds"

    hours = seconds // 3600
    rem = seconds % 3600
    minutes = rem // 60
    secs = rem % 60

    parts = []
    if hours > 0:
        parts.append(f"{hours} hour" if hours == 1 else f"{hours} hours")
    if minutes > 0:
        parts.append(f"{minutes} minute" if minutes == 1 else f"{minutes} minutes")
    if secs > 0 and hours == 0:  # Only show seconds if less than an hour
        parts.append(f"{secs} second" if secs == 1 else f"{secs} seconds")

    if not parts:
        return "0 seconds"
    if len(parts) == 1:
        return parts[0]
    return f"{parts[0]} and {parts[1]}"


def is_valid_email(email: str) -> bool:
    """
    Validates whether a given string is a syntactically valid email address.
    """
    if not email:
        return False
    email_regex = re.compile(
        r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    )
    return bool(email_regex.match(email.strip()))


def sanitize_input(text: str) -> str:
    """
    Strips dangerous characters from user input strings before processing.
    """
    if not text:
        return ""
    # Strip control characters except newline and tab
    return "".join(ch for ch in text if ch.isprintable() or ch in "\n\t").strip()

