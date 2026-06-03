from __future__ import annotations

import pytest

from mainboard import AMDGPU, NvidiaGPU
from mainboard.gpu import GPU
from mainboard.npu import NPU
from mainboard.providers.apple import AppleGPU, AppleNPU


def test_each_root_owns_its_own_registry() -> None:
    """`GPU` and `NPU` are separate roots, each listing only its own providers."""
    assert GPU.registry() is not NPU.registry()
    assert {GPU, AMDGPU, AppleGPU, NvidiaGPU} <= set(GPU.registry())
    assert {NPU, AppleNPU} <= set(NPU.registry())
    assert NvidiaGPU not in NPU.registry()


def test_root_all_fans_out_over_providers(monkeypatch: pytest.MonkeyPatch) -> None:
    """The root `all` concatenates each provider's own probe, skipping the root."""
    apple_gpu = AppleGPU(index=7)
    apple_npu = AppleNPU(index=3)
    monkeypatch.setattr(AppleGPU, "all", classmethod(lambda cls: (apple_gpu,)))
    monkeypatch.setattr(AppleNPU, "all", classmethod(lambda cls: (apple_npu,)))
    assert apple_gpu in GPU.all()
    assert apple_npu in NPU.all()
