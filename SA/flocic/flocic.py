import struct
import sys
import math
from pathlib import Path

class BitStream:
    def __init__(self):
        self.bits = []

    def write_bit(self, bit):
        self.bits.append(1 if bit else 0)

    def write_bits(self, value, num_bits):
        for i in range(num_bits - 1, -1, -1):
            self.write_bit((value >> i) & 1)

    def to_bytes(self):
        byte_array = bytearray()
        for i in range(0, len(self.bits), 8):
            byte = 0
            for j in range(8):
                if i + j < len(self.bits):
                    byte |= (self.bits[i + j] << (7 - j))
            byte_array.append(byte)
        return bytes(byte_array)

    def from_bytes(self, data):
        self.bits = []
        for byte in data:
            for i in range(7, -1, -1):
                self.bits.append((byte >> i) & 1)
        return self

    def read_bit(self, pos):
        if pos < len(self.bits):
            return self.bits[pos]
        return 0

    def read_bits(self, pos, num_bits):
        value = 0
        for i in range(num_bits):
            value = (value << 1) | self.read_bit(pos + i)
        return value, pos + num_bits

def read_bmp(filename):
    with open(filename, 'rb') as f:
        header = f.read(54)

        width = struct.unpack('<I', header[18:22])[0]
        height = struct.unpack('<I', header[22:26])[0]
        bits_per_pixel = struct.unpack('<H', header[28:30])[0]

        if bits_per_pixel == 8:
            palette = f.read(1024)

        row_size = ((width * bits_per_pixel + 31) // 32) * 4
        pixels = []

        for y in range(height):
            row_data = f.read(row_size)
            row = []
            for x in range(width):
                row.append(row_data[x])
            pixels.append(row)

        pixels.reverse()

        return pixels, width, height

def write_bmp(filename, pixels, width, height):
    row_size = ((width * 8 + 31) // 32) * 4
    pixel_data_size = row_size * height
    file_size = 54 + 1024 + pixel_data_size

    header = bytearray(54)
    header[0:2] = b'BM'
    struct.pack_into('<I', header, 2, file_size)
    struct.pack_into('<I', header, 10, 1078)
    struct.pack_into('<I', header, 14, 40)
    struct.pack_into('<I', header, 18, width)
    struct.pack_into('<I', header, 22, height)
    struct.pack_into('<H', header, 26, 1)
    struct.pack_into('<H', header, 28, 8)
    struct.pack_into('<I', header, 34, pixel_data_size)

    palette = bytearray()
    for i in range(256):
        palette.extend([i, i, i, 0])

    reversed_pixels = list(reversed(pixels))

    pixel_data = bytearray()
    for row in reversed_pixels:
        row_bytes = bytearray(row)
        padding = row_size - width
        row_bytes.extend([0] * padding)
        pixel_data.extend(row_bytes)

    with open(filename, 'wb') as f:
        f.write(header)
        f.write(palette)
        f.write(pixel_data)

def predict(pixels, x, y, width, height):
    if y == 0 and x == 0:
        return pixels[0][0]
    elif y == 0:
        return pixels[0][x - 1]
    elif x == 0:
        return pixels[y - 1][0]
    else:
        left = pixels[y][x - 1]
        top = pixels[y - 1][x]
        diag = pixels[y - 1][x - 1]

        if diag >= max(left, top):
            return min(left, top)
        elif diag <= min(left, top):
            return max(left, top)
        else:
            return left + top - diag

def jpeg_ls_predict(pixels, width, height):
    E = []

    for y in range(height):
        for x in range(width):
            if y == 0 and x == 0:
                E.append(pixels[0][0])
            elif y == 0:
                E.append(pixels[0][x - 1] - pixels[0][x])
            elif x == 0:
                E.append(pixels[y - 1][0] - pixels[y][0])
            else:
                pred = predict(pixels, x, y, width, height)
                E.append(pred - pixels[y][x])

    return E

def interleave(E):
    N = [E[0]]
    for i in range(1, len(E)):
        if E[i] >= 0:
            N.append(2 * E[i])
        else:
            N.append(2 * abs(E[i]) - 1)
    return N

def create_cumulative(N):
    C = [N[0]]
    for i in range(1, len(N)):
        C.append(C[i - 1] + N[i])
    return C

def encode_binary(bits, value, num_bits):
    for i in range(num_bits - 1, -1, -1):
        bits.write_bit((value >> i) & 1)

def interpolative_encode(bits, C, L, H):
    if H - L > 1:
        if C[H] != C[L]:
            m = (H + L) // 2
            g = math.ceil(math.log2(C[H] - C[L] + 1))
            encode_binary(bits, C[m] - C[L], g)
            if L < m:
                interpolative_encode(bits, C, L, m)
            if m < H:
                interpolative_encode(bits, C, m, H)

def compress(input_file, output_file):
    pixels, width, height = read_bmp(input_file)

    E = jpeg_ls_predict(pixels, width, height)

    n = width * height
    N = interleave(E)
    C = create_cumulative(N)

    bits = BitStream()

    header_data = struct.pack('<H', height)
    header_data += struct.pack('<B', C[0] & 0xFF)
    header_data += struct.pack('<I', C[n - 1])
    header_data += struct.pack('<I', n)

    interpolative_encode(bits, C, 0, n - 1)

    with open(output_file, 'wb') as f:
        f.write(header_data)
        f.write(bits.to_bytes())

def decode_binary(bits, pos, num_bits):
    value = 0
    for i in range(num_bits):
        if pos + i < len(bits.bits):
            value = (value << 1) | bits.bits[pos + i]
    return value, pos + num_bits

def interpolative_decode(bits, C, L, H, pos):
    if H - L > 1:
        if C[L] == C[H]:
            for i in range(L + 1, H):
                C[i] = C[L]
        else:
            m = (H + L) // 2
            g = math.ceil(math.log2(C[H] - C[L] + 1))
            value, pos = decode_binary(bits, pos, g)
            C[m] = C[L] + value
            if L < m:
                pos = interpolative_decode(bits, C, L, m, pos)
            if m < H:
                pos = interpolative_decode(bits, C, m, H, pos)
    return pos

def initialize_C(n, c0, cn_1):
    C = [c0] + [-1] * (n - 2) + [cn_1]
    return C

def deinterleave(N):
    E = [N[0]]
    for i in range(1, len(N)):
        if N[i] % 2 == 0:
            E.append(N[i] // 2)
        else:
            E.append(-((N[i] + 1) // 2))
    return E

def inverse_jpeg_ls_predict(E, width, height):
    pixels = [[0] * width for _ in range(height)]

    for y in range(height):
        for x in range(width):
            idx = y * width + x
            if y == 0 and x == 0:
                pixels[0][0] = E[0]
            elif y == 0:
                pixels[0][x] = pixels[0][x - 1] - E[idx]
            elif x == 0:
                pixels[y][0] = pixels[y - 1][0] - E[idx]
            else:
                left = pixels[y][x - 1]
                top = pixels[y - 1][x]
                diag = pixels[y - 1][x - 1]

                if diag >= max(left, top):
                    pred = min(left, top)
                elif diag <= min(left, top):
                    pred = max(left, top)
                else:
                    pred = left + top - diag

                pixels[y][x] = pred - E[idx]

    for y in range(height):
        for x in range(width):
            pixels[y][x] = max(0, min(255, pixels[y][x]))

    return pixels

def decompress(input_file, output_file):
    with open(input_file, 'rb') as f:
        header_data = f.read(11)

        height = struct.unpack('<H', header_data[0:2])[0]
        c0 = struct.unpack('<B', header_data[2:3])[0]
        cn_1 = struct.unpack('<I', header_data[3:7])[0]
        n = struct.unpack('<I', header_data[7:11])[0]

        width = n // height

        compressed_data = f.read()

    C = initialize_C(n, c0, cn_1)

    bits = BitStream()
    bits.from_bytes(compressed_data)

    interpolative_decode(bits, C, 0, n - 1, 0)

    N = [C[0]]
    for i in range(1, n):
        N.append(C[i] - C[i - 1])

    E = deinterleave(N)

    pixels = inverse_jpeg_ls_predict(E, width, height)

    write_bmp(output_file, pixels, width, height)

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('Uporaba: python flocic.py [compress|decompress] <vhodna_slika> <izhodna_slika>')
        sys.exit(1)

    mode = sys.argv[1]
    input_file = sys.argv[2]
    output_file = sys.argv[3]

    if mode == 'compress':
        compress(input_file, output_file)
        print(f'Kompresija končana: {output_file}')
    elif mode == 'decompress':
        decompress(input_file, output_file)
        print(f'Dekompresija končana: {output_file}')
    else:
        print('Napaka: način mora biti "compress" ali "decompress"')
        sys.exit(1)
