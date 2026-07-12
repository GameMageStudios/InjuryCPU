import argparse
import sys
import os
import pyperclip

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from assembler import assemble_file, assemble_list_file
from assembler.output import to_hex_dump, to_hex_string
from assembler.parser import AssemblyError


def main():
    parser = argparse.ArgumentParser(description="Injury CPU Assembler")
    parser.add_argument("input", help="Input assembly file (or - for stdin)")
    parser.add_argument("-o", "--output", help="Output file (default: stdout)")
    parser.add_argument(
        "-f",
        "--format",
        choices=["hex", "bin", "dump"],
        default="hex",
        help="Output format: hex (string), bin (raw binary), dump (hex dump)",
    )
    parser.add_argument(
        "-l", "--list", action="store_true", help="Show assembly listing"
    )
    args = parser.parse_args()

    try:
        if args.list:
            if args.input == "-":
                source = sys.stdin.read()
                from assembler import assemble_list

                listing = assemble_list(source)
            else:
                listing = assemble_list_file(args.input)
            if args.output:
                with open(args.output, "w") as f:
                    f.write(listing)
            else:
                print(listing)
            return

        if args.input == "-":
            source = sys.stdin.read()
            from assembler import assemble

            result = assemble(source, fmt="bytes")
        else:
            result = assemble_file(args.input, fmt="bytes")

        if args.format == "hex":
            output = to_hex_string(result)
        elif args.format == "dump":
            output = to_hex_dump(result)
        else:
            if args.output:
                with open(args.output, "wb") as f:
                    f.write(result)
            else:
                sys.stdout.buffer.write(result)
            return

        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
        else:
            print(output)
            pyperclip.copy(output)

    except AssemblyError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
