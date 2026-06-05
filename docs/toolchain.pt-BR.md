# Toolchain

`Machine.toolchain`, também presente no snapshot, informa os compiladores C, C++ e CUDA e os build systems encontrados no PATH do host, para que uma ferramenta conheça a real capacidade de build da máquina sem precisar invocá-los por conta própria.

```python
from mainboard import Machine

toolchain = Machine().toolchain
for tool in toolchain.tools:
    print(tool.name, tool.version, tool.path)
```

Só são mantidas as ferramentas que estão de fato no PATH, então a lista reflete o que o host pode realmente executar. Cada ferramenta mantém a ordem em que foi registrada, agrupada por categoria.

## No snapshot

O campo `toolchain` de `Machine().model_dump_json()` lista cada ferramenta disponível:

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

`version` é `null` quando a ferramenta está presente mas a saída da versão não pode ser interpretada.

## DetectedTool

Cada entrada em `tools` é um `DetectedTool`, o resultado estruturado de uma sondagem.

| campo | tipo | significado |
|---|---|---|
| `name` | `str` | nome de exibição da ferramenta, ex. `gcc` ou `cmake` |
| `category` | `ToolCategory` | grupo de toolchain ao qual a ferramenta pertence |
| `path` | `str \| None` | caminho absoluto do binário resolvido, `None` quando não está no PATH |
| `version` | `str \| None` | string de versão interpretada, `None` quando ausente ou ilegível |
| `available` | `bool` | se o binário foi encontrado no PATH |

## ToolCategory

`ToolCategory` é um `StrEnum` que separa cada ferramenta em grupos.

| membro | valor |
|---|---|
| `C_COMPILER` | `c-compiler` |
| `CXX_COMPILER` | `cxx-compiler` |
| `CUDA_COMPILER` | `cuda-compiler` |
| `BUILD_SYSTEM` | `build-system` |

`Toolchain.by_category` reagrupa as ferramentas disponíveis nesses grupos.

```python
from mainboard import Machine, ToolCategory

toolchain = Machine().toolchain
cuda = toolchain.by_category.get(ToolCategory.CUDA_COMPILER, ())
print([tool.name for tool in cuda])
```

## Como é sondado

A descoberta é orientada a dados. Um `ToolProbe` é uma receita imutável para encontrar uma ferramenta, e a tupla `TOOL_PROBES` no nível do módulo é o registro que `Toolchain.probe()` executa.

| campo | tipo | significado |
|---|---|---|
| `name` | `str` | nome de exibição reportado no `DetectedTool` |
| `category` | `ToolCategory` | grupo de toolchain ao qual a ferramenta pertence |
| `binaries` | `tuple[str, ...]` | nomes de executáveis candidatos, testados em ordem até um estar no PATH |
| `version_args` | `tuple[str, ...]` | argumentos que fazem o binário imprimir sua versão, padrão `("--version",)` |
| `pattern` | `re.Pattern[str]` | regex cujo primeiro grupo captura a versão na saída do comando |

Para cada sondagem, vence o primeiro binário encontrado no PATH. A saída da versão é capturada e o primeiro grupo do pattern vira `version`. O registro padrão cobre gcc, clang, g++, clang++, nvcc, cmake, ninja, make e meson.

## Estendendo o registro

Adicionar uma ferramenta é uma linha. Acrescente um `ToolProbe` a `TOOL_PROBES` e ele é descoberto na próxima sondagem, sem nenhuma mudança na lógica de descoberta.

```python
from mainboard.models.toolchain import TOOL_PROBES, ToolProbe
from mainboard import ToolCategory

bazel = ToolProbe("bazel", ToolCategory.BUILD_SYSTEM, ("bazel",))
probes = (*TOOL_PROBES, bazel)

from mainboard import Toolchain

toolchain = Toolchain.probe(probes)
```

Uma ferramenta com um comando de versão fora do padrão define `version_args` e `pattern`.

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

Uma família inteiramente nova de ferramentas é um membro de `ToolCategory` mais suas sondagens, então o modelo cresce adicionando código em vez de editar o loop de sondagem.
