# Injury CPU Assembler Documentation

## Overview

The Injury CPU is a 16-bit simulated embedded system. It has:
- **Quick Memory (QM):** 256 × 16-bit words (addressed 0x00–0xFF)
- **RAM:** 65,536 bytes (addressed 0x0000–0xFFFF)
- **Video Memory:** Last 4,000 bytes of RAM (0xF060–0xFFFF), 80×25 character display
- **Instructions:** Variable length, 1–4 bytes

---

## Quick Start

```asm
#define JMPADDR 0x0F

MSG: .db "Hello, World!" 0x00

start:
    LD  0x00, MSG           ; load first byte of string
    ST  0x00, 0xF060        ; write to video memory
    JMP start
```

```bash
python assembler/main.py program.asm -l          # listing
python assembler/main.py program.asm -o out.hex  # hex output
python assembler/main.py program.asm -f bin -o rom.bin  # binary
```

---

## Instruction Set

### 1-byte Instructions

| Opcode | Mnemonic | Description |
|--------|----------|-------------|
| `00`   | `NOP`    | No operation |

### 2-byte Instructions

| Opcode | Mnemonic | Operand 1 | Description |
|--------|----------|-----------|-------------|
| `20`   | `CPC`    | Q-addr    | Copy PC into QM[Q-addr] |
| `21`   | `JMP`    | Q-addr    | Jump to address in QM[Q-addr] |

### 3-byte Instructions

| Opcode | Mnemonic | Operand 1 | Operand 2 | Description |
|--------|----------|-----------|-----------|-------------|
| `01`   | `LDI`    | Q-addr    | Value (16-bit) | Load immediate into QM |
| `02`   | `LD`     | Q-addr    | RAM-addr (16-bit) | Load from RAM into QM |
| `03`   | `LDP`    | Q-addr    | Q-pointer | Load through pointer in QM |
| `04`   | `ST`     | Q-addr    | RAM-addr (16-bit) | Store from QM to RAM |
| `05`   | `STP`    | Q-addr    | Q-pointer | Store through pointer in QM |
| `06`   | `MOV`    | Q-src     | Q-dest    | Copy QM[src] to QM[dest] |
| `10`   | `NEG`    | Q-src     | Q-dest    | Negate QM[src] → QM[dest] |
| `11`   | `INV`    | Q-src     | Q-dest    | Bitwise NOT QM[src] → QM[dest] |
| `22`   | `JIF`    | Q-addr    | Q-cond    | Jump if QM[cond] ≠ 0 |
| `23`   | `JIN`    | Q-addr    | Q-cond    | Jump if QM[cond] = 0 |

### 4-byte Instructions

| Opcode | Mnemonic | Op 1 | Op 2 | Op 3 | Description |
|--------|----------|------|------|------|-------------|
| `08`   | `ADD`    | Q-a  | Q-b  | Q-str | QM[str] = QM[a] + QM[b] |
| `09`   | `SUB`    | Q-a  | Q-b  | Q-str | QM[str] = QM[a] - QM[b] |
| `0A`   | `MUL`    | Q-a  | Q-b  | Q-str | QM[str] = QM[a] × QM[b] |
| `0B`   | `DIV`    | Q-a  | Q-b  | Q-str | QM[str] = QM[a] ÷ QM[b] |
| `0C`   | `MOD`    | Q-a  | Q-b  | Q-str | QM[str] = QM[a] % QM[b] |
| `0D`   | `AND`    | Q-a  | Q-b  | Q-str | QM[str] = QM[a] & QM[b] |
| `0E`   | `OR`     | Q-a  | Q-b  | Q-str | QM[str] = QM[a] \| QM[b] |
| `0F`   | `XOR`    | Q-a  | Q-b  | Q-str | QM[str] = QM[a] ^ QM[b] |
| `12`   | `EQ`     | Q-a  | Q-b  | Q-str | QM[str] = (QM[a] == QM[b]) ? 1 : 0 |
| `13`   | `GT`     | Q-a  | Q-b  | Q-str | QM[str] = (QM[a] > QM[b]) ? 1 : 0 |
| `14`   | `LT`     | Q-a  | Q-b  | Q-str | QM[str] = (QM[a] < QM[b]) ? 1 : 0 |

