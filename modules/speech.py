"""
Speech Recognition and Text-To-Speech (TTS) Module for ArnavSharma_Task1.
Provides thread-safe pyttsx3 speech synthesis and robust microphone speech recognition
with graceful fallbacks for missing hardware or network outages.
"""

import os
import sys
import queue
import threading
import time
from typing import Callable, Optional, Tuple

from utils.logger import get_logger

logger = get_logger("Speech")

# Safe imports for SpeechRecognition and PyAudio
HAVE_SR = False
HAVE_PYAUDIO = False
try:
    import speech_recognition as sr
    HAVE_SR = True
except ImportError:
    sr = None
    logger.warning("speech_recognition library is not installed.")

try:
    import pyaudio
    HAVE_PYAUDIO = True
except ImportError:
    pyaudio = None
    logger.warning("pyaudio library is not installed.")

# Safe import for pyttsx3
HAVE_PYTTSX3 = False
try:
    import pyttsx3
    HAVE_PYTTSX3 = True
except ImportError:
    pyttsx3 = None
    logger.warning("pyttsx3 library is not installed.")


class TTSManager:
    """
    Thread-safe, queue-based Text-To-Speech manager using pyttsx3.
    Decouples voice synthesis from main and UI threads to prevent blocking or audio device conflicts.
    """

    def __init__(
        self,
        voice_index: int = 0,
        rate: int = 180,
        volume: float = 1.0,
        on_start: Optional[Callable[[str], None]] = None,
        on_finish: Optional[Callable[[], None]] = None,
    ):
        self.voice_index = voice_index
        self.rate = rate
        self.volume = volume
        self.on_start = on_start
        self.on_finish = on_finish
        self.is_muted = False

        self._queue: queue.Queue = queue.Queue()
        self._stop_event = threading.Event()
        self._is_speaking = False
        self._thread: Optional[threading.Thread] = None

        if HAVE_PYTTSX3:
            self._start_worker()
        else:
            logger.warning("pyttsx3 is unavailable. Spoken audio feedback will be printed to console only.")

    def _start_worker(self) -> None:
        """Starts the dedicated background TTS worker thread."""
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._worker_loop, daemon=True, name="TTS-Worker")
        self._thread.start()

    def _worker_loop(self) -> None:
        """Dedicated thread loop for pyttsx3 engine to prevent COM/SAPI threading errors."""
        engine = None
        try:
            engine = pyttsx3.init()
            # Configure voice properties
            engine.setProperty("rate", self.rate)
            engine.setProperty("volume", self.volume)
            voices = engine.getProperty("voices")
            if voices and 0 <= self.voice_index < len(voices):
                engine.setProperty("voice", voices[self.voice_index].id)
        except Exception as err:
            logger.error(f"Failed to initialize pyttsx3 engine: {err}")
            return

        while not self._stop_event.is_set():
            try:
                item = self._queue.get(timeout=0.2)
            except queue.Empty:
                continue

            if item is None:  # Shutdown sentinel
                break

            text, done_event = item
            if self.is_muted or not text.strip():
                if done_event:
                    done_event.set()
                self._queue.task_done()
                continue

            self._is_speaking = True
            if self.on_start:
                try:
                    self.on_start(text)
                except Exception as cb_err:
                    logger.debug(f"TTS on_start callback error: {cb_err}")

            try:
                engine.say(text)
                engine.runAndWait()
            except Exception as say_err:
                logger.error(f"Error during pyttsx3 speech synthesis: {say_err}")

            self._is_speaking = False
            if self.on_finish:
                try:
                    self.on_finish()
                except Exception as cb_err:
                    logger.debug(f"TTS on_finish callback error: {cb_err}")

            if done_event:
                done_event.set()
            self._queue.task_done()

        try:
            engine.stop()
        except Exception:
            pass

    def speak(self, text: str, wait: bool = False) -> None:
        """
        Enqueues text to be spoken by the assistant.

        Args:
            text: Text to speak aloud.
            wait: If True, blocks calling thread until speech is completed.
        """
        if not text:
            return

        # Print speech feedback in console
        print(f"\n[Aura]: {text}")

        if not HAVE_PYTTSX3 or self.is_muted:
            return

        done_event = threading.Event() if wait else None
        self._queue.put((text, done_event))

        if wait and done_event:
            done_event.wait()

    def stop(self) -> None:
        """Clears all pending speech items in queue."""
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
                self._queue.task_done()
            except queue.Empty:
                break

    def set_muted(self, muted: bool) -> None:
        """Enables or disables speech audio output."""
        self.is_muted = muted
        if muted:
            self.stop()

    def is_speaking(self) -> bool:
        """Returns True if audio is actively playing."""
        return self._is_speaking

    def shutdown(self) -> None:
        """Stops the worker thread cleanly."""
        self._stop_event.set()
        self._queue.put(None)
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)


