from __future__ import annotations

import pytest

from mainboard import Board
from mainboard.models import board as board_mod


def test_linux_probe_reads_dmi_sysfs(monkeypatch: pytest.MonkeyPatch) -> None:
    """On Linux every field is read from its DMI sysfs file."""
    values = {
        "board_vendor": "ASUSTeK COMPUTER INC.",
        "board_name": "ROG STRIX X670E",
        "board_version": "Rev 1.xx",
        "bios_vendor": "American Megatrends",
        "bios_version": "2.10",
    }
    monkeypatch.setattr(board_mod.platform, "system", lambda: "Linux")
    monkeypatch.setattr(board_mod.shell, "read_dmi", lambda field: values[field])

    board = Board.probe()

    assert board.vendor == "ASUSTeK COMPUTER INC."
    assert board.model == "ROG STRIX X670E"
    assert board.version == "Rev 1.xx"
    assert board.bios_vendor == "American Megatrends"
    assert board.bios_version == "2.10"


def test_macos_probe_uses_system_profiler(monkeypatch: pytest.MonkeyPatch) -> None:
    """On macOS the board is read from `system_profiler` with Apple as vendor."""
    profile = {"SPHardwareDataType": [{"machine_model": "Mac16,8", "machine_name": "MacBook Pro"}]}
    monkeypatch.setattr(board_mod.platform, "system", lambda: "Darwin")
    monkeypatch.setattr(board_mod.shell, "system_profiler", lambda *types: profile)

    board = Board.probe()

    assert board.vendor == "Apple"
    assert board.model == "Mac16,8"
    assert board.version == "MacBook Pro"
    assert board.bios_vendor == ""


def test_macos_probe_falls_back_to_chip(monkeypatch: pytest.MonkeyPatch) -> None:
    """Without a machine model the chip name stands in as the board model."""
    profile = {"SPHardwareDataType": [{"chip_type": "Apple M4 Pro"}]}
    monkeypatch.setattr(board_mod.platform, "system", lambda: "Darwin")
    monkeypatch.setattr(board_mod.shell, "system_profiler", lambda *types: profile)

    board = Board.probe()

    assert board.model == "Apple M4 Pro"
    assert board.version == ""


def test_macos_probe_tolerates_profiler_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    """An empty `system_profiler` result yields an all-empty board, never an error."""
    monkeypatch.setattr(board_mod.platform, "system", lambda: "Darwin")
    monkeypatch.setattr(board_mod.shell, "system_profiler", lambda *types: {})

    board = Board.probe()

    assert board == Board()
