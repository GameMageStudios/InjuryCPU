from __future__ import annotations


class ExprError(Exception):
    pass


class ExprTokenizer:
    def __init__(self, s: str):
        self.s = s
        self.pos = 0
        self.tokens: list[str] = []
        self._tokenize()

    def _skip_ws(self):
        while self.pos < len(self.s) and self.s[self.pos] in " \t":
            self.pos += 1

    def _tokenize(self):
        while self.pos < len(self.s):
            self._skip_ws()
            if self.pos >= len(self.s):
                break
            c = self.s[self.pos]
            if c in "+-*/%&|^~!<>()":
                if (
                    c == "0"
                    and self.pos + 1 < len(self.s)
                    and self.s[self.pos + 1] in "xXbB"
                ):
                    self._read_number()
                elif c == "(" or c == ")":
                    self.tokens.append(c)
                    self.pos += 1
                elif (
                    c == "<"
                    and self.pos + 1 < len(self.s)
                    and self.s[self.pos + 1] == "="
                ):
                    self.tokens.append("<=")
                    self.pos += 2
                elif (
                    c == ">"
                    and self.pos + 1 < len(self.s)
                    and self.s[self.pos + 1] == "="
                ):
                    self.tokens.append(">=")
                    self.pos += 2
                elif (
                    c == "!"
                    and self.pos + 1 < len(self.s)
                    and self.s[self.pos + 1] == "="
                ):
                    self.tokens.append("!=")
                    self.pos += 2
                elif (
                    c == "="
                    and self.pos + 1 < len(self.s)
                    and self.s[self.pos + 1] == "="
                ):
                    self.tokens.append("==")
                    self.pos += 2
                elif (
                    c == "<"
                    and self.pos + 1 < len(self.s)
                    and self.s[self.pos + 1] == "<"
                ):
                    self.tokens.append("<<")
                    self.pos += 2
                elif (
                    c == ">"
                    and self.pos + 1 < len(self.s)
                    and self.s[self.pos + 1] == ">"
                ):
                    self.tokens.append(">>")
                    self.pos += 2
                else:
                    self.tokens.append(c)
                    self.pos += 1
            elif c.isdigit() or c == "-":
                self._read_number()
            elif c == "'":
                self._read_char()
            elif c.isalpha() or c == "_" or c == ".":
                self._read_ident()
            else:
                raise ExprError(f"Unexpected character '{c}' at position {self.pos}")

    def _read_number(self):
        start = self.pos
        if self.s[self.pos] == "0" and self.pos + 1 < len(self.s):
            nxt = self.s[self.pos + 1]
            if nxt in "xX":
                self.pos += 2
                while self.pos < len(self.s) and (
                    self.s[self.pos] in "0123456789abcdefABCDEF"
                ):
                    self.pos += 1
            elif nxt in "bB":
                self.pos += 2
                while self.pos < len(self.s) and self.s[self.pos] in "01":
                    self.pos += 1
            else:
                self.pos += 1
                while self.pos < len(self.s) and self.s[self.pos].isdigit():
                    self.pos += 1
        else:
            if self.s[self.pos] == "-":
                self.pos += 1
            while self.pos < len(self.s) and self.s[self.pos].isdigit():
                self.pos += 1
        self.tokens.append(self.s[start : self.pos])

    def _read_char(self):
        start = self.pos
        self.pos += 1
        if self.pos >= len(self.s):
            raise ExprError("Unterminated character constant")
        if self.s[self.pos] == "\\":
            self.pos += 1
            if self.pos >= len(self.s):
                raise ExprError("Unterminated escape sequence")
            escape = self.s[self.pos]
            self.pos += 1
            if self.pos >= len(self.s) or self.s[self.pos] != "'":
                raise ExprError("Unterminated character constant")
            self.pos += 1
            esc_map = {
                "n": 10,
                "t": 9,
                "r": 13,
                "0": 0,
                "\\": ord("\\"),
                "'": ord("'"),
                '"': ord('"'),
            }
            val = esc_map.get(escape, ord(escape))
            self.tokens.append(str(val))
        else:
            ch = self.s[self.pos]
            self.pos += 1
            if self.pos >= len(self.s) or self.s[self.pos] != "'":
                raise ExprError("Unterminated character constant")
            self.pos += 1
            self.tokens.append(str(ord(ch)))

    def _read_ident(self):
        start = self.pos
        while self.pos < len(self.s) and (
            self.s[self.pos].isalnum() or self.s[self.pos] in "_."
        ):
            self.pos += 1
        self.tokens.append(self.s[start : self.pos])


