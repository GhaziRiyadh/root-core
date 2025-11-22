# ...existing code...
from __future__ import annotations
import logging
import logging.handlers
import os
from typing import Any, Dict, Optional, MutableMapping, override

from core.env_manager import EnvManager

# /d:/projects/mutor/backend/src/core/logger.py
"""
Simple logging setup for the project.

Provides:
- configure_logging(...) to configure root logger (idempotent)
- get_logger(name) -> LoggerAdapter that preserves "extra" context when used
"""


DEFAULT_LEVEL = logging.INFO
LOG_DIR = EnvManager.get("MUTOR_LOG_DIR", "logs")
LOG_FILE = os.path.join(LOG_DIR, "app.log")
MAX_BYTES = 10 * 1024 * 1024  # 10 MB
BACKUP_COUNT = 5


class ContextLoggerAdapter(logging.LoggerAdapter):
    """
    LoggerAdapter that ensures "extra" dict exists and is merged into the LogRecord.
    Use logger = get_logger(__name__).bind(user_id=..., request_id=...)
    """

    @override
    def process(
        self, msg: Any, kwargs: MutableMapping[str, Any]
    ) -> tuple[Any, MutableMapping[str, Any]]:
        # kwargs is a mutable mapping per logging.LoggerAdapter.process signature
        extra_any = kwargs.get("extra", {})
        # Ensure we have plain dicts for unpacking (satisfy type checkers)
        base_extra = (
            dict(self.extra) if not isinstance(self.extra, dict) else self.extra
        )
        call_extra = dict(extra_any) if not isinstance(extra_any, dict) else extra_any
        merged: Dict[str, Any] = {**base_extra, **call_extra}
        kwargs["extra"] = merged  # type: ignore[index]
        return msg, kwargs

    def bind(self, **kwargs: Any) -> "ContextLoggerAdapter":
        # combine adapter extra with provided kwargs
        base_extra = (
            dict(self.extra) if not isinstance(self.extra, dict) else self.extra
        )
        new_extra: Dict[str, Any] = {**base_extra, **kwargs}
        return ContextLoggerAdapter(self.logger, new_extra)


class ExtraFilter(logging.Filter):
    """
    Ensures that 'extra' keys exist on the LogRecord to avoid KeyError in formatters.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "extra"):
            record.extra = {}
        return True


def _make_formatter() -> logging.Formatter:
    # ISO timestamp, level, name, message, and serialized extra if present
    fmt = "%(asctime)s %(levelname)-8s %(name)s %(message)s"
    # include a stable timezone-less ISO format for timestamps
    formatter = logging.Formatter(fmt=fmt, datefmt="%Y-%m-%dT%H:%M:%S")
    return formatter


def configure_logging(
    level: int = DEFAULT_LEVEL,
    *,
    log_file: Optional[str] = None,
    max_bytes: int = MAX_BYTES,
    backup_count: int = BACKUP_COUNT,
) -> None:
    """
    Configure root logger. Safe to call multiple times; ensures required handlers
    (console and rotating file) are present and avoids duplicating them.
    """
    root = logging.getLogger()
    root.setLevel(level)
    formatter = _make_formatter()

    # Ensure console handler exists
    has_stream = any(
        isinstance(h, logging.StreamHandler)
        and not isinstance(h, logging.handlers.RotatingFileHandler)
        for h in root.handlers
    )
    if not has_stream:
        ch = logging.StreamHandler()
        ch.setLevel(level)
        ch.setFormatter(formatter)
        ch.addFilter(ExtraFilter())
        root.addHandler(ch)

    # File handler
    if log_file is None:
        log_file = LOG_FILE

    # Make directories if needed
    try:
        os.makedirs(os.path.dirname(log_file) or ".", exist_ok=True)
    except Exception as e:
        # if you can't create dirs, fall through and try to create a handler (it may still fail)
        print(e)

    # Add a rotating file handler only if not already present for this path
    abs_log_file = os.path.abspath(log_file)
    has_file = False
    for h in root.handlers:
        try:
            # RotatingFileHandler exposes a baseFilename attribute
            if (
                isinstance(h, logging.handlers.RotatingFileHandler)
                and os.path.abspath(getattr(h, "baseFilename", "")) == abs_log_file
            ):
                has_file = True
                break
        except Exception as e:
            print("Error while checking handler", h, e)
            continue

    if not has_file:
        try:
            fh = logging.handlers.RotatingFileHandler(
                log_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
            )
            fh.setLevel(level)
            fh.setFormatter(formatter)
            fh.addFilter(ExtraFilter())
            root.addHandler(fh)
        except Exception as e:
            # If a file handler cannot be created, log a warning to a console
            root.warning(
                "Could not create log file handler; continuing with console logging only."
            )
            print("error creating file handler:", e)


def get_logger(name: str, *, level: Optional[int] = None) -> ContextLoggerAdapter:
    """
    Return a ContextLoggerAdapter for the given name. Call configure_logging() once at startup.
    """
    if level is not None:
        logging.getLogger(name).setLevel(level)
    logger = logging.getLogger(name)
    return ContextLoggerAdapter(logger, {})


# Initialize with defaults when module is imported in apps that don't call a configuring explicitly.
configure_logging()

__all__ = ["configure_logging", "get_logger", "ContextLoggerAdapter"]
