"""
Voice Reminders Module for ArnavSharma_Task1.
Provides non-blocking background thread timers, audible alert chimes,
and natural spoken notifications when reminders trigger.
"""

import sys
import time
import threading
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Callable, Dict, List, Optional, Tuple

from utils.helpers import format_duration_readable
from utils.logger import get_logger

logger = get_logger("Reminders")


@dataclass
class ReminderItem:
    id: int
    task: str
    duration_seconds: int
    created_at: datetime
    target_time: datetime
    is_cancelled: bool = False


class ReminderManager:
    """Manages scheduled voice reminders with background thread execution."""

    def __init__(
        self,
        alert_callback: Optional[Callable[[str], None]] = None,
        sound_enabled: bool = True,
    ):
        self.alert_callback = alert_callback
        self.sound_enabled = sound_enabled
        self._reminders: Dict[int, ReminderItem] = {}
        self._next_id = 1
        self._lock = threading.Lock()
        self._shutdown_event = threading.Event()

    def set_alert_callback(self, callback: Callable[[str], None]) -> None:
        """Sets or updates the callback function triggered when a reminder expires."""
        self.alert_callback = callback

    def _play_alert_tone(self) -> None:
        """Plays an audible beep chime on Windows or system bell fallback."""
        if not self.sound_enabled:
            return

        try:
            if sys.platform == "win32":
                import winsound
                # Play a pleasant dual-tone chime
                winsound.Beep(880, 200)   # A5
                time.sleep(0.05)
                winsound.Beep(1175, 350)  # D6
            else:
                sys.stdout.write("\a")
                sys.stdout.flush()
        except Exception as err:
            logger.debug(f"Audio tone playback note: {err}")

    def set_reminder(self, task: str, seconds: int) -> Tuple[bool, str, Optional[ReminderItem]]:
        """
        Schedules a new reminder in a background daemon thread.

        Args:
            task: The reminder description (e.g. 'study', 'drink water').
            seconds: Duration in seconds before reminder fires.

        Returns:
            Tuple of (success, spoken_feedback_string, reminder_item)
        """
        if seconds <= 0:
            return False, "Reminder duration must be greater than zero.", None

        clean_task = task.strip() or "general reminder"
        now = datetime.now()
        target = now + timedelta(seconds=seconds)

        with self._lock:
            rem_id = self._next_id
            self._next_id += 1
            item = ReminderItem(
                id=rem_id,
                task=clean_task,
                duration_seconds=seconds,
                created_at=now,
                target_time=target,
            )
            self._reminders[rem_id] = item

        # Start non-blocking daemon thread
        t = threading.Thread(
            target=self._reminder_worker,
            args=(item,),
            daemon=True,
            name=f"Reminder-{rem_id}",
        )
        t.start()

        duration_text = format_duration_readable(seconds)
        # Matches user prompt: "Your reminder has been successfully set for 10 minutes."
        feedback = f"Your reminder has been successfully set for {duration_text}."
        logger.info(f"Reminder #{rem_id} created: '{clean_task}' in {duration_text}.")
        return True, feedback, item

    def _reminder_worker(self, item: ReminderItem) -> None:
        """Background thread worker that sleeps until the target time arrives."""
        while not self._shutdown_event.is_set():
            if item.is_cancelled:
                logger.info(f"Reminder #{item.id} cancelled. Exiting thread.")
                return

            remaining = (item.target_time - datetime.now()).total_seconds()
            if remaining <= 0:
                break

            # Sleep in small slices to remain responsive to cancellations
            sleep_chunk = min(remaining, 0.5)
            time.sleep(sleep_chunk)

        if item.is_cancelled or self._shutdown_event.is_set():
            return

        # Trigger audible alert
        self._play_alert_tone()

        alert_message = f"Reminder alert! You asked me to: {item.task}."
        logger.info(f"TRIGGERED Reminder #{item.id}: '{item.task}'")

        # Invoke callback for TTS and GUI notification
        if self.alert_callback:
            try:
                self.alert_callback(alert_message)
            except Exception as cb_err:
                logger.error(f"Error in reminder alert callback: {cb_err}")

        # Clean up from active dict
        with self._lock:
            self._reminders.pop(item.id, None)

    def list_active_reminders(self) -> Tuple[int, str]:
        """
        Returns the count and a natural spoken list of currently active reminders.
        """
        with self._lock:
            active = [item for item in self._reminders.values() if not item.is_cancelled]

        if not active:
            return 0, "You do not have any active reminders right now."

        now = datetime.now()
        descriptions = []
        for i, item in enumerate(active, start=1):
            remaining_secs = max(0, int((item.target_time - now).total_seconds()))
            time_left_str = format_duration_readable(remaining_secs)
            descriptions.append(f"Number {i}: {item.task}, due in {time_left_str}.")

        count_str = f"You have {len(active)} active " + ("reminder" if len(active) == 1 else "reminders")
        full_speech = f"{count_str}. " + " ".join(descriptions)
        return len(active), full_speech

    def cancel_all_reminders(self) -> str:
        """Cancels all currently active reminders."""
        with self._lock:
            count = len(self._reminders)
            for item in self._reminders.values():
                item.is_cancelled = True
            self._reminders.clear()

        if count == 0:
            return "There are no active reminders to cancel."
        return f"Successfully cancelled all {count} active reminders."

    def cancel_reminder_by_task(self, keyword: str) -> Tuple[bool, str]:
        """Cancels a reminder matching a keyword in its task description."""
        keyword_lower = keyword.lower().strip()
        found_id = None
        found_task = ""

        with self._lock:
            for rem_id, item in self._reminders.items():
                if keyword_lower in item.task.lower():
                    item.is_cancelled = True
                    found_id = rem_id
                    found_task = item.task
                    break

            if found_id is not None:
                del self._reminders[found_id]

        if found_id is not None:
            return True, f"Cancelled reminder for '{found_task}'."
        return False, f"Could not find any active reminder matching '{keyword}'."

    def shutdown(self) -> None:
        """Shuts down all reminder threads cleanly."""
        self._shutdown_event.set()
        with self._lock:
            for item in self._reminders.values():
                item.is_cancelled = True
            self._reminders.clear()

