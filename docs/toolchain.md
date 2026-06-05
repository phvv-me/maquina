# Toolchain

`Machine.toolchain`, also carried in the snapshot, reports the C, C++, and CUDA compilers and build systems found on the host PATH, so a tool can learn the machine's real build capability without shelling out itself.

```python
from mainboard import Machine

toolchain = Machine().toolchain
for tool in toolchain.tools:
    print(tool.name, tool.version, tool.path)
```

Only tools that are actually on PATH are kept, so the list reflects what the host can really run. Each tool keeps its registered order, grouped by category.

## In the snapshot

The `toolchain` field of `Machine().model_dump_json()` lists every available tool:

```json
{
  "tools": [
    {
      "name": "gcc",
      "category": "c-compiler",
      "path": "/usr/bin/gcc",
      "version": "13.2.0",
      "available": true
    },
    {
      "name": "clang",
      "category": "c-compiler",
      "path": "/usr/bin/clang",
      "version": "21.0.0",
      "available": true
    },
    {
      "name": "nvcc",
      "category": "cuda-compiler",
      "path": "/usr/local/cuda/bin/nvcc",
      "version": "13.0",
      "available": true
    },
    {
      "name": "cmake",
      "category": "build-system",
      "path": "/usr/bin/cmake",
      "version": "3.28.3",
      "available": true
    },
    {
      "name": "ninja",
      "category": "build-system",
      "path": "/usr/bin/ninja",
      "version": "1.11.1",
      "available": true
    }
  ]
}
```

`version` is `null` when the tool is present but its version output cannot be parsed.

## DetectedTool

Each entry in `tools` is a `DetectedTool`, the structured result of one probe.

| field | type | meaning |
|---|---|---|
| `name` | `str` | display name of the tool, e.g. `gcc` or `cmake` |
| `category` | `ToolCategory` | toolchain group the tool belongs to |
| `path` | `str \| None` | absolute path to the resolved binary, `None` when not on PATH |
| `version` | `str \| None` | parsed version string, `None` when absent or unparseable |
| `available` | `bool` | whether the binary was found on PATH |

## ToolCategory

`ToolCategory` is a `StrEnum` that buckets each tool.

| member | value |
|---|---|
| `C_COMPILER` | `c-compiler` |
| `CXX_COMPILER` | `cxx-compiler` |
| `CUDA_COMPILER` | `cuda-compiler` |
| `BUILD_SYSTEM` | `build-system` |

`Toolchain.by_category` regroups the available tools into these buckets.

```python
from mainboard import Machine, ToolCategory

toolchain = Machine().toolchain
cuda = toolchain.by_category.get(ToolCategory.CUDA_COMPILER, ())
print([tool.name for tool in cuda])
```

## How it is probed

Discovery is data-driven. A `ToolProbe` is an immutable recipe for finding one tool, and the module-level `TOOL_PROBES` tuple is the registry that `Toolchain.probe()` runs.

| field | type | meaning |
|---|---|---|
| `name` | `str` | display name reported on the `DetectedTool` |
| `category` | `ToolCategory` | toolchain group the tool belongs to |
| `binaries` | `tuple[str, ...]` | candidate executable names, tried in order until one is on PATH |
| `version_args` | `tuple[str, ...]` | arguments that make the binary print its version, default `("--version",)` |
| `pattern` | `re.Pattern[str]` | regex whose first group captures the version from the command output |

For each probe, the first binary found on PATH wins. Its version output is captured and the pattern's first group becomes `version`. The default registry covers gcc, clang, g++, clang++, nvcc, cmake, ninja, make, and meson.

## Extending the registry

Adding a tool is one line. Append a `ToolProbe` to `TOOL_PROBES` and it is discovered on the next probe, with no change to the discovery logic.

```python
from mainboard.models.toolchain import TOOL_PROBES, ToolProbe
from mainboard import ToolCategory

bazel = ToolProbe("bazel", ToolCategory.BUILD_SYSTEM, ("bazel",))
probes = (*TOOL_PROBES, bazel)

from mainboard import Toolchain

toolchain = Toolchain.probe(probes)
```

A tool with a non-standard version command sets `version_args` and `pattern`.

```python
import re
from mainboard.models.toolchain import ToolProbe
from mainboard import ToolCategory

icx = ToolProbe(
    "icx",
    ToolCategory.C_COMPILER,
    ("icx",),
    version_args=("--version",),
    pattern=re.compile(r"(\d+\.\d+\.\d+)"),
)
```

A brand-new family of tools is one `ToolCategory` member plus its probes, so the model grows by adding code rather than editing the probe loop.