class SpeechRecognizer:
    """
    Microphone speech capturer and Google Web Speech recognizer wrapper.
    Gracefully handles ambient noise calibration, timeouts, and microphone errors.
    """

    def __init__(
        self,
        energy_threshold: int = 300,
        dynamic_energy_threshold: bool = True,
        listen_timeout: int = 5,
        phrase_time_limit: int = 8,
    ):
        self.energy_threshold = energy_threshold
        self.dynamic_energy_threshold = dynamic_energy_threshold
        self.listen_timeout = listen_timeout
        self.phrase_time_limit = phrase_time_limit

        self.recognizer: Optional["sr.Recognizer"] = None
        self.microphone: Optional["sr.Microphone"] = None
        self.is_mic_available = False

        if HAVE_SR:
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = self.energy_threshold
            self.recognizer.dynamic_energy_threshold = self.dynamic_energy_threshold
            self.recognizer.pause_threshold = 0.8
            self._check_microphone()
        else:
            logger.warning("SpeechRecognition is not installed. Text input fallback will be used.")

    def _check_microphone(self) -> bool:
        """Checks if a valid input microphone device is accessible."""
        if not HAVE_SR or not HAVE_PYAUDIO:
            self.is_mic_available = False
            return False

        try:
            # Attempt to probe default microphone
            with sr.Microphone() as source:
                self.is_mic_available = True
                logger.info("Microphone detected and operational.")
                return True
        except Exception as err:
            self.is_mic_available = False
            logger.warning(f"No working microphone found or PyAudio error: {err}")
            return False

    def calibrate_noise(self, duration: float = 1.0) -> None:
        """Calibrates speech recognizer against room ambient noise."""
        if not self.is_mic_available or not self.recognizer:
            return
        try:
            logger.info("Calibrating microphone for ambient room noise...")
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=duration)
            logger.info(f"Calibration complete. Energy threshold set to: {self.recognizer.energy_threshold}")
        except Exception as err:
            logger.warning(f"Ambient noise calibration failed: {err}")

    def listen(
        self,
        timeout: Optional[int] = None,
        phrase_time_limit: Optional[int] = None,
    ) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Captures spoken voice from microphone and converts it to text.

        Returns:
            Tuple of (recognized_text, error_code, user_friendly_message)
            - Success: (text, None, None)
            - Silence/Timeout: (None, "TIMEOUT", None)
            - Unintelligible: (None, "UNKNOWN", "I'm sorry, I didn't catch that. Could you please repeat?")
            - Network/Service error: (None, "REQUEST_ERROR", "Speech service is currently unavailable. Please check your connection or type your command.")
            - Hardware/Mic error: (None, "MIC_ERROR", "Microphone is unavailable. Please type your query.")
        """
        if not self.is_mic_available or not self.recognizer:
            return (None, "MIC_ERROR", "Microphone is unavailable. Please type your query.")

        to = timeout if timeout is not None else self.listen_timeout
        pl = phrase_time_limit if phrase_time_limit is not None else self.phrase_time_limit

        try:
            with sr.Microphone() as source:
                # Capture raw audio
                audio = self.recognizer.listen(source, timeout=to, phrase_time_limit=pl)

            # Recognize using Google Speech Recognition API
            text = self.recognizer.recognize_google(audio)
            text = text.strip()
            logger.info(f"Speech Recognized: '{text}'")
            return (text, None, None)

        except sr.WaitTimeoutError:
            # Normal silence timeout when user doesn't speak
            return (None, "TIMEOUT", None)

        except sr.UnknownValueError:
            logger.info("Speech captured but was unintelligible.")
            return (
                None,
                "UNKNOWN",
                "I'm sorry, I didn't catch that. Could you please repeat?",
            )

        except sr.RequestError as req_err:
            logger.error(f"Google Speech Recognition service request error: {req_err}")
            return (
                None,
                "REQUEST_ERROR",
                "Speech recognition service is currently unavailable. Please check your internet connection or type your command.",
            )

        except Exception as err:
            logger.error(f"Unexpected error capturing microphone audio: {err}")
            return (
                None,
                "MIC_ERROR",
                f"Audio capture error: {str(err)}. You can type your command below.",
            )

