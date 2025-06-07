# face_embedder.py
import os
import sys
import numpy as np
import tensorflow as tf
import cv2
from typing import Union, Optional

# --- Nastavitev poti za pravilne importe ---
# Skripta predpostavlja, da se nahaja v korenu projekta (ORV/).
PROJECT_ROOT = os.getcwd()
SRC_PATH = os.path.join(PROJECT_ROOT, 'src')
if SRC_PATH not in sys.path:
    sys.path.append(SRC_PATH)

try:
    from src import config
    from src.model_definition import l2_normalize_layer_func
except ImportError as e:
    print(f"NAPAKA: Ni mogoče uvoziti modulov iz 'src/'. Prepričaj se, da je struktura map pravilna. Napaka: {e}")
    sys.exit(1)

# --- GLOBALNE SPREMENLJIVKE IN NALAGANJE VIROV ---
# Ta del se izvede samo enkrat, ko se modul prvič importa.

# Poti do potrebnih datotek
MODEL_PATH = os.path.join(PROJECT_ROOT, 'model', config.EMBEDDING_MODEL_NAME)
CASCADE_PATH = os.path.join(PROJECT_ROOT, 'haarcascade_frontalface_default.xml')

# Globalne spremenljivke za model in detektor
_model = None
_face_cascade = None
_is_initialized = False


def _initialize_resources():
    """
    Interna funkcija, ki naloži model in detektor v pomnilnik.
    Pokliče se samodejno ob prvem klicu glavne funkcije.
    """
    global _model, _face_cascade, _is_initialized

    if _is_initialized:
        return

    print("Inicializacija virov (model in detektor)... To se zgodi samo enkrat.")

    # Preverjanje obstoja datotek
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model ni najden na poti: {MODEL_PATH}")
    if not os.path.exists(CASCADE_PATH):
        raise FileNotFoundError(f"Haar cascade datoteka ni najdena na poti: {CASCADE_PATH}")

    # Nalaganje modela za prepoznavo obrazov
    try:
        tf.keras.config.enable_unsafe_deserialization()
        _model = tf.keras.models.load_model(
            MODEL_PATH,
            custom_objects={'l2_normalize_layer_func': l2_normalize_layer_func},
            compile=False
        )
        print("-> Model uspešno naložen.")
    except Exception as e:
        raise RuntimeError(f"Napaka pri nalaganju modela: {e}")

    # Nalaganje detektorja obrazov
    _face_cascade = cv2.CascadeClassifier(CASCADE_PATH)
    if _face_cascade.empty():
        raise IOError(f"Napaka pri nalaganju Haar cascade klasifikatorja iz: {CASCADE_PATH}")
    print("-> Detektor obrazov uspešno naložen.")

    _is_initialized = True
    print("Inicializacija končana.")


def _detect_and_crop_face(image_np_uint8):
    """
    Interna funkcija, ki poišče največji obraz, ga obreže in pomanjša.
    """
    img_rgb = cv2.cvtColor(image_np_uint8, cv2.COLOR_BGR2RGB)
    gray_img = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)

    faces = _face_cascade.detectMultiScale(gray_img, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50))
    if not len(faces):
        return None

    if len(faces) > 1:
        faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)

    x, y, w, h = faces[0]
    cropped = img_rgb[y:y + h, x:x + w]
    resized = cv2.resize(cropped, (config.IMG_WIDTH, config.IMG_HEIGHT), interpolation=cv2.INTER_AREA)
    return resized


# --- GLAVNA FUNKCIJA ZA UPORABO V API-ju ---

def get_embedding_from_image_bytes(image_bytes: bytes) -> Optional[np.ndarray]:
    """
    Glavna funkcija. Sprejme sliko v obliki bajtov, vrne 128-dimenzionalni embedding.

    Args:
        image_bytes: Slika, prebrana iz datoteke (npr. z `request.read()`).

    Returns:
        NumPy array (1, 128) z embeddingom, ali None, če obraz ni bil najden.
    """
    # Zagotovi, da so model in ostali viri naloženi
    _initialize_resources()

    try:
        # Pretvori bajte v NumPy array, ki ga razume OpenCV
        nparr = np.frombuffer(image_bytes, np.uint8)
        img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img_bgr is None:
            print("OPOZORILO: Neveljavni bajti slike.")
            return None

        # Zaznaj in obreži obraz
        cropped_face = _detect_and_crop_face(img_bgr)
        if cropped_face is None:
            print("INFO: Obraz na sliki ni bil zaznan.")
            return None

        # Priprava za model (normalizacija in dodajanje batch dimenzije)
        img_normalized = cropped_face.astype(np.float32) / 255.0
        model_input = np.expand_dims(img_normalized, axis=0)

        # Generiranje in vrnitev embeddinga
        embedding = _model.predict(model_input)
        return embedding

    except Exception as e:
        print(f"Napaka med obdelavo slike: {e}")
        return None


# --- Primer uporabe (za testiranje) --->
if __name__ == '__main__':
    print("\n--- Testiranje funkcije get_embedding_from_image_bytes ---")

    # Pot do testne slike (prilagodi po potrebi)
    test_image_path = os.path.join(PROJECT_ROOT, 'test', 'Tomi_Cigula1.png')

    if not os.path.exists(test_image_path):
        print(f"Testna slika '{test_image_path}' ne obstaja. Testiranje ni mogoče.")
    else:
        print(f"Nalaganje testne slike: {test_image_path}")

        # Preberemo sliko kot bajte, tako kot bi jo prejel API
        with open(test_image_path, 'rb') as f:
            image_bytes_content = f.read()

        # Kličemo glavno funkcijo
        embedding_vector = get_embedding_from_image_bytes(image_bytes_content)

        if embedding_vector is not None:
            print("\nUspešno pridobljen embedding!")
            print(f"  - Oblika vektorja: {embedding_vector.shape}")
            print(f"  - Prvih 5 vrednosti: {embedding_vector[0, :5]}")
            # Preverimo normo, da se prepričamo o L2 normalizaciji
            norm = np.linalg.norm(embedding_vector)
            print(f"  - Dolžina (norma) vektorja: {norm:.4f} (mora biti blizu 1.0)")
        else:
            print("\nEmbeddinga ni bilo mogoče pridobiti (verjetno obraz ni bil zaznan).")