from __future__ import annotations

import json
from functools import cache
from typing import Any

from plumbum import CommandNotFound, local

type SystemProfile = dict[str, list[dict[str, Any]]]


@cache
def system_profiler(*datatypes: str) -> SystemProfile:
    """Parsed macOS `system_profiler` data for one or more datatypes.

    Runs `system_profiler <datatypes...> -json` once per datatype set and parses
    the result. Returns an empty mapping when the tool is missing or its output
    cannot be parsed, so callers stay platform-tolerant.

    datatypes: profiler datatype keys, e.g. `"SPHardwareDataType"`.
    """
    try:
        return json.loads(local["system_profiler"]("-json", *datatypes))
    except (CommandNotFound, OSError, json.JSONDecodeError):
        return {}
