import struct
import zlib
import sys

def replace_str(input: bytes, old: bytes, new: bytes) -> bytes:
    """Replace all occurrences of `old` with `new` in `input`."""
    
    old_len_u32 = len(old).to_bytes(4, byteorder='little')
    new_len_u32 = len(new).to_bytes(4, byteorder='little')

    old = old_len_u32 + old
    new = new_len_u32 + new

    return input.replace(old, new)


def patch_save(file_path: str):
    magic: bytes = b""
    type_char: bytes = b""
    version: int = 0
    decompressed_length: int = 0

    with open(file_path, "rb") as file:
        magic = file.read(3)
        if magic != b"BOW":
            raise ValueError("Invalid file format: expected 'BOW' magic number")

        type_char = file.read(1)
        version = struct.unpack("<I", file.read(4))[0]
        decompressed_length = struct.unpack("<I", file.read(4))[0]
        compressed_data = file.read()
        decompressed_data = zlib.decompress(compressed_data)

        if len(decompressed_data) != decompressed_length:
            raise ValueError(
                f"Decompressed data length {len(decompressed_data)} does not match expected length {decompressed_length}"
            )

        print(magic, type_char, version)
        print(decompressed_length)

    with open(file_path, "wb") as file:
        patched_data = decompressed_data

        patched_data = replace_str(patched_data,
                    b"system/save.asb",
                    b"save:/inject.iet")

        print(patched_data[:256])
        patched_compressed = zlib.compress(patched_data, level=9)

        # construct the new file
        header = (
            magic
            + type_char
            + struct.pack("<I", version)
            + struct.pack("<I", len(patched_data))
        )

        file.write(header)
        file.write(patched_compressed)

        print("Patched!")


if __name__ == "__main__":
    # read from the argument
    if len(sys.argv) < 2:
        print("Usage: python patch-save.py <file>")
        sys.exit(1)

    file_path = sys.argv[1]
    patch_save(file_path)
