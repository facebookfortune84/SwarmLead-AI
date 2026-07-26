"""
Secret Rotation Framework

Configuration-driven secret rotation using existing env var infrastructure.
Supports scheduled key rotation with grace periods for zero-downtime rotation.
"""

import logging
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

ROTATION_CONFIG = {
    "JWT_SECRET_KEY": {
        "min_age_days": 90,
        "grace_period_minutes": 5,
        "env_var": "JWT_SECRET_KEY",
        "previous_env_var": "JWT_SECRET_KEY_PREVIOUS",
    },
    "ELEVENLABS_API_KEY": {
        "min_age_days": 30,
        "grace_period_minutes": 0,
        "env_var": "ELEVENLABS_API_KEY",
        "previous_env_var": "ELEVENLABS_API_KEY_PREVIOUS",
    },
}


def get_secret_age_days(secret_name: str) -> Optional[float]:
    """Get the age of a secret in days from its rotation timestamp."""
    timestamp_var = f"{secret_name}_ROTATED_AT"
    timestamp_str = os.getenv(timestamp_var)
    if not timestamp_str:
        return None
    try:
        rotated_at = datetime.fromisoformat(timestamp_str)
        return (datetime.now(timezone.utc) - rotated_at.replace(tzinfo=timezone.utc)).total_seconds() / 86400
    except (ValueError, TypeError):
        return None


def is_rotation_due(secret_name: str) -> bool:
    """Check if a secret is due for rotation based on its configured min age."""
    config = ROTATION_CONFIG.get(secret_name)
    if not config:
        return False
    age_days = get_secret_age_days(secret_name)
    if age_days is None:
        return False
    return age_days >= config["min_age_days"]


def rotate_secret(secret_name: str, new_value: str) -> bool:
    """Rotate a secret by moving current to previous and setting new value."""
    config = ROTATION_CONFIG.get(secret_name)
    if not config:
        logger.error(f"No rotation config for secret: {secret_name}")
        return False

    current = os.getenv(config["env_var"], "")
    if not current:
        logger.warning(f"No current value for {secret_name}, setting directly")
        _set_env_var(config["env_var"], new_value)
        _set_env_var(f"{secret_name}_ROTATED_AT", datetime.now(timezone.utc).isoformat())
        return True

    _set_env_var(config["previous_env_var"], current)
    _set_env_var(config["env_var"], new_value)
    _set_env_var(f"{secret_name}_ROTATED_AT", datetime.now(timezone.utc).isoformat())
    logger.info(f"Rotated secret: {secret_name}")
    return True


def get_previous_secret(secret_name: str) -> Optional[str]:
    """Get the previous value of a rotated secret (for grace period validation)."""
    config = ROTATION_CONFIG.get(secret_name)
    if not config:
        return None
    return os.getenv(config["previous_env_var"])


def list_rotation_status() -> List[Dict[str, object]]:
    """List all configured secrets and their rotation status."""
    statuses = []
    for secret_name, config in ROTATION_CONFIG.items():
        current = os.getenv(config["env_var"], "")
        age = get_secret_age_days(secret_name)
        due = is_rotation_due(secret_name)
        statuses.append({
            "secret": secret_name,
            "configured": bool(current),
            "age_days": round(age, 1) if age is not None else None,
            "rotation_due": due,
            "min_age_days": config["min_age_days"],
        })
    return statuses


def _set_env_var(name: str, value: str) -> None:
    """Set an environment variable (in-process only; use .env for persistence)."""
    os.environ[name] = value


__all__ = [
    "get_secret_age_days",
    "is_rotation_due",
    "rotate_secret",
    "get_previous_secret",
    "list_rotation_status",
]
