def to_hex(data: bytes, separator: str = "", prefix: str = "0x") -> str:
    return separator.join(f"{prefix}{b:02X}" for b in data)


def to_hex_string(data: bytes) -> str:
    return "".join(f"{b:02X}" for b in data)


def to_hex_dump(data: bytes, bytes_per_line: int = 16) -> str:
    lines = []
    for offset in range(0, len(data), bytes_per_line):
        chunk = data[offset : offset + bytes_per_line]
        hex_part = " ".join(f"{b:02X}" for b in chunk)
        ascii_part = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        lines.append(f"{offset:08X}  {hex_part:<{bytes_per_line * 3}}  {ascii_part}")
    return "\n".join(lines)


EXPANDED_JUMP_OPCODES = {"JMP", "JIF", "JIN"}


def to_listing(tokens, coded: list[tuple[int, list[int]]]) -> str:
    from .opcodes import INSTRUCTIONS, OPCODE_MAP

    lines = []
    code_index = 0
    for tok in tokens:
        if tok.label:
            lines.append(f"  {tok.label}:")
        if tok.mnemonic and code_index < len(coded):
            addr, code = coded[code_index]

            if tok.mnemonic in EXPANDED_JUMP_OPCODES and code[0] == OPCODE_MAP["LDI"]:
                ldi_addr, ldi_code = coded[code_index]
                jmp_addr, jmp_code = coded[code_index + 1]
                ldi_hex = " ".join(f"{b:02X}" for b in ldi_code)
                jmp_hex = " ".join(f"{b:02X}" for b in jmp_code)
                lines.append(f"  {ldi_addr:04X}  {ldi_hex:<20}  {tok.raw.strip()}")
                lines.append(f"  {jmp_addr:04X}  {jmp_hex:<20}")
                code_index += 2
            else:
                hex_bytes = " ".join(f"{b:02X}" for b in code)
                lines.append(f"  {addr:04X}  {hex_bytes:<20}  {tok.raw.strip()}")
                code_index += 1
        elif not tok.label:
            continue
    return "\n".join(lines)
