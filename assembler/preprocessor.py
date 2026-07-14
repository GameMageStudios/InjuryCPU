import re
import os


LineOrigin = tuple[str, int] | None


def strip_comments(source: str, line_origin: list[LineOrigin]) -> str:
    result = []
    i = 0
    length = len(source)
    in_block = False
    out_lines: list[list[str]] = [[]]
    out_line_idx = 0

    while i < length:
        if source[i] == "\n":
            out_lines.append([])
            out_line_idx += 1
            result.append("\n")
            i += 1
            continue

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

        out_lines[out_line_idx].append(source[i])
        result.append(source[i])
        i += 1

    # Build new origin mapping: each output line inherits origin from its input line
    in_lines = source.split("\n")
    new_origin: list[LineOrigin] = []
    in_idx = 0
    for out_chars in out_lines:
        out_text = "".join(out_chars)
        # Find which input line this output line's content starts from
        if in_idx < len(line_origin):
            new_origin.append(line_origin[in_idx])
        else:
            new_origin.append(None)
        # Advance input index for non-empty output lines
        if out_text.strip() and in_idx < len(in_lines) - 1:
            in_idx += 1
        elif not out_text.strip() and in_idx < len(in_lines):
            in_idx += 1

    line_origin.clear()
    line_origin.extend(new_origin)
    return "".join(result)


def process_defines(
    source: str, line_origin: list[LineOrigin]
) -> tuple[str, dict[str, str]]:
    defines = {}
    lines = source.split("\n")
    result = []
    new_origin: list[LineOrigin] = []

    for line, origin in zip(lines, line_origin):
        stripped = line.strip()
        m = re.match(r"#define\s+(\S+)\s+(.*)", stripped)
        if m:
            defines[m.group(1)] = m.group(2).strip()
        else:
            result.append(line)
            new_origin.append(origin)

    line_origin.clear()
    line_origin.extend(new_origin)
    return "\n".join(result), defines


def apply_defines(source: str, defines: dict[str, str]) -> str:
    if not defines:
        return source

    for name, value in defines.items():
        pattern = re.compile(r"(?<!\w)" + re.escape(name) + r"(?!\w)")
        source = pattern.sub(value, source)

    return source


def process_includes(
    source: str,
    base_dir: str,
    seen: set[str] | None = None,
    main_filename: str | None = None,
) -> tuple[str, list[LineOrigin]]:
    if seen is None:
        seen = set()

    lines = source.split("\n")
    result: list[str] = []
    line_origin: list[LineOrigin] = []

    for line_num, line in enumerate(lines, start=1):
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
            inc_text, inc_origin = process_includes(
                inc_source, inc_dir, seen, main_filename=inc_path
            )
            inc_lines = inc_text.split("\n")
            for inc_line, inc_line_origin in zip(inc_lines, inc_origin):
                result.append(inc_line)
                line_origin.append(inc_line_origin)
        else:
            result.append(line)
            origin_file = main_filename if main_filename else None
            line_origin.append((origin_file, line_num))

    return "\n".join(result), line_origin


MACRO_DEF_RE = re.compile(r"#macro\s+(\w+)\s*\(([^)]*)\)\s*\{", re.DOTALL)


def process_macros(
    source: str, line_origin: list[LineOrigin]
) -> tuple[str, dict[str, tuple[list[str], str]]]:
    macros: dict[str, tuple[list[str], str]] = {}
    lines = source.split("\n")
    result = []
    new_origin: list[LineOrigin] = []
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
            new_origin.append(line_origin[i] if i < len(line_origin) else None)
        i += 1

    line_origin.clear()
    line_origin.extend(new_origin)
    return "\n".join(result), macros


def expand_macros(
    source: str, macros: dict[str, tuple[list[str], str]], line_origin: list[LineOrigin]
) -> str:
    if not macros:
        return source

    for _ in range(100):
        new_source, new_origin = _expand_macros_once(source, macros, line_origin)
        if new_source == source:
            break
        source = new_source
        line_origin.clear()
        line_origin.extend(new_origin)

    return source


def _expand_macros_once(
    source: str, macros: dict[str, tuple[list[str], str]], line_origin: list[LineOrigin]
) -> tuple[str, list[LineOrigin]]:
    lines = source.split("\n")
    result = []
    new_origin: list[LineOrigin] = []

    for line_idx, line in enumerate(lines):
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

                origin_entry = (
                    line_origin[line_idx] if line_idx < len(line_origin) else None
                )
                for exp_line in expanded_body.split("\n"):
                    exp_stripped = exp_line.strip()
                    if exp_stripped:
                        result.append(exp_stripped)
                        new_origin.append(origin_entry)
                expanded = True
                break

        if not expanded:
            result.append(line)
            new_origin.append(
                line_origin[line_idx] if line_idx < len(line_origin) else None
            )

    return "\n".join(result), new_origin


def preprocess(
    source: str, base_dir: str = ".", filename: str | None = None
) -> tuple[str, dict[str, str], list[LineOrigin]]:
    source, line_origin = process_includes(source, base_dir, main_filename=filename)
    source = strip_comments(source, line_origin)
    source, macros = process_macros(source, line_origin)
    source = expand_macros(source, macros, line_origin)
    source, defines = process_defines(source, line_origin)
    source = apply_defines(source, defines)
    return source, defines, line_origin
