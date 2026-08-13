# ALUExtendida

## Objetivo

La `ALUExtendida` conserva el comportamiento de la ALU original de Nand2Tetris
y agrega las cinco operaciones exigidas por el proyecto: XOR, NAND, NOR, EQ y ABS.

## Interfaz

Entradas:

- `x[16]`, `y[16]`
- `a`
- `zx`, `nx`, `zy`, `ny`, `f`, `no`

Salidas:

- `out[16]`
- `zr`
- `ng`

## Compatibilidad

Se usa `a` como selector del modo extendido:

- `a = 0`: la salida proviene de la ALU original, sin alterar su comportamiento.
- `a = 1`: los seis bits `zx nx zy ny f no` se comparan con los códigos
  extendidos. Si el código no corresponde a una operación nueva, se conserva la
  salida de la ALU original.

Esta organización evita que las nuevas operaciones rompan las operaciones
preexistentes.

## Operaciones extendidas

| Operación | Código `zx nx zy ny f no` | Resultado |
|---|---|---|
| XOR | `010110` | `x XOR y` |
| NAND | `000001` | `!(x AND y)` |
| NOR | `110100` | `!(x OR y)` |
| EQ | `101000` | `1` si `x == y`, en otro caso `0` |
| ABS | `100010` | `|x|` en complemento a dos; `y` se ignora |

## Diseño

### XOR

Se implementa mediante:

`(x OR y) AND NOT(x AND y)`

### NAND

Primero se calcula `x AND y` y después se invierte.

### NOR

Primero se calcula `x OR y` y después se invierte.

### EQ

Se calcula XOR entre `x` e `y`. Si ningún bit de ese XOR es `1`, entonces los
operandos son iguales y la salida es `0000000000000001`.

### ABS

Se inspecciona el bit de signo `x[15]`.

- Si es `0`, `x` ya es no negativo.
- Si es `1`, se calcula el complemento a dos: `!x + 1`.

En 16 bits, `-32768` permanece `-32768`, ya que su valor absoluto matemático
`32768` no puede representarse como entero positivo con signo de 16 bits.

## Flags

Los flags se calculan sobre `finalOut`, es decir, después de decidir si la salida
proviene de la ALU original o de una operación extendida.

- `zr = 1` únicamente cuando los 16 bits de `finalOut` son cero.
- `ng = finalOut[15]`.

## Dependencias

`HDL/` incluye una copia de `ALU.hdl` (la misma del Proyecto 2) para que la
extensión se construya sobre la ALU implementada en este trabajo y no sobre el
chip integrado del simulador. El resto de las dependencias (`Or16`, `And16`,
`Not16`, `Mux16`, `Or8Way`, `Add16`, `And`, `Or`, `Not`) se resuelven con los
chips del simulador.

## Nota de implementación

El simulador de Nand2Tetris no permite referenciar un sub-bus de un nodo
interno. Por eso las mitades usadas para calcular `zr` se extraen directamente
en la salida del chip que las produce
(`out[0..7]=...`, `out[8..15]=...`, `out[15]=ng`).

## Verificación

La ALUExtendida se verificó en el simulador de hardware de Nand2Tetris sobre
49 casos: las cinco operaciones nuevas, un código de control no reconocido con
`a = 1` que debe recaer en la ALU original, y los 36 casos de la tabla oficial
de la ALU ejecutados con `a = 0` para comprobar que el comportamiento original
se conserva sin alteraciones.

Las evidencias entregadas en este repositorio son las capturas de pantalla de
esas ejecuciones, ubicadas en `TESTS/`.

## Evidencias

| Captura | Qué demuestra |
|---|---|
| `ALUExtendida.png` | Ejecución completa de la verificación, con el mensaje `Simulation successful: The output file is identical to the compare file` y las 49 filas comparadas |
| `XOR.png` | `x = 0000000000000101`, `y = 0000000000000011`, `a = 1`, código `010110` → `out = 0000000000000110` |
| `NAND.png` | Mismos operandos, código `000001` → `out = 1111111111111110`, `ng = 1` |
| `NOR.png` | Mismos operandos, código `110100` → `out = 1111111111111000`, `ng = 1` |
| `EQ-iguales.png` | `x = y = 0000000000000111`, código `101000` → `out = 0000000000000001` |
| `EQ-diferentes.png` | `x = 0000000000000111`, `y = 0000000000000110` → `out = 0000000000000000`, `zr = 1` |
| `ABS-positivo.png` | `x = 0000000000001001` (+9), código `100010` → `out = 0000000000001001` |
| `ABS-negativo.png` | `x = 1111111111110111` (−9) → `out = 0000000000001001`, con `y` ignorado |
| `ABS-cero.png` | `x = 0000000000000000` → `out = 0000000000000000`, `zr = 1` |
| `compatibilidad-a0.png` | `x = 17`, `y = 3`, `a = 0`, código `000010` → `out = 0000000000010100`, es decir la suma de la ALU original sin alterar |
