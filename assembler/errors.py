class AssemblyError(Exception):
    def __init__(
        self,
        msg: str,
        filename: str | None = None,
        lineno: int | None = None,
        col: int | None = None,
    ):
        self.filename = filename
        self.lineno = lineno
        self.col = col
        parts = []
        if filename:
            parts.append(filename)
        if lineno is not None:
            parts.append(str(lineno))
            if col is not None:
                parts.append(str(col))
        prefix = ":".join(parts)
        if prefix:
            super().__init__(f"{prefix}: {msg}")
        else:
            super().__init__(msg)
