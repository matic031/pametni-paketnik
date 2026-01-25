import os
import time
from pathlib import Path
from flocic import compress, decompress

def get_file_size(filename):
    return os.path.getsize(filename)

def format_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.2f} MB"

def test_images():
    bmp_dir = Path('slikeBMP')
    if not bmp_dir.exists():
        bmp_dir = Path('../../slikeBMP')

    test_files = [
        'Man.bmp',
        'Barb.bmp',
        'Lena.bmp',
        'Barbara.bmp',
        'Baboon.bmp',
        'Cameraman.bmp',
        'Peppers.bmp',
        'Bridge.bmp',
        'boat 512x512.bmp',
        'Earth.bmp'
    ]

    results = []

    output_dir = Path('output')
    output_dir.mkdir(exist_ok=True)

    compressed_dir = Path('compressed')
    compressed_dir.mkdir(exist_ok=True)

    print("=" * 120)
    print(f"{'#':<4} {'Datoteka':<25} {'Original':<15} {'Stisnjeno':<15} {'Razmerje':<12} {'Čas komp.':<12} {'Čas dekomp.':<12}")
    print("=" * 120)

    for i, filename in enumerate(test_files, 1):
        input_path = bmp_dir / filename
        compressed_path = compressed_dir / f"{Path(filename).stem}.fic"
        output_path = output_dir / f"{Path(filename).stem}_decompressed.bmp"

        if not input_path.exists():
            print(f"Opozorilo: {filename} ne obstaja, preskakujem...")
            continue

        original_size = get_file_size(input_path)

        start_time = time.time()
        compress(str(input_path), str(compressed_path))
        compress_time = time.time() - start_time

        compressed_size = get_file_size(compressed_path)

        start_time = time.time()
        decompress(str(compressed_path), str(output_path))
        decompress_time = time.time() - start_time

        ratio = original_size / compressed_size if compressed_size > 0 else 0

        results.append({
            'num': i,
            'filename': filename,
            'original': original_size,
            'compressed': compressed_size,
            'ratio': ratio,
            'compress_time': compress_time,
            'decompress_time': decompress_time
        })

        print(f"{i:<4} {filename:<25} {format_size(original_size):<15} {format_size(compressed_size):<15} "
              f"{ratio:<12.3f} {compress_time:<12.4f} {decompress_time:<12.4f}")

    print("=" * 120)

    total_original = sum(r['original'] for r in results)
    total_compressed = sum(r['compressed'] for r in results)
    avg_ratio = total_original / total_compressed if total_compressed > 0 else 0

    print(f"\nSkupaj: Original={format_size(total_original)}, Stisnjeno={format_size(total_compressed)}, "
          f"Povprečno razmerje={avg_ratio:.3f}")

    print("\n5 decompressed slik shranjenih v 'output/' direktoriju za preverjanje")
    print("Kompresirane datoteke v 'compressed/' direktoriju")

if __name__ == '__main__':
    test_images()
