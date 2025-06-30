import os


# Stub for feature flags module
# Add actual feature flag logic as needed
class FeatureFlags:
    @staticmethod
    def is_enabled(feature_name: str) -> bool:
        features = os.getenv("REVIEWPOINT_FEATURES", "")
        enabled = {f.strip() for f in features.split(",") if f.strip()}
        # Option 2: Also check individual env vars
        env_var = "REVIEWPOINT_FEATURE_" + feature_name.upper().replace(":", "_")
        env_val = os.getenv(env_var)
        result = feature_name in enabled or (
            env_val is not None and env_val.lower() == "true"
        )
        # print(
        #     f"[FeatureFlags] Checking '{feature_name}' against enabled: {enabled} and {env_var}={env_val} -> {result}",
        #     file=sys.stderr,
        # )
        return result
