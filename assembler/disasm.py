from __future__ import annotations

OPCODE_TABLE: dict[int, tuple[str, list[int]]] = {
    0x00: ("NOP", []),
    0x01: ("LDI", [1, 2]),
    0x02: ("LD", [1, 2]),
    0x03: ("LDP", [1, 1]),
    0x04: ("ST", [1, 2]),
    0x05: ("STP", [1, 1]),
    0x06: ("MOV", [1, 1]),
    0x08: ("ADD", [1, 1, 1]),
    0x09: ("SUB", [1, 1, 1]),
    0x0A: ("MUL", [1, 1, 1]),
    0x0B: ("DIV", [1, 1, 1]),
    0x0C: ("MOD", [1, 1, 1]),
    0x0D: ("AND", [1, 1, 1]),
    0x0E: ("OR", [1, 1, 1]),
    0x0F: ("XOR", [1, 1, 1]),
    0x10: ("NEG", [1, 1]),
    0x11: ("INV", [1, 1]),
    0x12: ("EQ", [1, 1, 1]),
    0x13: ("GT", [1, 1, 1]),
    0x14: ("LT", [1, 1, 1]),
    0x20: ("CPC", [1]),
    0x21: ("JMP", [1]),
    0x22: ("JIF", [1, 1]),
    0x23: ("JIN", [1, 1]),
    0x24: ("CALL", [1]),
    0x25: ("RET", []),
}

JUMP_OPCODES = {0x21, 0x22, 0x23, 0x24}


def parse_hex(hex_str: str) -> bytes:
    cleaned = hex_str.replace(" ", "").replace("\n", "").replace("\r", "")
    return bytes.fromhex(cleaned)


def try_decode_instr(data: bytes, offset: int) -> tuple[str, list[int], int] | None:
    if offset >= len(data):
        return None
    opcode = data[offset]
    if opcode not in OPCODE_TABLE:
        return None
    mnemonic, op_sizes = OPCODE_TABLE[opcode]
    total = 1 + sum(op_sizes)
    if offset + total > len(data):
        return None
    operands = []
    pos = offset + 1
    for size in op_sizes:
        if size == 1:
            operands.append(data[pos])
            pos += 1
        else:
            operands.append((data[pos] << 8) | data[pos + 1])
            pos += 2
    return mnemonic, operands, total


def format_operand(val: int, size: int) -> str:
    if size == 1:
        return f"0x{val:02X}"
    return f"0x{val:04X}"


def format_instr(
    addr: int, mnemonic: str, operands: list[int], op_sizes: list[int]
) -> str:
    parts = [f"0x{addr:04X}:", mnemonic]
    for val, size in zip(operands, op_sizes):
        parts.append(format_operand(val, size))
    return " ".join(parts)


def detect_string(data: bytes, offset: int) -> list[int] | None:
    if offset >= len(data):
        return None
    if data[offset] < 0x20 or data[offset] > 0x7E:
        return None
    end = offset
    while end < len(data) and 0x20 <= data[end] <= 0x7E:
        end += 1
    if end - offset < 3:
        return None
    run = list(range(offset, end))
    if end < len(data) and data[end] == 0x00:
        run.append(end)
    return run


def format_data_line(addr: int, indices: list[int], data: bytes) -> str:
    has_null = indices[-1] < len(data) and data[indices[-1]] == 0x00
    char_indices = indices[:-1] if has_null else indices
    if len(char_indices) >= 3 and all(0x20 <= data[i] <= 0x7E for i in char_indices):
        string_val = "".join(chr(data[i]) for i in char_indices)
        suffix = " 0x00" if has_null else ""
        return f'0x{addr:04X}: .db "{string_val}"{suffix}'
    parts = [f"0x{data[i]:02X}" for i in indices]
    return f"0x{addr:04X}: .db {' '.join(parts)}"


def disassemble(data: bytes) -> str:
    visited: set[int] = set()
    output_lines: list[str] = []
    entry_points: list[int] = [0]

    while entry_points:
        entry_points.sort()
        start = entry_points.pop(0)
        if start in visited or start >= len(data):
            continue

        i = start
        while i < len(data):
            if i in visited:
                break
            visited.add(i)

            result = try_decode_instr(data, i)
            if result is None:
                string_run = detect_string(data, i)
                if string_run is not None:
                    output_lines.append(format_data_line(i, string_run, data))
                    i = string_run[-1] + 1
                else:
                    output_lines.append(f"0x{i:04X}: .db 0x{data[i]:02X}")
                    i += 1
                continue

            mnemonic, operands, size = result
            op_sizes = OPCODE_TABLE[data[i]][1]
            output_lines.append(format_instr(i, mnemonic, operands, op_sizes))

            if data[i] in JUMP_OPCODES:
                target = operands[0]
                if target not in visited and target < len(data):
                    entry_points.append(target)

            i += size

    output_lines.sort(key=lambda line: int(line.split(":")[0], 16))
    return "\n".join(output_lines) + "\n"
