import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from assembler.disasm import disassemble, parse_hex


def main():
    parser = argparse.ArgumentParser(description="Injury CPU Disassembler")
    parser.add_argument("input", help="Input hex string or binary file")
    parser.add_argument(
        "-f",
        "--format",
        choices=["hex", "bin"],
        default="hex",
        help="Input format: hex (hex string), bin (raw binary)",
    )
    parser.add_argument("-o", "--output", help="Output file (default: stdout)")
    args = parser.parse_args()

    try:
        if args.format == "hex":
            with open(args.input, "r") as f:
                hex_str = f.read()
            data = parse_hex(hex_str)
        else:
            with open(args.input, "rb") as f:
                data = f.read()

        result = disassemble(data)

        if args.output:
            with open(args.output, "w") as f:
                f.write(result)
        else:
            print(result, end="")

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
