# Toolchain

`Machine.toolchain`, también incluido en la instantánea, informa los compiladores de C, C++ y CUDA y los sistemas de compilación encontrados en el PATH del host, para que una herramienta conozca la capacidad real de compilación de la máquina sin tener que invocarlos por su cuenta.

```python
from mainboard import Machine

toolchain = Machine().toolchain
for tool in toolchain.tools:
    print(tool.name, tool.version, tool.path)
```

Solo se conservan las herramientas que están realmente en el PATH, por lo que la lista refleja lo que el host puede ejecutar de verdad. Cada herramienta mantiene el orden en que fue registrada, agrupada por categoría.

## En la instantánea

El campo `toolchain` de `Machine().model_dump_json()` lista cada herramienta disponible:

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

`version` es `null` cuando la herramienta está presente pero su salida de versión no se puede interpretar.

## DetectedTool

Cada entrada en `tools` es un `DetectedTool`, el resultado estructurado de un sondeo.

| campo | tipo | significado |
|---|---|---|
| `name` | `str` | nombre visible de la herramienta, p. ej. `gcc` o `cmake` |
| `category` | `ToolCategory` | grupo de toolchain al que pertenece la herramienta |
| `path` | `str \| None` | ruta absoluta al binario resuelto, `None` cuando no está en el PATH |
| `version` | `str \| None` | cadena de versión interpretada, `None` cuando está ausente o no se puede leer |
| `available` | `bool` | si el binario se encontró en el PATH |

## ToolCategory

`ToolCategory` es un `StrEnum` que clasifica cada herramienta en grupos.

| miembro | valor |
|---|---|
| `C_COMPILER` | `c-compiler` |
| `CXX_COMPILER` | `cxx-compiler` |
| `CUDA_COMPILER` | `cuda-compiler` |
| `BUILD_SYSTEM` | `build-system` |

`Toolchain.by_category` reagrupa las herramientas disponibles en estos grupos.

```python
from mainboard import Machine, ToolCategory

toolchain = Machine().toolchain
cuda = toolchain.by_category.get(ToolCategory.CUDA_COMPILER, ())
print([tool.name for tool in cuda])
```

## Cómo se sondea

El descubrimiento está orientado a datos. Un `ToolProbe` es una receta inmutable para encontrar una herramienta, y la tupla `TOOL_PROBES` a nivel de módulo es el registro que ejecuta `Toolchain.probe()`.

| campo | tipo | significado |
|---|---|---|
| `name` | `str` | nombre visible que se reporta en el `DetectedTool` |
| `category` | `ToolCategory` | grupo de toolchain al que pertenece la herramienta |
| `binaries` | `tuple[str, ...]` | nombres de ejecutables candidatos, probados en orden hasta que uno esté en el PATH |
| `version_args` | `tuple[str, ...]` | argumentos que hacen que el binario imprima su versión, por defecto `("--version",)` |
| `pattern` | `re.Pattern[str]` | regex cuyo primer grupo captura la versión de la salida del comando |

Para cada sondeo, gana el primer binario encontrado en el PATH. Su salida de versión se captura y el primer grupo del pattern se convierte en `version`. El registro por defecto cubre gcc, clang, g++, clang++, nvcc, cmake, ninja, make y meson.

## Extender el registro

Agregar una herramienta es una línea. Añade un `ToolProbe` a `TOOL_PROBES` y se descubre en el siguiente sondeo, sin ningún cambio en la lógica de descubrimiento.

```python
from mainboard.models.toolchain import TOOL_PROBES, ToolProbe
from mainboard import ToolCategory

bazel = ToolProbe("bazel", ToolCategory.BUILD_SYSTEM, ("bazel",))
probes = (*TOOL_PROBES, bazel)

from mainboard import Toolchain

toolchain = Toolchain.probe(probes)
```

Una herramienta con un comando de versión no estándar define `version_args` y `pattern`.

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

Una familia de herramientas completamente nueva es un miembro de `ToolCategory` más sus sondeos, así que el modelo crece agregando código en lugar de editar el bucle de sondeo.
