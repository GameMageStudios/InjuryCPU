import os
from .preprocessor import preprocess
from .lexer import tokenize
from .parser import assemble_lines
from .errors import AssemblyError
from .output import to_hex_string


def _run(
    source: str, base_dir: str = ".", filename: str | None = None
) -> list[tuple[int, list[int]]]:
    processed, defines, line_origin = preprocess(source, base_dir, filename=filename)
    tokens = tokenize(processed, line_origin)
    return assemble_lines(tokens, defines)


def assemble(
    source: str, base_dir: str = ".", fmt: str = "bytes", filename: str | None = None
) -> bytes | str:
    coded = _run(source, base_dir, filename=filename)

    if not coded:
        return b"" if fmt == "bytes" else ""

    max_addr = max(addr + len(code) for addr, code in coded)
    rom = bytearray(max_addr)
    for addr, code in coded:
        for i, b in enumerate(code):
            rom[addr + i] = b

    data = bytes(rom)
    if fmt == "hex":
        return to_hex_string(data)
    return data


def assemble_file(path: str, fmt: str = "bytes") -> bytes | str:
    base_dir = os.path.dirname(os.path.abspath(path))
    with open(path, "r") as f:
        source = f.read()
    return assemble(source, base_dir=base_dir, fmt=fmt, filename=path)


def assemble_list(source: str, base_dir: str = ".", filename: str | None = None) -> str:
    processed, defines, line_origin = preprocess(source, base_dir, filename=filename)
    tokens = tokenize(processed, line_origin)
    coded = assemble_lines(tokens, defines)
    from .output import to_listing

    return to_listing(tokens, coded)


def assemble_list_file(path: str) -> str:
    base_dir = os.path.dirname(os.path.abspath(path))
    with open(path, "r") as f:
        source = f.read()
    return assemble_list(source, base_dir, filename=path)
