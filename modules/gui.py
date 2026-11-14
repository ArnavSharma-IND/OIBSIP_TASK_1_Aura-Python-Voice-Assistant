"""
Desktop Graphical User Interface (GUI) Module for ArnavSharma_Task1.
Provides a modern dark-themed Tkinter interface with speech-to-text triggers,
live chat transcript, quick-action chips, and typed input fallback.
"""

import queue
import sys
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Optional

from utils.logger import get_logger

logger = get_logger("GUI")


# UI Theme Palette
BG_DARK = "#12131A"
BG_CARD = "#1E202C"
BG_INPUT = "#2A2D3E"
ACCENT_BLUE = "#3B82F6"
ACCENT_GREEN = "#10B981"
ACCENT_AMBER = "#F59E0B"
TEXT_PRIMARY = "#F3F4F6"
TEXT_SECONDARY = "#9CA3AF"
USER_BUBBLE = "#1D4ED8"
BOT_BUBBLE = "#2D3142"


class AssistantGUI:
    """Tkinter-based Desktop GUI for the Voice Assistant."""

    def __init__(self, assistant):
        self.assistant = assistant
        self.root = tk.Tk()
        self.root.title(f"{assistant.assistant_name} – Python Voice Assistant")
        self.root.geometry("640x760")
        self.root.minsize(520, 600)
        self.root.configure(bg=BG_DARK)

        # Message queue for cross-thread GUI updates
        self.gui_queue: queue.Queue = queue.Queue()
        self.is_listening = False
        self.listen_thread: Optional[threading.Thread] = None

        # Register UI callback on the assistant
        self.assistant.ui_callback = self.enqueue_message

        # Build UI layout
        self._build_widgets()
        self._start_queue_listener()

        # Display initial greeting
        initial_greeting = self.assistant.get_initial_greeting()
        self.enqueue_message("Assistant", initial_greeting)
        # Speak greeting in background
        threading.Thread(target=lambda: self.assistant.tts.speak(initial_greeting), daemon=True).start()

    def _build_widgets(self) -> None:
        """Constructs all GUI visual components."""
        # --- Top Header Bar ---
        header_frame = tk.Frame(self.root, bg=BG_CARD, padx=16, pady=12)
        header_frame.pack(fill=tk.X, side=tk.TOP)

        title_frame = tk.Frame(header_frame, bg=BG_CARD)
        title_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        title_lbl = tk.Label(
            title_frame,
            text=f"🎙️ {self.assistant.assistant_name} Voice Assistant",
            font=("Segoe UI", 14, "bold"),
            bg=BG_CARD,
            fg=TEXT_PRIMARY,
        )
        title_lbl.pack(anchor="w")

        sub_lbl = tk.Label(
            title_frame,
            text=f"Built by {self.assistant.user_name} Sharma | Oasis InfoTech Internship",
            font=("Segoe UI", 9),
            bg=BG_CARD,
            fg=TEXT_SECONDARY,
        )
        sub_lbl.pack(anchor="w")

        # Status indicator badge
        self.status_lbl = tk.Label(
            header_frame,
            text="🟢 Ready",
            font=("Segoe UI", 9, "bold"),
            bg=BG_CARD,
            fg=ACCENT_GREEN,
            padx=10,
            pady=4,
        )
        self.status_lbl.pack(side=tk.RIGHT)

        # --- Quick Action Chips ---
        chips_frame = tk.Frame(self.root, bg=BG_DARK, padx=12, pady=8)
        chips_frame.pack(fill=tk.X)

        quick_actions = [
            ("🕒 Time", "what time is it"),
            ("📅 Date", "what is today's date"),
            ("⛅ Weather", f"weather in {self.assistant.weather_service.default_city}"),
            ("⏰ 10s Timer", "remind me in 10 seconds to take a break"),
            ("❓ Help", "help"),
        ]

        for label, cmd in quick_actions:
            btn = tk.Button(
                chips_frame,
                text=label,
                font=("Segoe UI", 8),
                bg=BG_CARD,
                fg=TEXT_PRIMARY,
                activebackground=ACCENT_BLUE,
                activeforeground=TEXT_PRIMARY,
                relief=tk.FLAT,
                bd=0,
                padx=8,
                pady=3,
                cursor="hand2",
                command=lambda c=cmd: self._send_command_async(c),
            )
            btn.pack(side=tk.LEFT, padx=4)

        # --- Chat Transcript Area ---
        chat_container = tk.Frame(self.root, bg=BG_DARK, padx=12, pady=4)
        chat_container.pack(fill=tk.BOTH, expand=True)

        self.chat_display = scrolledtext.ScrolledText(
            chat_container,
            wrap=tk.WORD,
            bg=BG_CARD,
            fg=TEXT_PRIMARY,
            insertbackground=TEXT_PRIMARY,
            font=("Segoe UI", 10),
            relief=tk.FLAT,
            bd=0,
            padx=12,
            pady=12,
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        self.chat_display.config(state=tk.DISABLED)

        # Configure tag styles for message formatting
        self.chat_display.tag_config("user_tag", foreground="#60A5FA", font=("Segoe UI", 10, "bold"))
        self.chat_display.tag_config("bot_tag", foreground="#34D399", font=("Segoe UI", 10, "bold"))
        self.chat_display.tag_config("alert_tag", foreground="#FBBF24", font=("Segoe UI", 10, "bold"))
        self.chat_display.tag_config("body_tag", foreground=TEXT_PRIMARY, font=("Segoe UI", 10))
        self.chat_display.tag_config("time_tag", foreground=TEXT_SECONDARY, font=("Segoe UI", 8))

        # --- Bottom Input & Control Bar ---
        bottom_frame = tk.Frame(self.root, bg=BG_CARD, padx=12, pady=10)
        bottom_frame.pack(fill=tk.X, side=tk.BOTTOM)

        # Microphone Toggle Button
        self.mic_btn = tk.Button(
            bottom_frame,
            text="🎙️ Speak",
            font=("Segoe UI", 10, "bold"),
            bg=ACCENT_BLUE,
            fg=TEXT_PRIMARY,
            activebackground="#2563EB",
            activeforeground=TEXT_PRIMARY,
            relief=tk.FLAT,
            bd=0,
            padx=14,
            pady=8,
            cursor="hand2",
            command=self._on_mic_clicked,
        )
        self.mic_btn.pack(side=tk.LEFT, padx=(0, 8))

        # Text input box for keyboard fallback
        self.input_entry = tk.Entry(
            bottom_frame,
            bg=BG_INPUT,
            fg=TEXT_PRIMARY,
            insertbackground=TEXT_PRIMARY,
            font=("Segoe UI", 10),
            relief=tk.FLAT,
            bd=6,
        )
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        self.input_entry.bind("<Return>", lambda e: self._on_send_clicked())

        # Send Button
        send_btn = tk.Button(
            bottom_frame,
            text="Send",
            font=("Segoe UI", 10, "bold"),
            bg="#374151",
            fg=TEXT_PRIMARY,
            activebackground=ACCENT_BLUE,
            activeforeground=TEXT_PRIMARY,
            relief=tk.FLAT,
            bd=0,
            padx=14,
            pady=8,
            cursor="hand2",
            command=self._on_send_clicked,
        )
        send_btn.pack(side=tk.LEFT)

        # Mute audio checkbox
        self.mute_var = tk.BooleanVar(value=False)
        mute_cb = tk.Checkbutton(
            bottom_frame,
            text="Mute Voice",
            variable=self.mute_var,
            bg=BG_CARD,
            fg=TEXT_SECONDARY,
            selectcolor=BG_INPUT,
            activebackground=BG_CARD,
            activeforeground=TEXT_PRIMARY,
            command=self._on_mute_toggled,
            font=("Segoe UI", 8),
        )
        mute_cb.pack(side=tk.RIGHT, padx=(8, 0))

    def _on_mute_toggled(self) -> None:
        """Handles voice mute checkbox toggle."""
        self.assistant.tts.set_muted(self.mute_var.get())

    def set_status(self, text: str, color: str = TEXT_PRIMARY) -> None:
        """Updates the top status badge."""
        self.status_lbl.config(text=text, fg=color)

    def enqueue_message(self, sender: str, text: str) -> None:
        """Thread-safe method to queue chat updates."""
        self.gui_queue.put((sender, text))

    def _start_queue_listener(self) -> None:
        """Periodically polls gui_queue and updates the chat display."""
        try:
            while not self.gui_queue.empty():
                sender, text = self.gui_queue.get_nowait()
                self._append_chat(sender, text)
        except Exception as err:
            logger.debug(f"Queue listener note: {err}")
        finally:
            self.root.after(100, self._start_queue_listener)

    def _append_chat(self, sender: str, text: str) -> None:
        """Renders a message line in the scrolled text area."""
        self.chat_display.config(state=tk.NORMAL)
        if sender == "User":
            self.chat_display.insert(tk.END, f"\n👤 You: ", "user_tag")
            self.chat_display.insert(tk.END, f"{text}\n", "body_tag")
        elif "⏰" in text:
            self.chat_display.insert(tk.END, f"\n⏰ Alert: ", "alert_tag")
            self.chat_display.insert(tk.END, f"{text.replace('⏰ ', '')}\n", "body_tag")
        else:
            self.chat_display.insert(tk.END, f"\n🎙️ {self.assistant.assistant_name}: ", "bot_tag")
            self.chat_display.insert(tk.END, f"{text}\n", "body_tag")

        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)

    def _on_send_clicked(self) -> None:
        """Triggered when user clicks 'Send' or presses Enter."""
        text = self.input_entry.get().strip()
        if not text:
            return
        self.input_entry.delete(0, tk.END)
        self._send_command_async(text)

    def _on_mic_clicked(self) -> None:
        """Triggered when user clicks the microphone button."""
        if self.is_listening:
            return

        if not self.assistant.recognizer.is_mic_available:
            self.enqueue_message("Assistant", "Microphone not detected. Please type your command in the box below.")
            return

        self.is_listening = True
        self.mic_btn.config(text="Listening...", bg=ACCENT_AMBER)
        self.set_status("🎙️ Listening...", ACCENT_AMBER)

        self.listen_thread = threading.Thread(target=self._listen_worker, daemon=True)
        self.listen_thread.start()

    def _listen_worker(self) -> None:
        """Background worker capturing microphone speech."""
        try:
            text, err_code, err_msg = self.assistant.recognizer.listen(timeout=5, phrase_time_limit=8)
            if text:
                self.root.after(0, lambda: self.set_status("⚙️ Processing...", ACCENT_BLUE))
                self.assistant.process_command(text)
            elif err_msg:
                self.assistant.speak_and_log(err_msg)
        except Exception as err:
            logger.error(f"Error in GUI listen worker: {err}")
        finally:
            self.is_listening = False
            self.root.after(0, self._reset_mic_button)

    def _reset_mic_button(self) -> None:
        """Resets mic button to idle state."""
        self.mic_btn.config(text="🎙️ Speak", bg=ACCENT_BLUE)
        self.set_status("🟢 Ready", ACCENT_GREEN)

    def _send_command_async(self, query: str) -> None:
        """Dispatches assistant command on a background worker thread."""
        self.set_status("⚙️ Processing...", ACCENT_BLUE)

        def worker():
            try:
                self.assistant.process_command(query)
            finally:
                self.root.after(0, lambda: self.set_status("🟢 Ready", ACCENT_GREEN))

        threading.Thread(target=worker, daemon=True).start()

    def run(self) -> None:
        """Starts the Tkinter main loop."""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            pass
        finally:
            self.assistant.shutdown()