def parse_number(s: str) -> int | None:
    s = s.strip()
    if not s:
        return None
    try:
        if s.startswith("0x") or s.startswith("0X"):
            return int(s, 16)
        if s.startswith("0b") or s.startswith("0B"):
            return int(s, 2)
        return int(s)
    except ValueError:
        return None


class ExprParser:
    def __init__(self, tokens: list[str], lookup):
        self.tokens = tokens
        self.pos = 0
        self.lookup = lookup

    def peek(self) -> str | None:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def consume(self) -> str:
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def expect(self, s: str):
        tok = self.consume()
        if tok != s:
            raise ExprError(f"Expected '{s}', got '{tok}'")

    def parse(self) -> int:
        val = self.parse_comparison()
        if self.pos < len(self.tokens):
            raise ExprError(f"Unexpected token '{self.tokens[self.pos]}'")
        return val

    def parse_comparison(self) -> int:
        left = self.parse_bitwise()
        op = self.peek()
        if op in ("==", "!=", "<", ">", "<=", ">="):
            self.consume()
            right = self.parse_bitwise()
            if op == "==":
                return 1 if left == right else 0
            if op == "!=":
                return 1 if left != right else 0
            if op == "<":
                return 1 if left < right else 0
            if op == ">":
                return 1 if left > right else 0
            if op == "<=":
                return 1 if left <= right else 0
            if op == ">=":
                return 1 if left >= right else 0
        return left

    def parse_bitwise(self) -> int:
        left = self.parse_shift()
        while self.peek() in ("&", "|", "^"):
            op = self.consume()
            right = self.parse_shift()
            if op == "&":
                left = left & right
            elif op == "|":
                left = left | right
            elif op == "^":
                left = left ^ right
        return left

    def parse_shift(self) -> int:
        left = self.parse_add()
        while self.peek() in ("<<", ">>"):
            op = self.consume()
            right = self.parse_add()
            if op == "<<":
                left = left << right
            elif op == ">>":
                left = left >> right
        return left

    def parse_add(self) -> int:
        left = self.parse_mul()
        while self.peek() in ("+", "-"):
            op = self.consume()
            right = self.parse_mul()
            if op == "+":
                left = left + right
            elif op == "-":
                left = left - right
        return left

    def parse_mul(self) -> int:
        left = self.parse_unary()
        while self.peek() in ("*", "/", "%"):
            op = self.consume()
            right = self.parse_unary()
            if op == "*":
                left = left * right
            elif op == "/":
                if right == 0:
                    raise ExprError("Division by zero")
                left = left // right
            elif op == "%":
                if right == 0:
                    raise ExprError("Division by zero")
                left = left % right
        return left

    def parse_unary(self) -> int:
        op = self.peek()
        if op == "-":
            self.consume()
            return -self.parse_unary()
        if op == "~":
            self.consume()
            return ~self.parse_unary()
        return self.parse_primary()

    def parse_primary(self) -> int:
        tok = self.peek()
        if tok is None:
            raise ExprError("Unexpected end of expression")

        if tok == "(":
            self.consume()
            val = self.parse_comparison()
            self.expect(")")
            return val

        self.consume()
        num = parse_number(tok)
        if num is not None:
            return num

        if self.lookup is not None:
            val = self.lookup(tok)
            if val is not None:
                return val

        raise ExprError(f"Unknown symbol '{tok}'")


def evaluate(expr: str, lookup=None) -> int:
    def _lookup(name: str):
        if lookup is not None:
            return lookup(name)
        return None

    tokenizer = ExprTokenizer(expr.strip())
    parser = ExprParser(tokenizer.tokens, _lookup)
    return parser.parse()


def try_evaluate(expr: str, lookup=None) -> int | None:
    try:
        return evaluate(expr, lookup)
    except ExprError:
        return None
