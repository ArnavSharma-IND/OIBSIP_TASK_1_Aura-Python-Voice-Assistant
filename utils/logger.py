"""
Thread-safe, sanitized logging utility for ArnavSharma_Task1 Voice Assistant.
Ensures sensitive tokens, passwords, and API keys are redacted before writing to logs.
"""

import os
import re
import logging
from logging.handlers import RotatingFileHandler
from typing import Optional

# Regular expression patterns for sensitive data redaction
REDACTION_PATTERNS = [
    (re.compile(r"(password|passwd|pwd)[\s:=]+['\"]?([^\s'\"]+)['\"]?", re.IGNORECASE), r"\1=***REDACTED***"),
    (re.compile(r"(api[_-]?key|token|secret)[\s:=]+['\"]?([a-zA-Z0-9_\-]{8,})['\"]?", re.IGNORECASE), r"\1=***REDACTED***"),
    (re.compile(r"(appid=)[a-zA-Z0-9]{16,}", re.IGNORECASE), r"\1***REDACTED***"),
    (re.compile(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", re.IGNORECASE), r"***EMAIL***"),
]


class SanitizedFilter(logging.Filter):
    """Filters log records to redact sensitive information such as credentials."""

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            msg = record.msg
            for pattern, repl in REDACTION_PATTERNS:
                msg = pattern.sub(repl, msg)
            record.msg = msg
        return True


_ROOT_LOGGER: Optional[logging.Logger] = None


def setup_logger(
    name: str = "VoiceAssistant",
    log_dir: str = "logs",
    log_file: str = "assistant.log",
    level: int = logging.INFO,
    console_output: bool = True,
) -> logging.Logger:
    """
    Initializes and configures the sanitized application logger.

    Args:
        name: Logger name.
        log_dir: Directory where logs should be stored.
        log_file: Log file name.
        level: Logging severity level.
        console_output: Whether to print log output to stderr/stdout.

    Returns:
        Configured logging.Logger instance.
    """
    global _ROOT_LOGGER
    if _ROOT_LOGGER is not None:
        return _ROOT_LOGGER

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.handlers.clear()

    # Formatter for log entries
    formatter = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)s] [%(name)s:%(module)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    sanitizer = SanitizedFilter()

    # Ensure log directory exists
    try:
        os.makedirs(log_dir, exist_ok=True)
        file_path = os.path.join(log_dir, log_file)
        file_handler = RotatingFileHandler(
            file_path,
            maxBytes=2 * 1024 * 1024,  # 2 MB per log file
            backupCount=3,
            encoding="utf-8",
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        file_handler.addFilter(sanitizer)
        logger.addHandler(file_handler)
    except Exception as err:
        # Fallback if filesystem write fails
        print(f"[Warning] Failed to initialize file logging in '{log_dir}': {err}")

    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%H:%M:%S",
        )
        console_handler.setFormatter(console_formatter)
        console_handler.addFilter(sanitizer)
        logger.addHandler(console_handler)

    _ROOT_LOGGER = logger
    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Retrieves the global assistant logger or child logger.
    """
    global _ROOT_LOGGER
    if _ROOT_LOGGER is None:
        return setup_logger()
    if name:
        return _ROOT_LOGGER.getChild(name)
    return _ROOT_LOGGER

