# process_lfw_data.py
import tensorflow_datasets as tfds
import numpy as np
import cv2
import os
import argparse
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import time

# --- Osnovne nastavitve ---
PROJECT_DATA_DIR = os.path.join(os.getcwd(), 'data')
RAW_DATA_DIR = PROJECT_DATA_DIR

# Nastavitve za Viola-Jones detektor
CASCADE_XML_FILENAME = 'haarcascade_frontalface_default.xml'
CASCADE_PATH = os.path.join(os.getcwd(), CASCADE_XML_FILENAME)

# Ciljne dimenzije slik
TARGET_IMG_HEIGHT = 64
TARGET_IMG_WIDTH = 64

# Nastavitve za delitev podatkov
VAL_SPLIT_SIZE = 0.15
TEST_SPLIT_SIZE = 0.15
RANDOM_STATE = 42


def denoise_image_opencv(image_uint8):
    """Odstrani šum iz slike (uint8 NumPy array) z Gaussovim filtrom."""
    return cv2.GaussianBlur(image_uint8, (3, 3), 0)


def detect_and_crop_face(image_np_uint8, face_cascade):
    """
    Z Viola-Jones detektorjem poišče obraz, ga obreže in pomanjša na ciljno velikost.
    Vhodna slika mora biti NumPy array v RGB formatu.
    """
    # Viola-Jones potrebuje sivinsko sliko. OpenCV interno pričakuje BGR za pretvorbo v sivo,
    # zato najprej pretvorimo iz RGB (TFDS format) v BGR.
    img_bgr = cv2.cvtColor(image_np_uint8, cv2.COLOR_RGB2BGR)
    gray_img = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray_img, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    if len(faces) == 0:
        return None

    if len(faces) > 1:
        faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)

    x, y, w, h = faces[0]

    # Obrežemo originalno RGB sliko
    cropped_face_rgb = image_np_uint8[y:y + h, x:x + w]

    # Pomanjšamo/povečamo na ciljno velikost
    resized_face = cv2.resize(cropped_face_rgb, (TARGET_IMG_WIDTH, TARGET_IMG_HEIGHT), interpolation=cv2.INTER_AREA)

    return resized_face


def extract_tfds_to_numpy(data_dir):
    """
    KORAK 1: Naloži TFDS dataset in ga takoj pretvori v surove NumPy arraye.
    S tem popolnoma izoliramo TensorFlow.
    """
    print("Korak A: Ekstrakcija TFDS v surove NumPy arraye...")
    try:
        # Naložimo dataset brez `as_supervised=True`, da dobimo slovarje
        ds, info = tfds.load('lfw', split='train', as_supervised=False, data_dir=data_dir, with_info=True)
        num_examples = info.splits['train'].num_examples
        print(f"Dataset naložen. Število primerov za pretvorbo: {num_examples}")

        # Uporabimo as_numpy_iterator za direktno in zanesljivo pretvorbo
        images_list = []
        labels_list = []

        # *** NAJNOVEJŠI POPRAVEK: Eksplicitno dostopamo do ključev 'image' in 'label' ***
        for example_dict in tfds.as_numpy(ds):
            images_list.append(example_dict['image'])
            labels_list.append(example_dict['label'])

        raw_images_np = np.array(images_list)
        raw_labels_np = np.array(labels_list)

        print(f"Ekstrakcija končana. Oblika slik: {raw_images_np.shape}, Oblika oznak: {raw_labels_np.shape}")
        return raw_images_np, raw_labels_np

    except Exception as e:
        print(f"Napaka pri nalaganju ali ekstrakciji LFW dataseta: {e}")
        return None, None


def process_numpy_data(raw_images, raw_labels, apply_denoising=False):
    """
    KORAK 2: Obdela surove NumPy arraye z OpenCV. Brez TensorFlow-a.
    """
    print("\nKorak B: Obdelava surovih NumPy podatkov z OpenCV...")
    if not os.path.exists(CASCADE_PATH):
        print(f"NAPAKA: Datoteka '{CASCADE_PATH}' ne obstaja.")
        return None, None

    face_cascade = cv2.CascadeClassifier(CASCADE_PATH)

    all_images = []
    all_labels = []
    num_examples = len(raw_images)

    start_time = time.time()
    for i in range(num_examples):
        image_np_uint8 = raw_images[i]
        label_bytes = raw_labels[i]

        cropped_face_uint8 = detect_and_crop_face(image_np_uint8, face_cascade)

        if cropped_face_uint8 is not None:
            final_image_uint8 = cropped_face_uint8

            if apply_denoising:
                final_image_uint8 = denoise_image_opencv(final_image_uint8)

            final_image_float32 = final_image_uint8.astype(np.float32) / 255.0
            all_images.append(final_image_float32)
            all_labels.append(label_bytes)

        if (i + 1) % 500 == 0:
            elapsed = time.time() - start_time
            print(f"  Obdelanih {i + 1}/{num_examples} slik... (Čas: {elapsed:.2f}s)")

    print(f"\nObdelava končana. Uspešno obrezanih: {len(all_images)}, Preskočenih: {num_examples - len(all_images)}")

    if not all_images:
        return None, None

    return np.array(all_images), np.array(all_labels)


