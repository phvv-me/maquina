# Toolchain

`Machine.toolchain`（也包含在快照中）报告主机 PATH 上找到的 C、C++、CUDA 编译器和构建系统，因此工具无需自己调用即可了解机器真实的构建能力。

```python
from mainboard import Machine

toolchain = Machine().toolchain
for tool in toolchain.tools:
    print(tool.name, tool.version, tool.path)
```

只保留实际位于 PATH 上的工具，因此该列表反映主机真正能够运行的内容。每个工具保持其注册顺序，并按类别分组。

## 在快照中

`Machine().model_dump_json()` 的 `toolchain` 字段列出每个可用工具：

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

当工具存在但其版本输出无法解析时，`version` 为 `null`。

## DetectedTool

`tools` 中的每一项都是一个 `DetectedTool`，即一次探测的结构化结果。

| 字段 | 类型 | 含义 |
|---|---|---|
| `name` | `str` | 工具的显示名称，例如 `gcc` 或 `cmake` |
| `category` | `ToolCategory` | 工具所属的工具链分组 |
| `path` | `str \| None` | 解析后二进制文件的绝对路径，不在 PATH 上时为 `None` |
| `version` | `str \| None` | 解析出的版本字符串，缺失或无法解析时为 `None` |
| `available` | `bool` | 二进制文件是否在 PATH 上找到 |

## ToolCategory

`ToolCategory` 是一个将每个工具分组的 `StrEnum`。

| 成员 | 值 |
|---|---|
| `C_COMPILER` | `c-compiler` |
| `CXX_COMPILER` | `cxx-compiler` |
| `CUDA_COMPILER` | `cuda-compiler` |
| `BUILD_SYSTEM` | `build-system` |

`Toolchain.by_category` 将可用工具重新归入这些分组。

```python
from mainboard import Machine, ToolCategory

toolchain = Machine().toolchain
cuda = toolchain.by_category.get(ToolCategory.CUDA_COMPILER, ())
print([tool.name for tool in cuda])
```

## 如何探测

探测是数据驱动的。`ToolProbe` 是查找一个工具的不可变配方，而模块级的 `TOOL_PROBES` 元组就是 `Toolchain.probe()` 运行的注册表。

| 字段 | 类型 | 含义 |
|---|---|---|
| `name` | `str` | 在 `DetectedTool` 上报告的显示名称 |
| `category` | `ToolCategory` | 工具所属的工具链分组 |
| `binaries` | `tuple[str, ...]` | 候选可执行文件名，按顺序尝试直到有一个在 PATH 上 |
| `version_args` | `tuple[str, ...]` | 让二进制文件打印版本的参数，默认为 `("--version",)` |
| `pattern` | `re.Pattern[str]` | 正则表达式，其第一个分组从命令输出中捕获版本 |

对于每次探测，PATH 上找到的第一个二进制文件胜出。捕获其版本输出，pattern 的第一个分组成为 `version`。默认注册表覆盖 gcc、clang、g++、clang++、nvcc、cmake、ninja、make 和 meson。

## 扩展注册表

添加一个工具只需一行。将一个 `ToolProbe` 追加到 `TOOL_PROBES`，下一次探测就会发现它，且无需改动任何探测逻辑。

```python
from mainboard.models.toolchain import TOOL_PROBES, ToolProbe
from mainboard import ToolCategory

bazel = ToolProbe("bazel", ToolCategory.BUILD_SYSTEM, ("bazel",))
probes = (*TOOL_PROBES, bazel)

from mainboard import Toolchain

toolchain = Toolchain.probe(probes)
```

版本命令不标准的工具可设置 `version_args` 和 `pattern`。

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

一个全新的工具家族只需一个 `ToolCategory` 成员加上它的探测项，因此模型通过添加代码而非修改探测循环来增长。
