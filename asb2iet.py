import struct
import sys
import os


def read_asb_file(file_path: str) -> str:
    output_lines = []

    with open(file_path, "rb") as file:

        def u32():
            return struct.unpack("<I", file.read(4))[0]

        def read_string():
            length = u32()
            if length == 0xFFFFFFFF:
                return ""

            content = file.read(length)
            null_terminator = file.read(1)

            if null_terminator != b"\x00":
                raise ValueError(f"Expected null terminator after string, found {null_terminator!r}")

            return content.decode("utf-8")

        magic = file.read(5)
        if magic != b"ASB\x00\x00":
            raise ValueError(f"Invalid magic number")

        block_count = u32()

        for _ in range(block_count):
            block_type = u32()
            block_name = read_string()

            # --- Block Type 1: Label ---
            # A label in .iet is like `*top` or `*game_start`
            if block_type == 1:
                output_lines.append(f"*{block_name}")

            # --- Block Type 0: Command ---
            # A command is like `[calllua function="..."]` or `[wt]`
            elif block_type == 0:
                # This block has an extra unknown/unused 4-byte field before the parameter count.
                _unknown_field = u32()  # We read and discard it.

                # Read the number of parameters for this command.
                param_count = u32()

                params = []
                # Loop through and read each parameter key-value pair.
                for _ in range(param_count):
                    key = read_string()
                    value = read_string()
                    params.append((key, value))

                # Format the command string based on its parameters.
                if not params:
                    # No parameters, e.g., `[stop]` or `[wt]`
                    line = f"[{block_name}]"
                else:
                    param_parts = []
                    for key, value in params:
                        # Named parameter, e.g. `function="system_initlua"`
                        if key:
                            if '"' in value or " " in value:
                                param_parts.append(f"{key}='{value}'")
                            else:
                                param_parts.append(f'{key}="{value}"')

                        # Positional parameter, e.g., `off` in `[loading off]`
                        else:
                            param_parts.append(value)

                    param_str = " ".join(param_parts)
                    line = f"[{block_name} {param_str}]"

                # Special handling for [lua] blocks to ensure proper newlines
                if block_name == "lua" and params:
                    # The content is the first (and only) positional parameter
                    lua_code = params[0][1]
                    # Indent the lua code for readability, though not strictly required
                    indented_code = "\n".join(
                        [f"\t{l}" for l in lua_code.strip().split("\n")]
                    )
                    line = f"[lua]\n{indented_code}\n[/lua]"

                output_lines.append(line)

            else:
                print(
                    f"Warning: Unknown block type {block_type} with name '{block_name}' found. Skipping.",
                    file=sys.stderr,
                )

        # Add a blank line between distinct sections for readability, similar to source .iet
        # This is an aesthetic choice to better match the samples.
        final_text = ""
        for i, line in enumerate(output_lines):
            final_text += line + "\n"
            # If the next line is a label, add an extra newline before it.
            if i + 1 < len(output_lines) and output_lines[i + 1].startswith("*"):
                if not line.startswith("*"):  # Avoid double newlines between labels
                    final_text += "\n"

    return final_text.strip()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python read-asb.py <input.asb> [output.iet]")
        sys.exit(1)

    input_path = sys.argv[1]
    if not os.path.exists(input_path):
        print(f"Error: Input file not found at '{input_path}'")
        sys.exit(1)

    try:
        result = read_asb_file(input_path)

        if len(sys.argv) > 2:
            output_path = sys.argv[2]
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(result)
            print(f"Successfully decompiled '{input_path}' to '{output_path}'")
        else:
            # If no output file is specified, print to stdout
            print(result)

    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)
