from __future__ import annotations

from pathlib import Path

DMI_ROOT = Path("/sys/class/dmi/id")


def read(path: str | Path) -> str:
    """Read a sysfs (or any) file, returning its raw contents.

    Returns an empty string when the path is missing or unreadable, so callers
    can probe Linux-only files without guarding their existence first.

    path: file to read, e.g. `/proc/cpuinfo` or `/sys/block/nvme0n1/size`.
    """
    try:
        return Path(path).read_text(encoding="utf-8")
    except OSError:
        return ""


def read_dmi(field: str) -> str:
    """Read a DMI identity field from `/sys/class/dmi/id`, stripped.

    Returns an empty string when the field is absent or unreadable.

    field: DMI file name, e.g. `board_vendor` or `bios_version`.
    """
    return read(DMI_ROOT / field).strip()
