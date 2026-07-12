from dataclasses import dataclass, field
from .opcodes import INSTRUCTIONS


@dataclass
class TokenLine:
    lineno: int
    label: str | None = None
    mnemonic: str | None = None
    operands: list[str] = field(default_factory=list)
    raw: str = ""


def parse_number(s: str) -> int | None:
    s = s.strip()
    if s.startswith("0x") or s.startswith("0X"):
        try:
            return int(s, 16)
        except ValueError:
            return None
    if s.startswith("0b") or s.startswith("0B"):
        try:
            return int(s, 2)
        except ValueError:
            return None
    try:
        return int(s)
    except ValueError:
        return None


DATA_DIRECTIVES = {".DB", ".DW"}


def split_tokens(s: str) -> list[str]:
    tokens = []
    current = []
    in_quote = None
    i = 0
    while i < len(s):
        c = s[i]
        if c in ('"', "'") and in_quote is None:
            in_quote = c
            current.append(c)
        elif c == in_quote:
            in_quote = None
            current.append(c)
        elif c == "\\" and in_quote is not None and i + 1 < len(s):
            current.append(c)
            current.append(s[i + 1])
            i += 2
            continue
        elif c in (" ", "\t") and in_quote is None:
            if current:
                tokens.append("".join(current))
                current = []
        else:
            current.append(c)
        i += 1
    if current:
        tokens.append("".join(current))
    return tokens


def split_operands(s: str) -> list[str]:
    parts = []
    current = []
    in_quote = None
    i = 0
    while i < len(s):
        c = s[i]
        if c in ('"', "'") and in_quote is None:
            in_quote = c
            current.append(c)
        elif c == in_quote:
            in_quote = None
            current.append(c)
        elif c == "\\" and in_quote is not None and i + 1 < len(s):
            current.append(c)
            current.append(s[i + 1])
            i += 2
            continue
        elif c == "," and in_quote is None:
            parts.append("".join(current).strip())
            current = []
        else:
            current.append(c)
        i += 1
    tail = "".join(current).strip()
    if tail:
        parts.append(tail)
    return parts


def tokenize(source: str) -> list[TokenLine]:
    lines = source.split("\n")
    result = []

    for i, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped:
            continue

        label = None
        mnemonic = None
        operands = []

        if ":" in stripped:
            parts = stripped.split(":", 1)
            label_candidate = parts[0].strip()
            if (
                label_candidate
                and " " not in label_candidate
                and "\t" not in label_candidate
            ):
                label = label_candidate
                stripped = parts[1].strip()

        if not stripped:
            result.append(TokenLine(lineno=i, label=label, raw=line))
            continue

        tokens = split_tokens(stripped)
        upper = tokens[0].upper()
        mnemonic = tokens[0]
        rest = " ".join(tokens[1:])

        if upper in INSTRUCTIONS or upper in DATA_DIRECTIVES:
            if "," in rest:
                operands = split_operands(rest)
            else:
                operands = tokens[1:]
        else:
            operands = tokens[1:]

        result.append(
            TokenLine(
                lineno=i, label=label, mnemonic=mnemonic, operands=operands, raw=line
            )
        )

    return result
