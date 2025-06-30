import os


# Stub for feature flags module
# Add actual feature flag logic as needed
class FeatureFlags:
    @staticmethod
    def is_enabled(feature_name: str) -> bool:
        features = os.getenv("REVIEWPOINT_FEATURES", "")
        enabled = {f.strip() for f in features.split(",") if f.strip()}
        # Check both the generic and specific env vars
        base = feature_name.split(":")[0].upper()
        env_var_specific = "REVIEWPOINT_FEATURE_" + feature_name.upper().replace(
            ":", "_"
        )
        env_var_base = f"REVIEWPOINT_FEATURE_{base}"
        env_val_specific = os.getenv(env_var_specific)
        env_val_base = os.getenv(env_var_base)
        # If either is explicitly set to false, feature is disabled
        if (env_val_specific is not None and env_val_specific.lower() == "false") or (
            env_val_base is not None and env_val_base.lower() == "false"
        ):
            return False
        # If either is true, or feature_name is in enabled set, feature is enabled
        result = (
            feature_name in enabled
            or (env_val_specific is not None and env_val_specific.lower() == "true")
            or (env_val_base is not None and env_val_base.lower() == "true")
        )
        return result
