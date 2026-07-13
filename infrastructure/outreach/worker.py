"""
Outreach queue worker.

Migrated from SwarmEnterprise v2.
"""

from __future__ import annotations

import importlib
import logging
import os
import threading
import time
from typing import Iterable

from infrastructure.queue.task_queue import (
    dequeue_task,
    enqueue_task,
)

logger = logging.getLogger("OutreachWorker")


class OutreachTask:
    def __init__(
        self,
        to_email: str,
        subject: str,
        body: str,
        attempts: int = 0,
    ):

        self.to_email = to_email
        self.subject = subject
        self.body = body
        self.attempts = attempts


def enqueue_campaign(
    recipients: Iterable[str],
    subject: str,
    body: str,
    from_name: str = "SwarmOS",
):

    recipient_list = [
        recipient.strip() for recipient in recipients if recipient and recipient.strip()
    ]

    if not recipient_list:
        logger.warning("Outreach campaign skipped: no recipients")

        return

    for recipient in recipient_list:
        enqueue_task(
            {
                "to_email": recipient,
                "subject": subject,
                "body": body,
                "attempts": 0,
                "from_name": from_name,
                "campaign": True,
            }
        )

        logger.info(
            "Enqueued outreach campaign to %s",
            recipient,
        )


def enqueue_outreach(
    to_email: str,
    subject: str,
    body: str,
):

    enqueue_campaign(
        [to_email],
        subject,
        body,
    )


def _worker_loop(
    stop_event: threading.Event,
):

    try:
        email_module = importlib.import_module("agents.outreach.email_engine")
        EmailTools = email_module.EmailTools

    except Exception:
        logger.warning("EmailTools unavailable; worker disabled")

        return

    email_tool = EmailTools()

    while not stop_event.is_set():
        item = dequeue_task(timeout=1)

        if not item:
            continue

        task = OutreachTask(
            item.get("to_email", ""),
            item.get("subject", ""),
            item.get("body", ""),
            item.get("attempts", 0),
        )

        try:
            result = email_tool.send_email(
                task.to_email,
                task.subject,
                task.body,
            )

            if str(result).startswith("SUCCESS"):
                logger.info(
                    "Outreach sent to %s",
                    task.to_email,
                )

            else:
                logger.warning(
                    "Outreach failed for %s: %s",
                    task.to_email,
                    result,
                )

                max_retries = int(
                    os.getenv(
                        "OUTREACH_MAX_RETRIES",
                        "3",
                    )
                )

                if task.attempts < max_retries:
                    next_attempt = task.attempts + 1

                    backoff = 2**next_attempt

                    time.sleep(backoff)

                    enqueue_task(
                        {
                            "to_email": task.to_email,
                            "subject": task.subject,
                            "body": task.body,
                            "attempts": next_attempt,
                        }
                    )

        except Exception:
            logger.exception("Outreach worker failure")


_worker_thread = None
_stop_event = None


def start_worker():

    global _worker_thread
    global _stop_event

    if _worker_thread and _worker_thread.is_alive():
        return

    _stop_event = threading.Event()

    _worker_thread = threading.Thread(
        target=_worker_loop,
        args=(_stop_event,),
        daemon=True,
    )

    _worker_thread.start()

    logger.info("Outreach worker started")


def stop_worker():

    global _worker_thread
    global _stop_event

    if _stop_event:
        _stop_event.set()

    if _worker_thread:
        _worker_thread.join(timeout=5)

    logger.info("Outreach worker stopped")
