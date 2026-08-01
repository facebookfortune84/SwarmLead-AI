"""
SMTP email sender for the autonomous growth loop.

Sends plaintext email via the configured SMTP provider (env: SMTP_HOST,
SMTP_PORT, SMTP_USER, SMTP_PASS, SMTP_FROM). Rate-limited per send window
and supports a dry-run mode (OUTREACH_DRY_RUN=1) so the pipeline can be
validated before real delivery is enabled.

Security: credentials come only from environment variables. The sender
never writes passwords to disk or logs.
"""

import asyncio
import logging
import os
import smtplib
import ssl
import time
from email.message import EmailMessage
from email.utils import formataddr
from typing import List, Optional

logger = logging.getLogger("EmailSender")


class EmailSender:
    """Thin, rate-limited SMTP client used by the growth loop."""

    def __init__(self) -> None:
        self.host = os.getenv("SMTP_HOST", "")
        self.port = int(os.getenv("SMTP_PORT", "587"))
        self.user = os.getenv("SMTP_USER", "")
        self.password = os.getenv("SMTP_PASS", "")
        self.from_name = os.getenv("SMTP_FROM_NAME", "SwarmOS")
        self.from_email = os.getenv("SMTP_FROM", self.user)
        self.dry_run = os.getenv("OUTREACH_DRY_RUN", "0") == "1"
        self.rate_limit_per_hour = int(os.getenv("OUTREACH_RATE_LIMIT_PER_HOUR", "40"))
        self._sent_window: List[float] = []

    @property
    def configured(self) -> bool:
        return bool(self.host and self.user and self.password)

    async def send(
        self,
        to_email: str,
        subject: str,
        body: str,
        reply_to: Optional[str] = None,
    ) -> dict:
        """Send one email. Returns a status dict; never raises for delivery."""
        if not self.configured:
            return {
                "status": "unconfigured",
                "message": "SMTP not configured (SMTP_HOST/USER/PASS missing)",
            }

        if self.dry_run:
            logger.info("DRY RUN — would send to %s: %s", to_email, subject)
            return {"status": "dry_run", "to_email": to_email, "subject": subject}

        now = time.time()
        self._sent_window = [t for t in self._sent_window if now - t < 3600]
        if len(self._sent_window) >= self.rate_limit_per_hour:
            return {
                "status": "rate_limited",
                "message": f"Hourly limit {self.rate_limit_per_hour} reached",
            }
        self._sent_window.append(now)

        try:
            await asyncio.to_thread(
                self._send_sync,
                to_email,
                subject,
                body,
                reply_to,
            )
            logger.info("Sent to %s: %s", to_email, subject)
            return {"status": "sent", "to_email": to_email, "subject": subject}
        except Exception as exc:  # pragma: no cover - network dependent
            logger.warning("Send failed for %s: %s", to_email, exc)
            return {"status": "failed", "error": str(exc)}

    def _send_sync(
        self,
        to_email: str,
        subject: str,
        body: str,
        reply_to: Optional[str] = None,
    ) -> None:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = formataddr((self.from_name, self.from_email))
        msg["To"] = to_email
        if reply_to:
            msg["Reply-To"] = reply_to
        msg.set_content(body)

        context = ssl.create_default_context()
        with smtplib.SMTP(self.host, self.port, timeout=30) as server:
            server.starttls(context=context)
            server.login(self.user, self.password)
            server.send_message(msg)

    async def send_bulk(self, items: List[dict]) -> List[dict]:
        """Send several emails sequentially (rate-limited)."""
        results = []
        for item in items:
            results.append(
                await self.send(
                    item["to_email"],
                    item["subject"],
                    item["body"],
                    reply_to=item.get("reply_to"),
                )
            )
            await asyncio.sleep(0.5)
        return results


email_sender = EmailSender()