All arithmetic wraps on overflow.

---

## Assembler Syntax

### Labels

Labels mark addresses in the code.

```asm
start:              ; main label — opens a local scope
    NOP
loop:               ; another main label
    NOP
```

### Local Labels

Local labels start with `.` and are scoped to the most recent main label. They can be reused across different scopes.

```asm
function_a:
.check:             ; function_a.check
    NOP

function_b:
.check:             ; function_b.check — different from above
    NOP
```

Referencing a local label resolves to the current scope:

```asm
function_a:
.check:
    JIF .check, 0x00       ; resolves to function_a.check
```

### Numbers

| Format | Example | Value |
|--------|---------|-------|
| Decimal | `42` | 42 |
| Hex | `0xFF` | 255 |
| Binary | `0b1010` | 10 |

### Number Formats

| Format | Example | Value |
|--------|---------|-------|
| Decimal | `42` | 42 |
| Hex | `0xFF` | 255 |
| Binary | `0b1010` | 10 |

---

## Directives

### `.db` — Define Byte

Emits one or more 8-bit values. Supports numbers, expressions, and string literals.

```asm
.db 0x48 0x65 0x6C           ; three bytes
.db "Hello"                   ; ASCII string
.db MSG & 0xFF                ; expression
.db "Hi", 0x00                ; comma-separated
```

### `.dw` — Define Word

Emits one or more 16-bit values (big-endian).

```asm
.dw 0x1234                    ; two bytes: 12 34
.dw start+4                   ; address expression
.dw MSG, handler              ; pointers
```

### Labels on Data Directives

Labels on `.db`/`.dw` give you a pointer to the data.

```asm
MSG:  .db "Hello" 0x00
TABLE: .dw handler_a, handler_b, handler_c
```

---

## Preprocessor

### `#define`

Text substitution. Values are substituted before assembly.

```asm
#define VIDEO 0xF060
#define JMPADDR 0x0F
LDI 0x00, 42
ST  0x00, VIDEO        ; expands to ST 0x00, 0xF060
```

### `#include`

Inlines another assembly file.

```asm
#include "video.asm"
#include "macros.asm"
```

Circular includes are detected and rejected.

### `#macro`

Parameterized macros. Body is enclosed in `{}`, arguments in `()`.

```asm
#macro CLEAN(qmem) {
    LDI qmem, 0x0000
}

#macro MOV3(a, b, c) {
    LDI a, 0x0000
    ADD a, b, c
}

#macro NOPARAM() {
    NOP
    NOP
}
```

Invoke by name with arguments:

```asm
CLEAN 0x00            ; expands to LDI 0x00, 0x0000
MOV3 0x00, 0x01, 0x02 ; expands to LDI 0x00, 0x0000 / ADD 0x00, 0x01, 0x02
NOPARAM               ; expands to NOP / NOP
```

Nesting works — macros can call other macros:

```asm
#macro CLEAR_SCREEN() {
    CLEAN 0x00
    CLEAN 0x01
}

CLEAR_SCREEN  ; expands to CLEAN 0x00 / CLEAN 0x01 / then each CLEAN expands
```

Argument substitution is whole-word — `qmem` inside the body is replaced with the argument value, but won't corrupt partial identifiers. Up to 100 expansion passes are supported for deep nesting.

### Comments

```asm
; This is a line comment

/*
   This is a
   block comment
*/
```

---

## Jump Expansion

`JMP`, `JIF`, and `JIN` read their jump target from Quick Memory (indirect). When used with a label, the assembler auto-expands to `LDI` + `JMP/JIF/JIN`:

```asm
#define JMPADDR 0x0F

start:
    LDI 0x00, 42
    JMP start          ; expands to:
                       ;   LDI 0x0F, <addr of start>
                       ;   JMP 0x0F
```

With a number, no expansion happens:

```asm
JMP 0x00              ; compiles directly to 21 00
```

`JMPADDR` must be `#define`d. If a label is used with JMP/JIF/JIN and `JMPADDR` is not defined, the assembler throws an error.

---

## Expressions

Full expression engine with PEMDAS precedence and parentheses.

### Operators (lowest to highest precedence)

