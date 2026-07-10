import json
import io
import logging

from utils.logging import (
    get_logger,
    log_with_context,
    log_performance,
    JSONFormatter,
)


def capture_logger_output(logger):
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)

    # Use production formatter
    handler.setFormatter(JSONFormatter())

    logger.addHandler(handler)
    return stream, handler


def test_logger_singleton_behavior():
    logger1 = get_logger("test_logger")
    logger2 = get_logger("test_logger")

    assert logger1 is logger2


def test_structured_log_output():
    logger = get_logger("structured_test")

    stream, handler = capture_logger_output(logger)

    try:
        log_with_context(
            logger,
            "info",
            "Test structured log",
            extra={"key": "value"},
            trace_id="trace-123",
        )

        handler.flush()
        output = stream.getvalue().strip()

        parsed = json.loads(output)

        assert parsed["message"] == "Test structured log"
        assert parsed["key"] == "value"
        assert parsed["trace_id"] == "trace-123"

    finally:
        logger.removeHandler(handler)


def test_performance_log_structure():
    logger = get_logger("perf_test")

    stream, handler = capture_logger_output(logger)

    try:
        log_performance(
            logger,
            "operation_test",
            0.456,
            metadata={"unit": "test"},
            trace_id="trace-perf",
        )

        handler.flush()
        output = stream.getvalue().strip()

        parsed = json.loads(output)

        assert parsed["message"] == "Performance: operation_test"
        assert parsed["operation"] == "operation_test"
        assert parsed["duration_seconds"] == 0.456
        assert parsed["trace_id"] == "trace-perf"

    finally:
        logger.removeHandler(handler)
