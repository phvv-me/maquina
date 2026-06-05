# Toolchain

`Machine.toolchain` は、スナップショットにも含まれており、ホストの PATH 上にある C、C++、CUDA コンパイラとビルドシステムを報告します。これにより、ツールは自分でコマンドを実行することなく、マシンの実際のビルド能力を知ることができます。

```python
from mainboard import Machine

toolchain = Machine().toolchain
for tool in toolchain.tools:
    print(tool.name, tool.version, tool.path)
```

実際に PATH 上にあるツールだけが保持されるため、リストはホストが本当に実行できるものを反映します。各ツールは登録順を保ち、カテゴリごとにグループ化されます。

## スナップショット内

`Machine().model_dump_json()` の `toolchain` フィールドは、利用可能なすべてのツールを列挙します。

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

ツールが存在していてもバージョン出力を解析できない場合、`version` は `null` になります。

## DetectedTool

`tools` の各エントリは、1 回の探査の構造化された結果である `DetectedTool` です。

| フィールド | 型 | 意味 |
|---|---|---|
| `name` | `str` | ツールの表示名、例 `gcc` や `cmake` |
| `category` | `ToolCategory` | ツールが属するツールチェーングループ |
| `path` | `str \| None` | 解決されたバイナリの絶対パス、PATH 上にない場合は `None` |
| `version` | `str \| None` | 解析されたバージョン文字列、存在しないか解析不能な場合は `None` |
| `available` | `bool` | バイナリが PATH 上で見つかったかどうか |

## ToolCategory

`ToolCategory` は各ツールをグループに分類する `StrEnum` です。

| メンバー | 値 |
|---|---|
| `C_COMPILER` | `c-compiler` |
| `CXX_COMPILER` | `cxx-compiler` |
| `CUDA_COMPILER` | `cuda-compiler` |
| `BUILD_SYSTEM` | `build-system` |

`Toolchain.by_category` は、利用可能なツールをこれらのグループに再編成します。

```python
from mainboard import Machine, ToolCategory

toolchain = Machine().toolchain
cuda = toolchain.by_category.get(ToolCategory.CUDA_COMPILER, ())
print([tool.name for tool in cuda])
```

## 探査の仕組み

検出はデータ駆動です。`ToolProbe` は 1 つのツールを見つけるための不変のレシピであり、モジュールレベルの `TOOL_PROBES` タプルが `Toolchain.probe()` の実行するレジストリです。

| フィールド | 型 | 意味 |
|---|---|---|
| `name` | `str` | `DetectedTool` に報告される表示名 |
| `category` | `ToolCategory` | ツールが属するツールチェーングループ |
| `binaries` | `tuple[str, ...]` | 候補となる実行ファイル名。PATH 上に見つかるまで順に試行される |
| `version_args` | `tuple[str, ...]` | バイナリにバージョンを出力させる引数、デフォルトは `("--version",)` |
| `pattern` | `re.Pattern[str]` | コマンド出力からバージョンを最初のグループで捕捉する正規表現 |

各探査では、PATH 上で最初に見つかったバイナリが採用されます。そのバージョン出力が取得され、pattern の最初のグループが `version` になります。デフォルトのレジストリは gcc、clang、g++、clang++、nvcc、cmake、ninja、make、meson をカバーします。

## レジストリの拡張

ツールの追加は 1 行です。`TOOL_PROBES` に `ToolProbe` を追加するだけで、検出ロジックを変更することなく次の探査で検出されます。

```python
from mainboard.models.toolchain import TOOL_PROBES, ToolProbe
from mainboard import ToolCategory

bazel = ToolProbe("bazel", ToolCategory.BUILD_SYSTEM, ("bazel",))
probes = (*TOOL_PROBES, bazel)

from mainboard import Toolchain

toolchain = Toolchain.probe(probes)
```

標準的でないバージョンコマンドを持つツールは、`version_args` と `pattern` を設定します。

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

まったく新しいツールのファミリーは、1 つの `ToolCategory` メンバーとその探査だけで構成されます。したがってモデルは、探査ループを編集するのではなく、コードを追加することで成長します。
