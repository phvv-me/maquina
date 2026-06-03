from __future__ import annotations

from functools import cache
from importlib import import_module
from typing import Any


def text(value: Any) -> str:
    """Convert CUDA/NVML byte strings and scalars to text."""
    if isinstance(value, bytes):
        return value.decode(errors="replace")
    return str(value)


class NvidiaApis:
    """Lazy CUDA/NVML imports for the NVIDIA provider."""

    def __init__(self) -> None:
        self.runtime: Any = import_module("cuda.bindings.runtime")
        self.system: Any = import_module("cuda.core.system")
        try:
            self.nvml: Any = import_module("cuda.bindings._nvml")
        except ModuleNotFoundError:
            self.nvml = import_module("cuda.bindings.nvml")
        cuda_core: Any = import_module("cuda.core")
        self.cuda_device_type: Any = cuda_core.Device
        self.nvml_errors: tuple[type[Exception], ...] = tuple(
            error
            for name in (
                "NotSupportedError",
                "NoPermissionError",
                "UnknownError",
                "GpuIsLostError",
            )
            if isinstance(error := getattr(self.nvml, name, None), type)
            and issubclass(error, Exception)
        )


@cache
def nvidia_apis() -> NvidiaApis:
    """Return cached CUDA/NVML imports for NVIDIA devices."""
    return NvidiaApis()
