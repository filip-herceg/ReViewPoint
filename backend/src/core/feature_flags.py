"""Feature flags module for enabling/disabling features.

This module provides environment variable-based feature flags.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from collections.abc import Set as AbstractSet

# Environment variable constants
ENV_FILE_VAR: Final[str] = "ENV_FILE"
REVIEWPOINT_FEATURES_VAR: Final[str] = "REVIEWPOINT_FEATURES"
FEATURE_PREFIX: Final[str] = "REVIEWPOINT_FEATURE_"

# Boolean string constants
TRUE_VALUE: Final[str] = "true"
FALSE_VALUE: Final[str] = "false"

# File path constants
CONFIG_ENV_PATH: Final[str] = "config/.env"
BACKEND_CONFIG_ENV_PATH: Final[str] = "backend/config/.env"
BACKEND_ENV_PATH: Final[str] = "backend/.env"

# Character constants
COMMENT_PREFIX: Final[str] = "#"
ASSIGNMENT_SEPARATOR: Final[str] = "="
FEATURE_SEPARATOR: Final[str] = ":"
LIST_SEPARATOR: Final[str] = ","
QUOTE_CHARS: Final[str] = "\"'"


class FeatureFlags:
    """Feature flag logic for environment variable-based features."""

    @staticmethod
    def is_enabled(feature_name: str) -> bool:
        """Check if a feature is enabled via environment variables.

        Args:
            feature_name: The name of the feature to check.

        Returns:
            True if the feature is enabled, False otherwise.

        Raises:
            OSError: If environment variable access fails.
            ValueError: If feature name parsing fails.

        """
        # Ensure settings are loaded to get .env variables
        _ensure_env_loaded()

        features_env: str = os.getenv(REVIEWPOINT_FEATURES_VAR, "")
        enabled: AbstractSet[str] = {
            f.strip() for f in features_env.split(LIST_SEPARATOR) if f.strip()
        }

        base: str = feature_name.split(FEATURE_SEPARATOR)[0].upper()
        env_var_specific: str = FEATURE_PREFIX + feature_name.upper().replace(
            FEATURE_SEPARATOR, "_"
        )
        env_var_base: str = f"{FEATURE_PREFIX}{base}"
        env_val_specific: str | None = os.getenv(env_var_specific)
        env_val_base: str | None = os.getenv(env_var_base)

        # If either is explicitly set to false, feature is disabled
        if (
            env_val_specific is not None and env_val_specific.lower() == FALSE_VALUE
        ) or (env_val_base is not None and env_val_base.lower() == FALSE_VALUE):
            return False

        # If either is true, or feature_name is in enabled set,
        # feature is enabled
        result: bool = (
            feature_name in enabled
            or (env_val_specific is not None and env_val_specific.lower() == TRUE_VALUE)
            or (env_val_base is not None and env_val_base.lower() == TRUE_VALUE)
        )
        return result


# Module-level flag to track if environment is loaded
_env_loaded: bool = False


def _ensure_env_loaded() -> None:
    """Ensure environment variables from .env file are loaded.

    Loads environment variables from a .env file into os.environ if not already
    loaded. Uses a module-level flag to track loading state.

    Raises:
        OSError: If file operations fail.
        ValueError: If environment variable parsing fails.

    """
    global _env_loaded

    # Check if we've already loaded the environment
    if _env_loaded:
        return

    try:
        # Load environment variables from the .env file into os.environ
        # This is needed because pydantic reads .env but doesn't set os.environ

        # Find the .env file (same logic as in config.py)
        env_path: str | None = os.getenv(ENV_FILE_VAR)
        env_file: Path | None = None

        if env_path:
            env_file = Path(env_path)
        elif Path(CONFIG_ENV_PATH).exists():
            env_file = Path(CONFIG_ENV_PATH)
        elif Path(BACKEND_CONFIG_ENV_PATH).exists():
            env_file = Path(BACKEND_CONFIG_ENV_PATH)
        elif Path(BACKEND_ENV_PATH).exists():
            env_file = Path(BACKEND_ENV_PATH)

        if env_file and env_file.exists():
            # Read .env file and set environment variables
            with env_file.open(encoding="utf-8") as f:
                for line_raw in f:
                    line: str = line_raw.strip()
                    if (
                        line
                        and not line.startswith(COMMENT_PREFIX)
                        and ASSIGNMENT_SEPARATOR in line
                    ):
                        key_value: list[str] = line.split(
                            ASSIGNMENT_SEPARATOR,
                            1,
                        )
                        key: str = key_value[0].strip()
                        value: str = key_value[1].strip()

                        # Remove quotes if present
                        for quote_char in QUOTE_CHARS:
                            value = value.strip(quote_char)

                        # Only set if not already in environment
                        if key not in os.environ:
                            os.environ[key] = value

        # Mark as loaded using module-level flag
        _env_loaded = True

    except (OSError, ValueError, IndexError):
        # If we can't load settings, just continue
        # Log error in production code
        pass
