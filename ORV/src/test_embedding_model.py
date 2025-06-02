# src/test_embedding_model.py

import os
import sys
import numpy as np
import tensorflow as tf
import cv2  # Za nalaganje in predobdelavo slik
import matplotlib.pyplot as plt

tf.keras.config.enable_unsafe_deserialization()

# Dodajanje korena projekta v sys.path, da lahko uvozimo module iz src
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)


from src import config  # Uporabimo konfiguracijo za poti in dimenzije
from src.model_definition import l2_normalize_layer_func # <<<---

# Uvozimo funkcijo za L2 normalizacijo, ki jo uporabljamo v modelu
def preprocess_image(image_path, target_height=config.IMG_HEIGHT, target_width=config.IMG_WIDTH):
    """Naloži sliko, jo spremeni v velikost in normalizira."""
    try:
        img = cv2.imread(image_path)
        if img is None:
            print(f"Napaka: Slike ni mogoče naložiti s poti: {image_path}")
            return None
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Pretvorba v RGB
        img_resized = cv2.resize(img, (target_width, target_height))
        img_normalized = img_resized.astype(np.float32) / 255.0
        # Model pričakuje batch slik, zato dodamo dimenzijo za batch (1, H, W, C)
        return np.expand_dims(img_normalized, axis=0)
    except Exception as e:
        print(f"Napaka pri predobdelavi slike {image_path}: {e}")
        return None

# Funkcije za izračun razdalje in podobnosti med embeddingi
def calculate_euclidean_distance(emb1, emb2):
    """Izračuna Evklidsko razdaljo med dvema embeddingoma."""
    return np.linalg.norm(emb1 - emb2)


def calculate_cosine_similarity(emb1, emb2):
    """Izračuna kosinusno podobnost med dvema embeddingoma."""
    # Zagotovi, da so embeddingi 1D arrayi
    emb1 = emb1.flatten()
    emb2 = emb2.flatten()
    dot_product = np.dot(emb1, emb2)
    norm_emb1 = np.linalg.norm(emb1)
    norm_emb2 = np.linalg.norm(emb2)
    if norm_emb1 == 0 or norm_emb2 == 0:  # Prepreči deljenje z nič
        return 0.0
    return dot_product / (norm_emb1 * norm_emb2)

