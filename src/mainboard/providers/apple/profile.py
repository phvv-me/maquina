from __future__ import annotations

from ... import shell


def apple_system_profile() -> shell.SystemProfile:
    """Return macOS hardware and display profiler data."""
    return shell.system_profiler("SPHardwareDataType", "SPDisplaysDataType")
