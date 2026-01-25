import os
import cv2
import numpy as np
import tempfile
from pathlib import Path
from datetime import datetime

from .flocic import compress, decompress

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
COMPRESSED_STORAGE_DIR = os.path.join(SCRIPT_DIR, '..', 'ORV', 'data_storage', 'compressed_faces')
os.makedirs(COMPRESSED_STORAGE_DIR, exist_ok=True)


def compress_face_image(image_bytes, user_id, save_to_storage=True):
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        raise ValueError("Neveljavni bajti slike")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    target_size = 128
    gray_resized = cv2.resize(gray, (target_size, target_size), interpolation=cv2.INTER_AREA)

    with tempfile.NamedTemporaryFile(suffix='.bmp', delete=False) as tmp_bmp:
        tmp_bmp_path = tmp_bmp.name
        cv2.imwrite(tmp_bmp_path, gray_resized)

    original_size = os.path.getsize(tmp_bmp_path)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{user_id}_{timestamp}.fic"

    if save_to_storage:
        compressed_path = os.path.join(COMPRESSED_STORAGE_DIR, filename)
    else:
        compressed_path = tempfile.mktemp(suffix='.fic')

    compress(tmp_bmp_path, compressed_path)
    compressed_size = os.path.getsize(compressed_path)

    os.unlink(tmp_bmp_path)

    compression_ratio = original_size / compressed_size if compressed_size > 0 else 0

    result = {
        'compressed_data': open(compressed_path, 'rb').read() if not save_to_storage else None,
        'original_size': original_size,
        'compressed_size': compressed_size,
        'compression_ratio': compression_ratio,
        'width': target_size,
        'height': target_size,
        'file_path': compressed_path if save_to_storage else None
    }

    if not save_to_storage:
        os.unlink(compressed_path)

    if save_to_storage:
        print(f"[FLoCIC] Kompresirana slika shranjena: {compressed_path}")
        print(f"[FLoCIC] Razmerje: {compression_ratio:.2f}x ({original_size} -> {compressed_size} B)")

    return result


def decompress_face_image(compressed_path):
    with tempfile.NamedTemporaryFile(suffix='.bmp', delete=False) as tmp_bmp:
        tmp_bmp_path = tmp_bmp.name

    decompress(compressed_path, tmp_bmp_path)
    img = cv2.imread(tmp_bmp_path, cv2.IMREAD_GRAYSCALE)
    os.unlink(tmp_bmp_path)

    return img


def get_compression_stats(user_id=None):
    files = list(Path(COMPRESSED_STORAGE_DIR).glob('*.fic'))

    if user_id:
        files = [f for f in files if f.name.startswith(user_id + '_')]

    total_compressed = sum(f.stat().st_size for f in files)
    estimated_original_per_file = 128 * 128 + 1078
    total_original = len(files) * estimated_original_per_file

    return {
        'total_files': len(files),
        'total_compressed_bytes': total_compressed,
        'estimated_original_bytes': total_original,
        'estimated_savings': total_original - total_compressed,
        'average_ratio': total_original / total_compressed if total_compressed > 0 else 0
    }