def split_data_into_sets(images, labels):
    """Razdeli podatke na učno, validacijsko in testno množico s stratifikacijo."""
    print("\nDelitev podatkov na učno, validacijsko in testno množico...")

    if len(images) < 3:
        print("OPOZORILO: Premalo podatkov za delitev. Vse gre v učno množico.")
        return images, labels, np.array([]), np.array([]), np.array([]), np.array([])

    try:
        X_rem, X_test, y_rem, y_test = train_test_split(
            images, labels, test_size=TEST_SPLIT_SIZE, random_state=RANDOM_STATE, stratify=labels
        )
        relative_val_size = VAL_SPLIT_SIZE / (1.0 - TEST_SPLIT_SIZE)
        X_train, X_val, y_train, y_val = train_test_split(
            X_rem, y_rem, test_size=relative_val_size, random_state=RANDOM_STATE, stratify=y_rem
        )
    except ValueError as e:
        print(f"OPOZORILO: Stratificirana delitev ni uspela ({e}). Uporabljam navadno delitev.")
        X_rem, X_test, y_rem, y_test = train_test_split(
            images, labels, test_size=TEST_SPLIT_SIZE, random_state=RANDOM_STATE
        )
        relative_val_size = VAL_SPLIT_SIZE / (1.0 - TEST_SPLIT_SIZE)
        X_train, X_val, y_train, y_val = train_test_split(
            X_rem, y_rem, test_size=relative_val_size, random_state=RANDOM_STATE
        )

    print(f"  Učna množica: {X_train.shape[0]} slik")
    print(f"  Validacijska množica: {X_val.shape[0]} slik")
    print(f"  Testna množica: {X_test.shape[0]} slik")
    return X_train, y_train, X_val, y_val, X_test, y_test


def display_sample_images(images, labels, count=5, title="Vzorčne slike"):
    """Prikaže nekaj vzorčnih slik iz NumPy arraya."""
    if images.size == 0:
        print(f"{title}: Ni slik za prikaz.")
        return
    plt.figure(figsize=(15, 5))
    plt.suptitle(title, fontsize=16)
    indices = np.random.choice(len(images), min(count, len(images)), replace=False)
    for i, idx in enumerate(indices):
        plt.subplot(1, len(indices), i + 1)
        plt.imshow(images[idx])
        label_str = labels[idx].decode('utf-8', errors='ignore')
        plt.title(f"{label_str[:15]}")
        plt.axis('off')
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.show()


def run_processing(apply_denoising_flag, show_plots):
    """Glavna funkcija za izvedbo celotnega procesa."""
    print(f"*** Začenjam procesiranje LFW podatkov (Odstranjevanje šuma: {apply_denoising_flag}) ***")

    raw_images_np, raw_labels_np = extract_tfds_to_numpy(data_dir=RAW_DATA_DIR)
    if raw_images_np is None:
        print("Ekstrakcija podatkov ni uspela. Prekinjam.")
        return False

    all_images, all_labels = process_numpy_data(raw_images_np, raw_labels_np, apply_denoising=apply_denoising_flag)
    if all_images is None:
        print("Obdelava podatkov ni uspela. Prekinjam.")
        return False

    if show_plots:
        display_sample_images(all_images, all_labels, count=5,
                              title=f"Primeri obrezanih obrazov (Denoise: {apply_denoising_flag})")

    train_img, train_lbl, val_img, val_lbl, test_img, test_lbl = split_data_into_sets(all_images, all_labels)

    denoise_suffix = f"_denoise-{str(apply_denoising_flag).lower()}"
    output_filename = f'lfw_processed_splits{denoise_suffix}.npz'
    output_path = os.path.join(PROJECT_DATA_DIR, output_filename)

    np.savez_compressed(
        output_path,
        train_images=train_img, train_labels=train_lbl,
        val_images=val_img, val_labels=val_lbl,
        test_images=test_img, test_labels=test_lbl
    )
    print(f"\nPodatkovne množice shranjene v {output_path}")
    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Predelava LFW dataseta z detekcijo in obrezovanjem obrazov.")
    parser.add_argument('--denoise', action='store_true', help="Vklopi odstranjevanje šuma.")
    parser.add_argument('--no_plots', action='store_true', help="Izklopi prikazovanje vzorčnih slik.")
    args = parser.parse_args()

    show_plots_flag = not args.no_plots

    print(f"Argument --denoise je nastavljen na: {args.denoise}")
    print(f"Argument --no_plots je nastavljen na: {args.no_plots} (Prikaz slik: {show_plots_flag})")

    run_processing(apply_denoising_flag=args.denoise, show_plots=show_plots_flag)