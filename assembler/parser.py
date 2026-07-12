from .opcodes import INSTRUCTIONS, instr_size
from .lexer import TokenLine, tokenize, DATA_DIRECTIVES
from .expr import evaluate, ExprError, parse_number as _parse_number


class AssemblyError(Exception):
    def __init__(self, msg: str, lineno: int | None = None):
        self.lineno = lineno
        if lineno is not None:
            super().__init__(f"Line {lineno}: {msg}")
        else:
            super().__init__(msg)


def is_local_label(name: str) -> bool:
    return name.startswith(".")


def _make_lookup(symbols: dict[str, int], scope: str | None):
    def lookup(name: str) -> int | None:
        if is_local_label(name):
            if scope is None:
                return None
            full = scope + name
            return symbols.get(full)
        return symbols.get(name)

    return lookup


def resolve_operand(
    operand: str, symbols: dict[str, int], scope: str | None, lineno: int
) -> int:
    lookup = _make_lookup(symbols, scope)
    try:
        return evaluate(operand, lookup)
    except ExprError as e:
        raise AssemblyError(str(e), lineno)


def parse_operand_value(s: str) -> int | None:
    return _parse_number(s)


JUMP_INSTRUCTIONS = {"JMP", "JIF", "JIN", "CALL"}


def is_jump_to_label(tok: TokenLine) -> bool:
    if tok.mnemonic not in JUMP_INSTRUCTIONS:
        return False
    if parse_operand_value(tok.operands[0]) is not None:
        return False
    return True


def parse_string_operand(s: str) -> list[int] | None:
    if len(s) >= 2 and s[0] in ('"', "'") and s[-1] == s[0]:
        inner = s[1:-1]
        result = []
        i = 0
        while i < len(inner):
            if inner[i] == "\\" and i + 1 < len(inner):
                nxt = inner[i + 1]
                if nxt == "n":
                    result.append(0x0A)
                elif nxt == "t":
                    result.append(0x09)
                elif nxt == "0":
                    result.append(0x00)
                elif nxt == "r":
                    result.append(0x0D)
                elif nxt == "\\":
                    result.append(0x5C)
                elif nxt == s[0]:
                    result.append(ord(s[0]))
                else:
                    result.append(ord("\\"))
                    result.append(ord(nxt))
                i += 2
            else:
                result.append(ord(inner[i]))
                i += 1
        return result
    return None


def data_size(mnemonic: str, operands: list[str]) -> int:
    upper = mnemonic.upper()
    if upper == ".DW":
        return len(operands) * 2
    count = 0
    for op in operands:
        string = parse_string_operand(op)
        if string is not None:
            count += len(string)
        else:
            count += 1
    return count


def assemble_data(
    tok: TokenLine, symbols: dict[str, int], scope: str | None
) -> list[int]:
    upper = tok.mnemonic.upper()
    code = []
    lookup = _make_lookup(symbols, scope)
    for op in tok.operands:
        if upper == ".DW":
            try:
                val = evaluate(op, lookup)
            except ExprError:
                raise AssemblyError(f"Invalid value '{op}' for .dw", tok.lineno)
            if val < 0 or val > 0xFFFF:
                raise AssemblyError(
                    f"Value {val} out of range for 16-bit word", tok.lineno
                )
            code.append((val >> 8) & 0xFF)
            code.append(val & 0xFF)
        else:
            string = parse_string_operand(op)
            if string is not None:
                code.extend(string)
            else:
                try:
                    val = evaluate(op, lookup)
                except ExprError:
                    raise AssemblyError(f"Invalid value '{op}' for .db", tok.lineno)
                if val < 0 or val > 0xFF:
                    raise AssemblyError(
                        f"Value {val} out of range for 8-bit byte", tok.lineno
                    )
                code.append(val & 0xFF)
    return code


