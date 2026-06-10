from __future__ import annotations

import os


def export_legacy_environment() -> None:
    """Map legacy KLIPPYAI_* variables without overriding new configuration."""
    for key, value in tuple(os.environ.items()):
        if not key.startswith("KLIPPYAI_"):
            continue
        replacement = f"KLIPPERAI_{key.removeprefix('KLIPPYAI_')}"
        os.environ.setdefault(replacement, value)
