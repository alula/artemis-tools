# b"BOW"
# 'S', 'G', 'X'
# u32: 1002
# u32: length of deflated data
# buffer

import struct
import zlib
import sys

def read_bow_file(file_path):
    with open(file_path, 'rb') as file:
        magic = file.read(3)
        if magic != b"BOW":
            raise ValueError("Invalid file format: expected 'BOW' magic number")
    
        type_char = file.read(1)
        version = struct.unpack('<I', file.read(4))[0]
        decompressed_length = struct.unpack('<I', file.read(4))[0]
        compressed_data = file.read()
        decompressed_data = zlib.decompress(compressed_data)
        
        if len(decompressed_data) != decompressed_length:
            raise ValueError(f"Decompressed data length {len(decompressed_data)} does not match expected length {decompressed_length}")
        
        print(magic, type_char, version)
        print(decompressed_length)

        return decompressed_data

if __name__ == "__main__":
    # read from the argument
    if len(sys.argv) < 2:
        print("Usage: python read-save.py <file> [output_decompressed_data]")
        sys.exit(1)

    file_path = sys.argv[1]
    decompressed = read_bow_file(file_path)

    if len(sys.argv) == 3:
        output_file = sys.argv[2]
        with open(output_file, 'wb') as out_file:
            out_file.write(decompressed)
        print(f"Decompressed data saved to {output_file}")