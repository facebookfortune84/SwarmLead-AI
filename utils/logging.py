import logging
import sys
import json
from datetime import datetime
from typing import Any, Dict, Optional

# ------------------------------------------------------------------
# Configuration Defaults
# ------------------------------------------------------------------

LOG_LEVEL = logging.INFO
LOG_FORMAT = "%(message)s"

LOG_FILE_PATH = "logs/swarm.log"
ERROR_LOG_FILE_PATH = "logs/error.log"

# ------------------------------------------------------------------
# JSON Formatter
# ------------------------------------------------------------------


class JSONFormatter(logging.Formatter):
    """
    Formats logs as JSON for structured logging.
    """

    def format(self, record: logging.LogRecord) -> str:
        log_record: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "filename": record.filename,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add extra fields if present
        if hasattr(record, "extra_data") and isinstance(record.extra_data, dict):
            log_record.update(record.extra_data)

        # Trace ID support
        if hasattr(record, "trace_id"):
            log_record["trace_id"] = record.trace_id

        # Exception handling
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_record)


# ------------------------------------------------------------------
# Logger Factory
# ------------------------------------------------------------------


def get_logger(name: str) -> logging.Logger:
    """
    Returns a configured logger instance.
    """

    logger = logging.getLogger(name)

    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    logger.setLevel(LOG_LEVEL)

    formatter = JSONFormatter()

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # File Handler (all logs)
    file_handler = logging.FileHandler(LOG_FILE_PATH)
    file_handler.setFormatter(formatter)

    # Error File Handler
    error_handler = logging.FileHandler(ERROR_LOG_FILE_PATH)
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)

    logger.propagate = False

    return logger


# ------------------------------------------------------------------
# Helper Logging Functions (Structured Logging)
# ------------------------------------------------------------------


def log_with_context(
    logger: logging.Logger,
    level: str,
    message: str,
    extra: Optional[Dict[str, Any]] = None,
    trace_id: Optional[str] = None,
):
    """
    Log with structured context.

    Example:
        log_with_context(logger, "info", "Agent started", {"agent": "strategy"})
    """

    extra_data = {"extra_data": extra or {}}

    if trace_id:
        extra_data["trace_id"] = trace_id

    log_method = getattr(logger, level.lower(), logger.info)

    log_method(message, extra=extra_data)


# ------------------------------------------------------------------
# Performance Logging Helper
# ------------------------------------------------------------------


def log_performance(
    logger: logging.Logger,
    operation: str,
    duration: float,
    metadata: Optional[Dict[str, Any]] = None,
    trace_id: Optional[str] = None,
):
    """
    Specialized performance log for analytics.

    Example:
        log_performance(logger, "agent_execution", 0.234, {"agent": "audience"})
    """

    log_with_context(
        logger,
        "info",
        f"Performance: {operation}",
        extra={
            "operation": operation,
            "duration_seconds": duration,
            **(metadata or {}),
        },
        trace_id=trace_id,
    )