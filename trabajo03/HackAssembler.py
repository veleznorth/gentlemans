"""Avance del trabajo 3: ensamblador Hack.

Uso: python3 HackAssembler.py Prog.asm [-o Prog.hack] [--force]
Traduce instrucciones A/C, etiquetas y variables mediante dos pasadas.
El desensamblador y la validación completa del proyecto están pendientes.
"""



COMP = {
    '0': '0101010', '1': '0111111', '-1': '0111010',
    'D': '0001100', 'A': '0110000', 'M': '1110000',
    '!D': '0001101', '!A': '0110001', '!M': '1110001',
    '-D': '0001111', '-A': '0110011', '-M': '1110011',
    'D+1': '0011111', 'A+1': '0110111', 'M+1': '1110111',
    'D-1': '0001110', 'A-1': '0110010', 'M-1': '1110010',
    'D+A': '0000010', 'D+M': '1000010',
    'D-A': '0010011', 'D-M': '1010011',
    'A-D': '0000111', 'M-D': '1000111',
    'D&A': '0000000', 'D&M': '1000000',
    'D|A': '0010101', 'D|M': '1010101',
}
DEST = {'': '000', 'M': '001', 'D': '010', 'MD': '011',
        'A': '100', 'AM': '101', 'AD': '110', 'AMD': '111'}
JUMP = {'': '000', 'JGT': '001', 'JEQ': '010', 'JGE': '011',
        'JLT': '100', 'JNE': '101', 'JLE': '110', 'JMP': '111'}


def encode_comp(mnemonic: str) -> str:
    try:
        return COMP[mnemonic]
    except KeyError:
        raise ValueError(f'comp inválido: {mnemonic!r}') from None


def encode_dest(mnemonic: str) -> str:
    # Las diapositivas usan DM y ADM; el orden de A, D, M no cambia los bits.
    if any(c not in 'ADM' for c in mnemonic) or len(set(mnemonic)) != len(mnemonic):
        raise ValueError(f'dest inválido: {mnemonic!r}')
    return ''.join('1' if c in mnemonic else '0' for c in 'ADM')


def encode_jump(mnemonic: str) -> str:
    try:
        return JUMP[mnemonic]
    except KeyError:
        raise ValueError(f'jump inválido: {mnemonic!r}') from None


import re
from dataclasses import dataclass

SYMBOL = re.compile(r'[A-Za-z_.$:][A-Za-z0-9_.$:]*\Z')


@dataclass(frozen=True)
class Instruction:
    line: int
    text: str

    def instruction_type(self) -> str:
        if self.text.startswith('@'):
            return 'A_INSTRUCTION'
        if self.text.startswith('('):
            return 'L_INSTRUCTION'
        return 'C_INSTRUCTION'

    def symbol(self) -> str:
        if self.instruction_type() == 'A_INSTRUCTION':
            value = self.text[1:]
            if re.fullmatch(r'[0-9]+', value):
                return value
        else:
            if not self.text.endswith(')'):
                raise ValueError('etiqueta sin paréntesis de cierre')
            value = self.text[1:-1]
        if not SYMBOL.fullmatch(value):
            raise ValueError(f'símbolo inválido: {value!r}')
        return value

    def fields(self) -> tuple[str, str, str]:
        if self.text.count('=') > 1 or self.text.count(';') > 1:
            raise ValueError('instrucción C mal formada')
        expression, separator, jump = self.text.partition(';')
        dest, equals, comp = expression.partition('=')
        if not equals:
            comp, dest = dest, ''
        if not comp or (equals and not dest) or (separator and not jump):
            raise ValueError('campo vacío en instrucción C')
        return dest, comp, jump


class Parser:
    def __init__(self, source: str):
        self.instructions = []
        for number, raw in enumerate(source.splitlines(), 1):
            text = ''.join(raw.split('//', 1)[0].split())
            if text:
                self.instructions.append(Instruction(number, text))

    def __iter__(self):
        return iter(self.instructions)


class SymbolTable:
    def __init__(self):
        self.entries = {f'R{i}': i for i in range(16)}
        self.entries.update(SP=0, LCL=1, ARG=2, THIS=3, THAT=4,
                            SCREEN=16384, KBD=24576)
        self.next_variable = 16

    def add_entry(self, symbol: str, address: int):
        if self.contains(symbol):
            raise ValueError(f'símbolo ya definido: {symbol}')
        self.entries[symbol] = address

    def contains(self, symbol: str) -> bool:
        return symbol in self.entries

    def get_address(self, symbol: str) -> int:
        return self.entries[symbol]

    def resolve(self, symbol: str) -> int:
        if not self.contains(symbol):
            if self.next_variable >= 16384:
                raise ValueError('sin espacio RAM para nuevas variables')
            self.add_entry(symbol, self.next_variable)
            self.next_variable += 1
        return self.get_address(symbol)


import argparse
from pathlib import Path


def translate_cli(translator, input_suffix: str, output_suffix: str, description: str):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('input', type=Path, help=f'archivo {input_suffix}')
    parser.add_argument('-o', '--output', type=Path, help='ruta del archivo de salida')
    parser.add_argument('--force', action='store_true', help='permitir reemplazar una salida existente')
    args = parser.parse_args()
    output = args.output or args.input.with_suffix(output_suffix)
    try:
        if args.input.suffix.lower() != input_suffix:
            raise ValueError(f'la entrada debe tener extensión {input_suffix}')
        if args.input.resolve() == output.resolve():
            raise ValueError('la salida debe ser distinta de la entrada')
        result = translator(args.input.read_text(encoding='utf-8-sig'))
        with output.open('w' if args.force else 'x', encoding='utf-8', newline='\n') as file:
            file.write(result)
    except FileExistsError:
        parser.exit(1, f'Error: {output} ya existe; usa -o o --force.\n')
    except (OSError, ValueError) as error:
        parser.exit(1, f'Error: {error}\n')
    print(f'{args.input} -> {output} ({len(result.splitlines())} instrucciones)')


def assemble(source: str) -> str:
    parser = Parser(source)
    symbols = SymbolTable()
    address = 0
    # Primera pasada: las etiquetas apuntan a la siguiente instrucción ROM.
    for instruction in parser:
        try:
            if instruction.instruction_type() == 'L_INSTRUCTION':
                if address > 32767:
                    raise ValueError('dirección ROM fuera de rango')
                symbols.add_entry(instruction.symbol(), address)
            else:
                if address >= 32768:
                    raise ValueError('programa demasiado grande para ROM32K')
                address += 1
        except ValueError as error:
            raise ValueError(f'línea {instruction.line}: {error}') from None

    result = []
    # Segunda pasada: asignar variables y emitir instrucciones de 16 bits.
    for instruction in parser:
        try:
            kind = instruction.instruction_type()
            if kind == 'L_INSTRUCTION':
                continue
            if kind == 'A_INSTRUCTION':
                symbol = instruction.symbol()
                value = int(symbol) if symbol.isdecimal() else symbols.resolve(symbol)
                if not 0 <= value <= 32767:
                    raise ValueError('el valor de @ debe estar entre 0 y 32767')
                result.append(f'{value:016b}')
            else:
                dest, comp, jump = instruction.fields()
                result.append('111' + encode_comp(comp) + encode_dest(dest) + encode_jump(jump))
        except ValueError as error:
            raise ValueError(f'línea {instruction.line}: {error}') from None
    return ''.join(line + '\n' for line in result)


if __name__ == '__main__':
    translate_cli(assemble, '.asm', '.hack', 'Ensamblador Hack')
