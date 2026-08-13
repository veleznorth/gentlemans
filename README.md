# Proyecto Integrador – Organización y Arquitectura de Computadores

## Estudiantes

- Nombre: Cristóbal Machado Sánchez
- Nombre: Mathías Vélez Londoño
- Nombre: Sebastián Sánchez Gómez

## Descripción

Este repositorio contiene la solución al Proyecto Integrador del primer corte
del curso de Organización y Arquitectura de Computadores.

El proyecto se basa en los Proyectos 1, 2 y 3 de la plataforma Nand2Tetris e
incluye una extensión académica denominada **ALUExtendida**, desarrollada
específicamente para este curso.

La construcción es jerárquica: compuertas lógicas básicas, bloques aritméticos,
ALU, componentes secuenciales, registros, memorias RAM y contador de programa.

---

# Contenido

## Proyecto 1

Implementación de las compuertas lógicas básicas y estructuras
combinacionales derivadas.

### Componentes

- Not
- And
- Or
- Xor
- Mux
- DMux
- Not16
- And16
- Or16
- Mux16
- Or8Way
- Mux4Way16
- Mux8Way16
- DMux4Way
- DMux8Way

---

## Proyecto 2

Implementación de circuitos aritméticos y de la ALU.

### Componentes

- HalfAdder
- FullAdder
- Add16
- Inc16
- ALU

---

## Proyecto 3

Implementación de componentes secuenciales y memoria.

### Componentes

- Bit
- Register
- RAM8
- RAM64
- RAM512
- RAM4K
- RAM16K
- PC

---

## Extensión: ALUExtendida

La ALUExtendida conserva la interfaz y el comportamiento de la ALU original de
Nand2Tetris y agrega cinco operaciones nuevas, habilitadas mediante la entrada
adicional `a`.

### Interfaz

- Entradas: `x[16]`, `y[16]`, `a`, `zx`, `nx`, `zy`, `ny`, `f`, `no`
- Salidas: `out[16]`, `zr`, `ng`

### Operaciones soportadas

| Operación | Código `zx nx zy ny f no` |
|---|---|
| XOR | `010110` |
| NAND | `000001` |
| NOR | `110100` |
| EQ | `101000` |
| ABS | `100010` |

Con `a = 0`, o con un código que no corresponda a una operación extendida, la
salida proviene de la ALU original. Los flags `zr` y `ng` se calculan siempre
sobre la salida final seleccionada.

La documentación detallada está en
[`alu_extendida/DOCUMENTACION/ALUExtendida.md`](alu_extendida/DOCUMENTACION/ALUExtendida.md).

---

# Estructura del Repositorio

```text
proyecto01/
├── HDL/
└── TESTS/

proyecto02/
├── HDL/
└── TESTS/

proyecto03/
├── HDL/
└── TESTS/

alu_extendida/
├── HDL/
├── TESTS/
└── DOCUMENTACION/

README.md
```

---

# Evidencias

Todos los componentes se verificaron en el simulador de hardware de Nand2Tetris
con las pruebas oficiales de la plataforma. La evidencia que se entrega en este
repositorio son las capturas de pantalla de esas ejecuciones satisfactorias.

Cada carpeta `TESTS/` contiene las capturas nombradas según el chip
correspondiente. En todas aparece el mensaje del simulador
`Simulation successful: The output file is identical to the compare file`.

Para la ALUExtendida, además de la captura de la verificación completa
(`ALUExtendida.png`), se incluye una captura por operación:

| Captura | Qué demuestra |
|---|---|
| `XOR.png` | `0000000000000101` XOR `0000000000000011` = `0000000000000110` |
| `NAND.png` | NAND de los mismos operandos = `1111111111111110` |
| `NOR.png` | NOR de los mismos operandos = `1111111111111000` |
| `EQ-iguales.png` | `x = y = 7` produce `1` |
| `EQ-diferentes.png` | `x = 7`, `y = 6` produce `0` con `zr = 1` |
| `ABS-positivo.png` | `ABS(+9) = 9` |
| `ABS-negativo.png` | `ABS(−9) = 9`, ignorando `y` |
| `ABS-cero.png` | `ABS(0) = 0` con `zr = 1` |
| `compatibilidad-a0.png` | Con `a = 0` la salida sigue siendo la de la ALU original (`17 + 3 = 20`) |

El detalle de diseño de la extensión está en
[`alu_extendida/DOCUMENTACION/ALUExtendida.md`](alu_extendida/DOCUMENTACION/ALUExtendida.md).
