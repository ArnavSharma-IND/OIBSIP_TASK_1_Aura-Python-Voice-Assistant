"""
Email Automation Service Module for ArnavSharma_Task1.
Provides SMTP-based email dispatch with alias resolution, multi-step slot filling,
and mandatory voice/text confirmation before transmission.
"""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, Optional, Tuple

from utils.helpers import is_valid_email
from utils.logger import get_logger

logger = get_logger("EmailService")


class EmailService:
    """Manages secure SMTP email dispatch and contact address resolution."""

    def __init__(
        self,
        smtp_server: Optional[str] = None,
        smtp_port: Optional[int] = None,
        smtp_email: Optional[str] = None,
        smtp_password: Optional[str] = None,
        use_tls: bool = True,
        contacts: Optional[Dict[str, str]] = None,
    ):
        # Prefer parameters, fall back to environment variables
        self.smtp_server = smtp_server or os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(smtp_port or os.getenv("SMTP_PORT", "587"))
        self.smtp_email = (smtp_email or os.getenv("SMTP_EMAIL", "")).strip()
        self.smtp_password = (smtp_password or os.getenv("SMTP_PASSWORD", "")).strip()
        self.use_tls = use_tls
        self.contacts = {k.lower(): v for k, v in (contacts or {}).items()}

    def update_contacts(self, contacts: Dict[str, str]) -> None:
        """Updates the alias contact directory."""
        self.contacts = {k.lower(): v for k, v in contacts.items()}

    def resolve_recipient(self, query: str) -> Optional[str]:
        """
        Resolves a user-provided alias or email string into a validated email address.
        Examples:
          - 'arnav' -> 'arnav.sharma.dev@example.com' (from contacts)
          - 'user@example.com' -> 'user@example.com'
        """
        if not query:
            return None

        clean = query.lower().strip()

        # Check contact alias dictionary
        if clean in self.contacts:
            return self.contacts[clean]

        # Check if direct email format
        if is_valid_email(clean):
            return clean

        return None

    def is_configured(self) -> bool:
        """Returns True if valid SMTP credentials are configured in .env."""
        placeholders = {
            "",
            "your_email@gmail.com",
            "your_app_password_here",
            "your_16_char_app_password_here",
        }
        return bool(
            self.smtp_email
            and self.smtp_email not in placeholders
            and self.smtp_password
            and self.smtp_password not in placeholders
        )

    def send_email(
        self,
        recipient: str,
        subject: str,
        body: str,
    ) -> Tuple[bool, str]:
        """
        Sends an email via SMTP.

        If SMTP credentials are not configured, executes in simulated (dry-run) mode
        so the assistant demonstrates full conversational automation safely.

        Args:
            recipient: Destination email address.
            subject: Email subject line.
            body: Email body content.

        Returns:
            Tuple of (success: bool, spoken_feedback: str)
        """
        resolved_to = self.resolve_recipient(recipient)
        if not resolved_to:
            return False, f"Invalid recipient address '{recipient}'. Please provide a valid email or contact name."

        if not subject.strip():
            subject = "Message from Voice Assistant"

        if not body.strip():
            return False, "Cannot send an email with an empty message body."

        # Dry-run simulation if real credentials are not provided
        if not self.is_configured():
            msg = (
                f"Simulated email sent to {resolved_to} with subject '{subject}'. "
                f"To send real emails, please configure SMTP_EMAIL and SMTP_PASSWORD in your .env file."
            )
            logger.info(f"[SIMULATED EMAIL] To: {resolved_to} | Subject: '{subject}' | Message: '{body[:40]}...'")
            return True, msg

        # Real SMTP dispatch
        try:
            logger.info(f"Connecting to SMTP server {self.smtp_server}:{self.smtp_port}...")

            # Construct MIME email
            msg = MIMEMultipart("alternative")
            msg["From"] = f"Voice Assistant <{self.smtp_email}>"
            msg["To"] = resolved_to
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain", "utf-8"))

            if self.smtp_port == 465:
                # SSL connection
                with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, timeout=10) as server:
                    server.login(self.smtp_email, self.smtp_password)
                    server.send_message(msg)
            else:
                # Standard SMTP with STARTTLS
                with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10) as server:
                    server.ehlo()
                    if self.use_tls:
                        server.starttls()
                        server.ehlo()
                    server.login(self.smtp_email, self.smtp_password)
                    server.send_message(msg)

            logger.info(f"Email successfully dispatched to {resolved_to}.")
            return True, f"Email has been sent successfully to {resolved_to}."

        except smtplib.SMTPAuthenticationError as auth_err:
            logger.error(f"SMTP authentication failure: {auth_err}")
            return False, "SMTP authentication failed. Please check your email and app password in .env."

        except smtplib.SMTPConnectError as conn_err:
            logger.error(f"SMTP connection error: {conn_err}")
            return False, "Failed to connect to the email server. Please check your internet connection."

        except Exception as err:
            logger.error(f"Unexpected error sending email: {err}")
            return False, f"Could not send email due to an error: {str(err)}"