# Glavna funkcija za testiranje naučenega embedding modela
def main_test():
    print("--- Testiranje naučenega Embedding Modela ---")

    # 1. Nalaganje naučenega embedding modela
    # 1. Nalaganje naučenega embedding modela
    model_path = os.path.join(config.MODEL_SAVE_DIR, config.EMBEDDING_MODEL_NAME)
    if not os.path.exists(model_path):
        print(f"NAPAKA: Model '{model_path}' ne obstaja. Prosim, najprej naučite model.")
        return

    print(f"Nalaganje modela iz: {model_path}")
    try:
        # POPRAVLJEN KLIC load_model:
        embedding_model = tf.keras.models.load_model(
            model_path,
            custom_objects={'l2_normalize_layer_func': l2_normalize_layer_func},  # <<<--- DODAJ TO
            compile=False
        )
        # embedding_model.summary()
    except Exception as e:
        print(f"NAPAKA pri nalaganju modela: {e}")
        return

    # 2. Priprava testnih slik
    test_image_dir = os.path.join(project_root, "test")
    # os.makedirs(test_image_dir, exist_ok=True) # Ni več nujno, če mapa že obstaja

    referencna_slika_path = os.path.join(test_image_dir, "Tomi_Cigula1.png")  # Vaša referenčna slika
    test_slika_ista_oseba_path = os.path.join(test_image_dir, "Tomi_Cigula.png")  # Vaša druga slika (ista oseba)
    test_slika_druga_oseba_path = os.path.join(test_image_dir, "Aron_Pena.png")  # Slika druge osebe

    print(f"\nPOMEMBNO: Prepričajte se, da slike obstajajo na naslednjih poteh:")
    print(f"  Referenčna slika: {referencna_slika_path}")
    print(f"  Test (ista oseba): {test_slika_ista_oseba_path}")
    print(f"  Test (druga oseba): {test_slika_druga_oseba_path}")

    # Preverjanje obstoja datotek
    paths_to_check = [referencna_slika_path, test_slika_ista_oseba_path, test_slika_druga_oseba_path]
    for path in paths_to_check:
        if not os.path.exists(path):
            print(f"\nNAPAKA: Slika na poti '{path}' ne obstaja. Prekinjam test.")
            print("Prosim, preverite imena datotek in poti v skripti ter v mapi 'test_images_za_evalvacijo'.")
            return

    # 3. Predobdelava slik
    print("\nPredobdelava slik...")
    img_ref_processed = preprocess_image(referencna_slika_path)
    img_test_ista_processed = preprocess_image(test_slika_ista_oseba_path)
    img_test_druga_processed = preprocess_image(test_slika_druga_oseba_path)

    if img_ref_processed is None or img_test_ista_processed is None or img_test_druga_processed is None:
        print("NAPAKA pri predobdelavi ene od slik. Prekinjam.")
        return

    # 4. Generiranje embeddingov
    print("\nGeneriranje embeddingov...")
    emb_ref = embedding_model.predict(img_ref_processed)
    emb_test_ista = embedding_model.predict(img_test_ista_processed)
    emb_test_druga = embedding_model.predict(img_test_druga_processed)

    # print(f"  Oblika referenčnega embeddinga: {emb_ref.shape}") # (1, 128)

    # 5. Shranjevanje referenčnega embeddinga (tukaj ga samo hranimo v spremenljivki)
    shranjen_referencni_embedding = emb_ref[0]  # Uporabimo 1D array
    # print(f"  'Shranjen' referenčni embedding (prvih 5 vrednosti): {shranjen_referencni_embedding[:5]}")

    # 6. Primerjava embeddingov
    print("\nPrimerjava embeddingov s shranjenim referenčnim embeddingom:")

    # Primerjava z isto osebo
    razdalja_ista = calculate_euclidean_distance(shranjen_referencni_embedding, emb_test_ista[0])
    podobnost_ista = calculate_cosine_similarity(shranjen_referencni_embedding, emb_test_ista[0])
    print(
        f"  Test z ISTO osebo ('{os.path.basename(referencna_slika_path)}' vs '{os.path.basename(test_slika_ista_oseba_path)}'):")
    print(f"    Evklidska razdalja: {razdalja_ista:.4f}")
    print(f"    Kosinusna podobnost: {podobnost_ista:.4f}")

    # Primerjava z drugo osebo
    razdalja_druga = calculate_euclidean_distance(shranjen_referencni_embedding, emb_test_druga[0])
    podobnost_druga = calculate_cosine_similarity(shranjen_referencni_embedding, emb_test_druga[0])
    print(
        f"  Test z DRUGO osebo ('{os.path.basename(referencna_slika_path)}' vs '{os.path.basename(test_slika_druga_oseba_path)}'):")
    print(f"    Evklidska razdalja: {razdalja_druga:.4f}")
    print(f"    Kosinusna podobnost: {podobnost_druga:.4f}")

    # 7. Odločitev na podlagi praga
    PRAG_RAZDALJE = 0.8  #
    PRAG_PODOBNOSTI = 0.7  #

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

    # Prikaz slik
    try:
        fig, axs = plt.subplots(1, 3, figsize=(15, 5))

        img_r = cv2.imread(referencna_slika_path)
        if img_r is not None:
            axs[0].imshow(cv2.cvtColor(img_r, cv2.COLOR_BGR2RGB))
        axs[0].set_title(f"Referenca: {os.path.basename(referencna_slika_path)}")
        axs[0].axis('off')

        img_i = cv2.imread(test_slika_ista_oseba_path)
        if img_i is not None:
            axs[1].imshow(cv2.cvtColor(img_i, cv2.COLOR_BGR2RGB))
        axs[1].set_title(
            f"Ista oseba (D:{razdalja_ista:.2f} S:{podobnost_ista:.2f})\n{os.path.basename(test_slika_ista_oseba_path)}")
        axs[1].axis('off')

        img_d = cv2.imread(test_slika_druga_oseba_path)
        if img_d is not None:
            axs[2].imshow(cv2.cvtColor(img_d, cv2.COLOR_BGR2RGB))
        axs[2].set_title(
            f"Druga oseba (D:{razdalja_druga:.2f} S:{podobnost_druga:.2f})\n{os.path.basename(test_slika_druga_oseba_path)}")
        axs[2].axis('off')

        plt.tight_layout()
        plt.show()
    except Exception as e_plot:
        print(f"Napaka pri prikazovanju slik: {e_plot}")


if __name__ == '__main__':
    gpus = tf.config.list_physical_devices('GPU')
    if gpus:
        try:
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
            # print(f"Na voljo {len(gpus)} GPU(s), memory growth nastavljen.")
        except RuntimeError as e:
            print(e)
    # else:
    # print("GPU ni na voljo, model bo deloval na CPU.")

    main_test()