INSTRUCTIONS = {
    # Each entry: opcode, list of operand sizes in bytes
    "NOP": {"opcode": 0x00, "op_sizes": []},
    "LDI": {"opcode": 0x01, "op_sizes": [1, 2]},  # Q-addr, Value
    "LD": {"opcode": 0x02, "op_sizes": [1, 2]},  # Q-addr, RAM-addr
    "LDP": {"opcode": 0x03, "op_sizes": [1, 1]},  # Q-addr, Q-pointer
    "ST": {"opcode": 0x04, "op_sizes": [1, 2]},  # Q-addr, RAM-addr
    "STP": {"opcode": 0x05, "op_sizes": [1, 1]},  # Q-addr, Q-pointer
    "MOV": {"opcode": 0x06, "op_sizes": [1, 1]},  # Q-src, Q-dest
    "ADD": {"opcode": 0x08, "op_sizes": [1, 1, 1]},
    "SUB": {"opcode": 0x09, "op_sizes": [1, 1, 1]},
    "MUL": {"opcode": 0x0A, "op_sizes": [1, 1, 1]},
    "DIV": {"opcode": 0x0B, "op_sizes": [1, 1, 1]},
    "MOD": {"opcode": 0x0C, "op_sizes": [1, 1, 1]},
    "AND": {"opcode": 0x0D, "op_sizes": [1, 1, 1]},
    "OR": {"opcode": 0x0E, "op_sizes": [1, 1, 1]},
    "XOR": {"opcode": 0x0F, "op_sizes": [1, 1, 1]},
    "NEG": {"opcode": 0x10, "op_sizes": [1, 1]},
    "INV": {"opcode": 0x11, "op_sizes": [1, 1]},
    "EQ": {"opcode": 0x12, "op_sizes": [1, 1, 1]},
    "GT": {"opcode": 0x13, "op_sizes": [1, 1, 1]},
    "LT": {"opcode": 0x14, "op_sizes": [1, 1, 1]},
    "CPC": {"opcode": 0x20, "op_sizes": [1]},
    "JMP": {"opcode": 0x21, "op_sizes": [1]},
    "JIF": {"opcode": 0x22, "op_sizes": [1, 1]},
    "JIN": {"opcode": 0x23, "op_sizes": [1, 1]},
    "CALL": {"opcode": 0x24, "op_sizes": [1]},  # Q-addr, 2-byte instruction
    "RET": {"opcode": 0x25, "op_sizes": []},  # 1-byte instruction
    "INP": {"opcode": 0x28, "op_sizes": [1]},
    "SND": {"opcode": 0x29, "op_sizes": [1]},
}


def instr_size(mnemonic: str) -> int:
    return 1 + sum(INSTRUCTIONS[mnemonic]["op_sizes"])


OPCODE_MAP = {name: info["opcode"] for name, info in INSTRUCTIONS.items()}
