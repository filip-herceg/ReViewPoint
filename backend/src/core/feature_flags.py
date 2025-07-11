import os
from collections.abc import Set


# Stub for feature flags module
# Add actual feature flag logic as needed
class FeatureFlags:
    """Feature flag logic for enabling/disabling features via environment variables."""

    # No class attributes/constants needed yet, but if added, use Final/ ClassVar

    @staticmethod
    def is_enabled(feature_name: str) -> bool:
        """Check if a feature is enabled via environment variables.

        Args:
            feature_name (str): The name of the feature to check.

        Returns:
            bool: True if the feature is enabled, False otherwise.

        """
        # Ensure settings are loaded to get .env variables
        _ensure_env_loaded()

        features: str = os.getenv("REVIEWPOINT_FEATURES", "")
        enabled: Set[str] = {f.strip() for f in features.split(",") if f.strip()}

        base: str = feature_name.split(":")[0].upper()
        env_var_specific: str = "REVIEWPOINT_FEATURE_" + feature_name.upper().replace(
            ":",
            "_",
        )
        env_var_base: str = f"REVIEWPOINT_FEATURE_{base}"
        env_val_specific: str | None = os.getenv(env_var_specific)
        env_val_base: str | None = os.getenv(env_var_base)

        # If either is explicitly set to false, feature is disabled
        if (env_val_specific is not None and env_val_specific.lower() == "false") or (
            env_val_base is not None and env_val_base.lower() == "false"
        ):
            return False

        # If either is true, or feature_name is in enabled set, feature is enabled
        result: bool = (
            feature_name in enabled
            or (env_val_specific is not None and env_val_specific.lower() == "true")
            or (env_val_base is not None and env_val_base.lower() == "true")
        )
        return result


def _ensure_env_loaded() -> None:
    """Ensure environment variables from .env file are loaded into os.environ."""
    # Check if we've already loaded the environment
    if hasattr(_ensure_env_loaded, "_loaded"):
        return

    try:
        from src.core.config import get_settings

        settings = get_settings()

        # Load environment variables from the .env file into os.environ
        # This is needed because pydantic reads .env but doesn't set os.environ
        import os
        from pathlib import Path

        # Find the .env file (same logic as in config.py)
        env_path = os.getenv("ENV_FILE")
        env_file = None

        if env_path:
            env_file = Path(env_path)
        elif Path("config/.env").exists():
            env_file = Path("config/.env")
        elif Path("backend/config/.env").exists():
            env_file = Path("backend/config/.env")
        elif Path("backend/.env").exists():
            env_file = Path("backend/.env")

        if env_file and env_file.exists():
            # Read .env file and set environment variables
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")

                        # Only set if not already in environment
                        if key not in os.environ:
                            os.environ[key] = value

        # Mark as loaded
        _ensure_env_loaded._loaded = True

    except Exception:
        # If we can't load settings, just continue
        pass
