import re
import os


def strip_comments(source: str) -> str:
    result = []
    i = 0
    length = len(source)
    in_block = False

    while i < length:
        if in_block:
            if source[i] == "*" and i + 1 < length and source[i + 1] == "/":
                in_block = False
                i += 2
            else:
                i += 1
            continue

        if source[i] == ";":
            while i < length and source[i] != "\n":
                i += 1
            continue

        if source[i] == "/" and i + 1 < length and source[i + 1] == "*":
            in_block = True
            i += 2
            continue

        result.append(source[i])
        i += 1

    return "".join(result)


def process_defines(source: str) -> tuple[str, dict[str, str]]:
    defines = {}
    lines = source.split("\n")
    result = []

    for line in lines:
        stripped = line.strip()
        m = re.match(r"#define\s+(\S+)\s+(.*)", stripped)
        if m:
            defines[m.group(1)] = m.group(2).strip()
        else:
            result.append(line)

    return "\n".join(result), defines


def apply_defines(source: str, defines: dict[str, str]) -> str:
    if not defines:
        return source

    for name, value in defines.items():
        pattern = re.compile(r"(?<!\w)" + re.escape(name) + r"(?!\w)")
        source = pattern.sub(value, source)

    return source


def process_includes(source: str, base_dir: str, seen: set[str] | None = None) -> str:
    if seen is None:
        seen = set()

    lines = source.split("\n")
    result = []

    for line in lines:
        stripped = line.strip()
        m = re.match(r'#include\s+"(.+)"', stripped)
        if m:
            inc_path = os.path.normpath(os.path.join(base_dir, m.group(1)))
            if inc_path in seen:
                raise RecursionError(f"Circular include detected: {inc_path}")
            seen.add(inc_path)
            if not os.path.isfile(inc_path):
                raise FileNotFoundError(f"Include file not found: {inc_path}")
            with open(inc_path, "r") as f:
                inc_source = f.read()
            inc_dir = os.path.dirname(inc_path)
            inc_source = process_includes(inc_source, inc_dir, seen)
            result.append(inc_source)
        else:
            result.append(line)

    return "\n".join(result)


MACRO_DEF_RE = re.compile(r"#macro\s+(\w+)\s*\(([^)]*)\)\s*\{", re.DOTALL)


def process_macros(source: str) -> tuple[str, dict[str, tuple[list[str], str]]]:
    macros: dict[str, tuple[list[str], str]] = {}
    lines = source.split("\n")
    result = []
    i = 0

    while i < len(lines):
        stripped = lines[i].strip()
        m = MACRO_DEF_RE.match(stripped)
        if m:
            name = m.group(1)
            args_str = m.group(2).strip()
            args = (
                [a.strip() for a in args_str.split(",") if a.strip()]
                if args_str
                else []
            )

            body_lines = []
            if "{" in stripped:
                after_brace = stripped[stripped.index("{") + 1 :]
                if "}" in after_brace:
                    body_lines.append(after_brace[: after_brace.index("}")])
                else:
                    if after_brace.strip():
                        body_lines.append(after_brace.strip())
                    i += 1
                    while i < len(lines):
                        line = lines[i]
                        if "}" in line:
                            before_brace = line[: line.index("}")]
                            if before_brace.strip():
                                body_lines.append(before_brace.strip())
                            break
                        body_lines.append(line.strip())
                        i += 1
            else:
                i += 1
                while i < len(lines):
                    line = lines[i]
                    if "}" in line:
                        before_brace = line[: line.index("}")]
                        if before_brace.strip():
                            body_lines.append(before_brace.strip())
                        break
                    body_lines.append(line.strip())
                    i += 1

            body = "\n".join(body_lines)
            macros[name] = (args, body)
        else:
            result.append(lines[i])
        i += 1

    return "\n".join(result), macros


def expand_macros(source: str, macros: dict[str, tuple[list[str], str]]) -> str:
    if not macros:
        return source

    for _ in range(100):
        new_source = _expand_macros_once(source, macros)
        if new_source == source:
            break
        source = new_source

    return source


def _expand_macros_once(source: str, macros: dict[str, tuple[list[str], str]]) -> str:
    lines = source.split("\n")
    result = []

    for line in lines:
        stripped = line.strip()
        expanded = False

        for name, (params, body) in macros.items():
            pattern = re.compile(r"^" + re.escape(name) + r"\s*(.*)", re.DOTALL)
            pm = pattern.match(stripped)
            if pm:
                args_str = pm.group(1).strip()
                if args_str:
                    args = [a.strip() for a in args_str.split(",")]
                else:
                    args = []

                if len(args) != len(params):
                    raise ValueError(
                        f"Macro '{name}' expects {len(params)} arguments, got {len(args)}"
                    )

                expanded_body = body
                for param, arg in zip(params, args):
                    expanded_body = re.sub(
                        r"(?<!\w)" + re.escape(param) + r"(?!\w)",
                        arg,
                        expanded_body,
                    )

                for exp_line in expanded_body.split("\n"):
                    exp_stripped = exp_line.strip()
                    if exp_stripped:
                        result.append(exp_stripped)
                expanded = True
                break

        if not expanded:
            result.append(line)

    return "\n".join(result)


def preprocess(source: str, base_dir: str = ".") -> tuple[str, dict[str, str]]:
    source = process_includes(source, base_dir)
    source = strip_comments(source)
    source, macros = process_macros(source)
    source = expand_macros(source, macros)
    source, defines = process_defines(source)
    source = apply_defines(source, defines)
    return source, defines
