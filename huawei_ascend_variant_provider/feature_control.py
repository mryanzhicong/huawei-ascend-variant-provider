from __future__ import annotations

AVAILABLE_FEATURES: set[str] = {"npu_type", "driver_version", "cann_version"}

# Configure disabled detection items here.
# Allowed values: "npu_type", "driver_version", "cann_version"
# Example:
# DISABLED_FEATURES: set[str] = {"driver_version", "cann_version"}
DISABLED_FEATURES: set[str] = set()


def is_feature_disabled(feature: str) -> bool:
    return feature.strip().lower() in {item.strip().lower() for item in DISABLED_FEATURES}