def assemble_lines(
    tokens: list[TokenLine], defines: dict[str, str] | None = None
) -> list[tuple[int, list[int]]]:
    if defines is None:
        defines = {}

    jmpaddr_val: int | None = None
    if "JMPADDR" in defines:
        jmpaddr_val = parse_operand_value(defines["JMPADDR"])

    symbols: dict[str, int] = {}
    scope: str | None = None
    instructions: list[tuple[TokenLine, int, str | None]] = []

    addr = 0
    for tok in tokens:
        if tok.label:
            if is_local_label(tok.label):
                if scope is None:
                    raise AssemblyError(
                        f"Local label '{tok.label}' defined before any main label",
                        tok.lineno,
                    )
                full = scope + tok.label
                if full in symbols:
                    raise AssemblyError(f"Duplicate symbol '{full}'", tok.lineno)
                symbols[full] = addr
            else:
                scope = tok.label
                if tok.label in symbols:
                    raise AssemblyError(f"Duplicate symbol '{tok.label}'", tok.lineno)
                symbols[tok.label] = addr

        if tok.mnemonic:
            mn_upper = tok.mnemonic.upper()
            if mn_upper in DATA_DIRECTIVES:
                instructions.append((tok, addr, scope))
                addr += data_size(tok.mnemonic, tok.operands)
            elif tok.mnemonic in INSTRUCTIONS:
                info = INSTRUCTIONS[tok.mnemonic]
                expected = len(info["op_sizes"])
                if len(tok.operands) != expected:
                    raise AssemblyError(
                        f"{tok.mnemonic} expects {expected} operands, got {len(tok.operands)}",
                        tok.lineno,
                    )
                instructions.append((tok, addr, scope))
                if is_jump_to_label(tok) and jmpaddr_val is not None:
                    addr += instr_size("LDI") + instr_size(tok.mnemonic)
                elif is_jump_to_label(tok) and jmpaddr_val is None:
                    raise AssemblyError(
                        f"JMP/JIF/JIN/CALL with label operand requires #define JMPADDR <qm_slot>",
                        tok.lineno,
                    )
                else:
                    addr += instr_size(tok.mnemonic)
            else:
                raise AssemblyError(f"Unknown instruction '{tok.mnemonic}'", tok.lineno)

    output: list[tuple[int, list[int]]] = []
    for tok, instr_addr, instr_scope in instructions:
        mn_upper = tok.mnemonic.upper() if tok.mnemonic else ""
        if mn_upper in DATA_DIRECTIVES:
            code = assemble_data(tok, symbols, instr_scope)
            output.append((instr_addr, code))
        elif is_jump_to_label(tok) and jmpaddr_val is not None:
            label_val = resolve_operand(
                tok.operands[0], symbols, instr_scope, tok.lineno
            )
            ldi_info = INSTRUCTIONS["LDI"]
            jmp_info = INSTRUCTIONS[tok.mnemonic]

            ldi_code = [ldi_info["opcode"]]
            ldi_code.append(jmpaddr_val & 0xFF)
            for b in range(1, -1, -1):
                ldi_code.append((label_val >> (b * 8)) & 0xFF)
            output.append((instr_addr, ldi_code))

            jmp_code = [jmp_info["opcode"]]
            jmp_code.append(jmpaddr_val & 0xFF)
            if len(tok.operands) > 1:
                for op, op_size in zip(tok.operands[1:], jmp_info["op_sizes"][1:]):
                    val = resolve_operand(op, symbols, instr_scope, tok.lineno)
                    for b in range(op_size - 1, -1, -1):
                        jmp_code.append((val >> (b * 8)) & 0xFF)
            output.append((instr_addr + instr_size("LDI"), jmp_code))
        else:
            info = INSTRUCTIONS[tok.mnemonic]
            code = [info["opcode"]]
            for op, op_size in zip(tok.operands, info["op_sizes"]):
                val = resolve_operand(op, symbols, instr_scope, tok.lineno)
                max_val = (1 << (op_size * 8)) - 1
                val = val & max_val
                for b in range(op_size - 1, -1, -1):
                    code.append((val >> (b * 8)) & 0xFF)
            output.append((instr_addr, code))

    return output
