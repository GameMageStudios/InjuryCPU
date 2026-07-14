# Injury CPU

Also visit [Website](https://gamemagestudios.github.io/InjuryCPU/)

## About

Injury CPU is a project made mostly in the Scratch and Python programing languages.
Scratch simulator, for execution, Python assembler for easier code writing.

## VSCode Extension

The project includes a very bad VSCode extension (*injury-cpu-asm-0.1.0.vsix*)

## Documentation

There is some documentation in docs.md and isa.ods, but i do not like writing .MD files so no good docs are available yet.

## Assembler

Requirements:
- `pyperclip` install with `pip install pyperclip`

```
usage: main.py [-h] [-o OUTPUT] [-f {hex,bin,dump}] [-l] input

positional arguments:
  input                 Input assembly file (or - for stdin)

options:
  -h, --help            show this help message and exit
  -o, --output OUTPUT   Output file (default: stdout)
  -f, --format {hex,bin,dump}
                        Output format: hex (string), bin (raw binary), dump (hex dump)
  -l, --list            Show assembly listing
```

The "dump" format automaticaly copies the output into clipboard
