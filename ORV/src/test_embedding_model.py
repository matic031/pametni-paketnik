# src/test_embedding_model.py

import os
import sys
import numpy as np
import tensorflow as tf
import cv2
import matplotlib.pyplot as plt

tf.keras.config.enable_unsafe_deserialization()

# Dodajanje korena projekta v sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

from src import config
from src.model_definition import l2_normalize_layer_func

# --- Nastavitve in funkcija za detekcijo obraza ---
CASCADE_XML_FILENAME = 'haarcascade_frontalface_default.xml'
CASCADE_PATH = os.path.join(project_root, CASCADE_XML_FILENAME)


def detect_and_crop_face(image_np_uint8, face_cascade, target_height, target_width):
    """
    Poišče največji obraz na sliki, ga obreže in pomanjša.
    Vrne obrezan obraz ali None, če obraz ni najden.
    """
    img_bgr = cv2.cvtColor(image_np_uint8, cv2.COLOR_RGB2BGR)
    gray_img = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray_img, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50))

    if len(faces) == 0:
        return None

    if len(faces) > 1:
        faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)

    x, y, w, h = faces[0]
    cropped_face_rgb = image_np_uint8[y:y + h, x:x + w]
    resized_face = cv2.resize(cropped_face_rgb, (target_width, target_height), interpolation=cv2.INTER_AREA)

    return resized_face


# --- Funkcija za predobdelavo slike ---
def preprocess_image(image_path, face_cascade, target_height=config.IMG_HEIGHT, target_width=config.IMG_WIDTH):
    """
    Naloži sliko, na njej zazna in obreže obraz.
    Vrne DVE vrednosti:
    1. Obdelan batch za model (1, H, W, C), normaliziran.
    2. Obrezan obraz za prikaz (H, W, C), z vrednostmi [0, 255] uint8.
    """
    try:
        img = cv2.imread(image_path)
        if img is None:
            print(f"Napaka: Slike ni mogoče naložiti s poti: {image_path}")
            return None, None

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        cropped_face = detect_and_crop_face(img_rgb, face_cascade, target_height, target_width)

        display_image = None
        if cropped_face is None:
            print(f"OPOZORILO: Obraz ni bil najden na sliki: {os.path.basename(image_path)}. Uporabljam celotno sliko.")
            cropped_face = cv2.resize(img_rgb, (target_width, target_height), interpolation=cv2.INTER_AREA)
            display_image = cropped_face
        else:
            display_image = cropped_face

        img_normalized = cropped_face.astype(np.float32) / 255.0
        model_input = np.expand_dims(img_normalized, axis=0)

        return model_input, display_image

    except Exception as e:
        print(f"Napaka pri predobdelavi slike {image_path}: {e}")
        return None, None


# --- Funkcije za izračun razdalje in podobnosti ---
def calculate_euclidean_distance(emb1, emb2):
    return np.linalg.norm(emb1 - emb2)


def calculate_cosine_similarity(emb1, emb2):
    emb1, emb2 = emb1.flatten(), emb2.flatten()
    dot_product = np.dot(emb1, emb2)
    norm_emb1, norm_emb2 = np.linalg.norm(emb1), np.linalg.norm(emb2)
    return 0.0 if norm_emb1 == 0 or norm_emb2 == 0 else dot_product / (norm_emb1 * norm_emb2)


