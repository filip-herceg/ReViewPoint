import os
from collections.abc import Set


# Stub for feature flags module
# Add actual feature flag logic as needed
class FeatureFlags:
    """
    Feature flag logic for enabling/disabling features via environment variables.
    """

    # No class attributes/constants needed yet, but if added, use Final/ ClassVar

    @staticmethod
    def is_enabled(feature_name: str) -> bool:
        """
        Check if a feature is enabled via environment variables.

        Args:
            feature_name (str): The name of the feature to check.

        Returns:
            bool: True if the feature is enabled, False otherwise.
        """
        features: str = os.getenv("REVIEWPOINT_FEATURES", "")
        enabled: Set[str] = {f.strip() for f in features.split(",") if f.strip()}

        base: str = feature_name.split(":")[0].upper()
        env_var_specific: str = "REVIEWPOINT_FEATURE_" + feature_name.upper().replace(
            ":", "_"
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