| Category | Operators |
|----------|-----------|
| Comparison | `==` `!=` `<` `>` `<=` `>=` |
| Bitwise | `&` `\|` `^` |
| Shift | `<<` `>>` |
| Add/Sub | `+` `-` |
| Mul/Div | `*` `/` `%` |
| Unary | `-` (negate) `~` (NOT) |

### Usage

Use commas to separate operands when an expression contains spaces:

```asm
LDI 0x00, (2 + 3) * 4        ; 20
LDI 0x01, 0xFF & 0x0F         ; 15
LDI 0x02, 1 << 4              ; 16
LDI 0x03, ~0x00               ; 0xFFFF
LDI 0x04, (10 + 5) / 3       ; 5
```

Without commas (backward compat), no spaces in expressions:

```asm
LDI 0x00 (10+5)*4             ; also works
.dw start+4                   ; expression without spaces
```

Expressions work in all operand positions including `.db` and `.dw`:

```asm
.db MSG & 0xFF                ; low byte of address
.dw start + 4                 ; address arithmetic
```

Negative values from `~` are masked to the operand width (unsigned two's complement).

---

## Video Memory

The last 4,000 bytes of RAM (0xF060–0xFFFF) simulate an 80×25 character display.

| Address Range | Content |
|---------------|---------|
| 0xF060–0xF0FF | Row 0 (80 chars × 2 bytes) |
| 0xF100–0xF19F | Row 1 |
| ... | ... |
| 0xFCE0–0xFD7F | Row 24 |

Each character is 2 bytes:
- **Byte 0:** ASCII character code
- **Byte 1:** Color (upper 4 bits = foreground, lower 4 bits = background)

### Color Codes

| Value | Color | Value | Color |
|-------|-------|-------|-------|
| `0x0` | Black | `0x8` | Dark Gray |
| `0x1` | White | `0x9` | Light Gray |
| `0x2` | Bright Red | `0xA` | Dark Red |
| `0x3` | Bright Green | `0xB` | Dark Green |
| `0x4` | Bright Blue | `0xC` | Dark Blue |
| `0x5` | Bright Yellow | `0xD` | Dark Yellow |
| `0x6` | Bright Cyan | `0xE` | Dark Cyan |
| `0x7` | Bright Magenta | `0xF` | Dark Magenta |

Example — write white-on-black 'H' to top-left corner:

```asm
LDI 0x00, 'H'       ; the character we want to display
ST 0x00, 0xF060     ; store at the first character of video memory
LDI 0x00, 0x02      ; black on red
ST 0x00, (0xF060+1) ; store at the second position of video memory
```

---

## Examples

### Hello World

```asm
#define JMPADDR 0x0F

MSG: .db "Hello, World!" 0x00

start:
    LDI 0x00, MSG
    ST  0x00, 0xF060
    ; ... write each character ...
    JMP start
```

### Loop Counter

```asm
#define JMPADDR 0x0F

start:
    LDI 0x00, 0          ; counter = 0
    LDI 0x01, 10         ; limit = 10
    LDI 0x02, 1          ; increment = 1
.loop:
    ADD 0x00, 0x02, 0x00 ; counter++
    LT  0x00, 0x01, 0x03 ; QM[3] = (counter < 10)
    JIF loop, 0x03       ; if counter < 10, loop
.done:
    jmp .done
```

---

## CLI Reference

```
python assembler/main.py <input> [options]

Options:
  -h, --help            Show help
  -o, --output FILE     Output file (default: stdout)
  -f, --format FORMAT   hex (default) | bin | dump
  -l, --list            Show assembly listing
```

### Output Formats

| Format | Description |
|--------|-------------|
| `hex` | Continuous hex string: `01000042210F` |
| `bin` | Raw binary file |
| `dump` | Hex dump with ASCII: `00000000 01 00 00 42 ...  ....B` |

---

## Library API

```python
from assembler import assemble, assemble_file, assemble_list

# Assemble from string
result = assemble("LDI 0x00, 42\nJMP 0x00", fmt="hex")
result = assemble(source, fmt="bytes")

# Assemble from file
result = assemble_file("program.asm", fmt="hex")

# Get listing
listing = assemble_list(source)
listing = assemble_list_file("program.asm")
```