def main_test():
    print("--- Testiranje naučenega Embedding Modela ---")

    # 1. Nalaganje modela in detektorja obrazov
    model_path = os.path.join(config.MODEL_SAVE_DIR, config.EMBEDDING_MODEL_NAME)
    #model_path = os.path.join('model/', config.EMBEDDING_MODEL_NAME)
    if not os.path.exists(model_path) or not os.path.exists(CASCADE_PATH):
        if not os.path.exists(model_path):
            print(f"NAPAKA: Model '{model_path}' ne obstaja. Prosim, najprej naučite model.")
        if not os.path.exists(CASCADE_PATH):
            print(f"NAPAKA: Datoteka '{CASCADE_PATH}' ne obstaja. Prosim, prenesi jo v korensko mapo projekta.")
        return

    print(f"Nalaganje modela iz: {model_path}")
    embedding_model = tf.keras.models.load_model(
        model_path,
        custom_objects={'l2_normalize_layer_func': l2_normalize_layer_func},
        compile=False
    )

    print(f"Nalaganje detektorja obrazov iz: {CASCADE_PATH}")
    face_cascade = cv2.CascadeClassifier(CASCADE_PATH)

    # 2. Priprava poti do testnih slik
    test_image_dir = os.path.join(project_root, "test")
    referencna_slika_path = os.path.join(test_image_dir, "Tomi_Cigula1.png")
    test_slika_ista_oseba_path = os.path.join(test_image_dir, "Tomi_Cigula.png")
    test_slika_druga_oseba_path = os.path.join(test_image_dir, "Aron_Pena.png")

    paths_to_check = [referencna_slika_path, test_slika_ista_oseba_path, test_slika_druga_oseba_path]
    for path in paths_to_check:
        if not os.path.exists(path):
            print(f"\nNAPAKA: Slika na poti '{path}' ne obstaja. Prekinjam test.")
            return

    # 3. Predobdelava slik z detekcijo obraza
    print("\nPredobdelava slik (z detekcijo obrazov)...")
    img_ref_model, img_ref_display = preprocess_image(referencna_slika_path, face_cascade)
    img_test_ista_model, img_test_ista_display = preprocess_image(test_slika_ista_oseba_path, face_cascade)
    img_test_druga_model, img_test_druga_display = preprocess_image(test_slika_druga_oseba_path, face_cascade)

    if img_ref_model is None or img_test_ista_model is None or img_test_druga_model is None:
        print("NAPAKA pri predobdelavi ene od slik. Prekinjam.")
        return

    # 4. Generiranje embeddingov
    print("\nGeneriranje embeddingov...")
    emb_ref = embedding_model.predict(img_ref_model)
    emb_test_ista = embedding_model.predict(img_test_ista_model)
    emb_test_druga = embedding_model.predict(img_test_druga_model)

    # 5. Izračun razdalj in podobnosti
    shranjen_referencni_embedding = emb_ref[0]
    razdalja_ista = calculate_euclidean_distance(shranjen_referencni_embedding, emb_test_ista[0])
    podobnost_ista = calculate_cosine_similarity(shranjen_referencni_embedding, emb_test_ista[0])
    razdalja_druga = calculate_euclidean_distance(shranjen_referencni_embedding, emb_test_druga[0])
    podobnost_druga = calculate_cosine_similarity(shranjen_referencni_embedding, emb_test_druga[0])

    # 6. Izpis rezultatov v želenem formatu
    print("\nPrimerjava embeddingov s shranjenim referenčnim embeddingom:")
    print(
        f"  Test z ISTO osebo ('{os.path.basename(referencna_slika_path)}' vs '{os.path.basename(test_slika_ista_oseba_path)}'):")
    print(f"    Evklidska razdalja: {razdalja_ista:.4f}")
    print(f"    Kosinusna podobnost: {podobnost_ista:.4f}")
    print(
        f"  Test z DRUGO osebo ('{os.path.basename(referencna_slika_path)}' vs '{os.path.basename(test_slika_druga_oseba_path)}'):")
    print(f"    Evklidska razdalja: {razdalja_druga:.4f}")
    print(f"    Kosinusna podobnost: {podobnost_druga:.4f}")

    # 7. Odločitev na podlagi praga
    PRAG_RAZDALJE = 1.0
    PRAG_PODOBNOSTI = 0.5
    print(f"\nOdločitev (Prag razdalje < {PRAG_RAZDALJE}, Prag podobnosti > {PRAG_PODOBNOSTI}):")

    verificirano_ista_razdalja = razdalja_ista < PRAG_RAZDALJE
    verificirano_ista_podobnost = podobnost_ista > PRAG_PODOBNOSTI
    print(f"  VERIFIKACIJA - ISTA OSEBA (razdalja): {'USPEŠNA' if verificirano_ista_razdalja else 'NEUSPEŠNA'}")
    print(f"  VERIFIKACIJA - ISTA OSEBA (podobnost): {'USPEŠNA' if verificirano_ista_podobnost else 'NEUSPEŠNA'}")

    verificirano_druga_razdalja = razdalja_druga < PRAG_RAZDALJE
    verificirano_druga_podobnost = podobnost_druga > PRAG_PODOBNOSTI
    print(
        f"  VERIFIKACIJA - DRUGA OSEBA (razdalja): {'USPEŠNA (NAPAKA - False Accept!)' if verificirano_druga_razdalja else 'NEUSPEŠNA (PRAVILNO - True Reject)'}")
    print(
        f"  VERIFIKACIJA - DRUGA OSEBA (podobnost): {'USPEŠNA (NAPAKA - False Accept!)' if verificirano_druga_podobnost else 'NEUSPEŠNA (PRAVILNO - True Reject)'}")

    # 8. Prikaz obrezanih slik
    print("\nPrikaz obdelanih slik (kot jih vidi model)...")
    try:
        fig, axs = plt.subplots(1, 3, figsize=(10, 4))
        fig.suptitle("Slike po detekciji in obrezovanju obrazov")

        if img_ref_display is not None:
            axs[0].imshow(img_ref_display)
        axs[0].set_title(f"Referenca:\n{os.path.basename(referencna_slika_path)}")
        axs[0].axis('off')

        if img_test_ista_display is not None:
            axs[1].imshow(img_test_ista_display)
        axs[1].set_title(f"Ista (S:{podobnost_ista:.2f})\n{os.path.basename(test_slika_ista_oseba_path)}")
        axs[1].axis('off')

        if img_test_druga_display is not None:
            axs[2].imshow(img_test_druga_display)
        axs[2].set_title(f"Druga (S:{podobnost_druga:.2f})\n{os.path.basename(test_slika_druga_oseba_path)}")
        axs[2].axis('off')

        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.show()
    except Exception as e_plot:
        print(f"Napaka pri prikazovanju slik: {e_plot}")


# === DODAN MANJKAJOČI BLOK ===
if __name__ == '__main__':
    gpus = tf.config.list_physical_devices('GPU')
    if gpus:
        try:
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
        except RuntimeError as e:
            print(e)

    main_test()