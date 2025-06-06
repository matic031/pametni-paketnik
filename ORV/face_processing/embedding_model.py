from keras_facenet import FaceNet
import numpy as np
import cv2  # Za resize in barvno pretvorbo, če je potrebno

# Globalni inicializator za model, da se naloži samo enkrat
embedder_model = None
EXPECTED_EMBEDDING_SHAPE = (160, 160)  # FaceNet pričakuje 160x160 RGB


def initialize_embedding_model():
    global embedder_model
    if embedder_model is None:
        print("Initializing FaceNet embedding model...")
        try:
            embedder_model = FaceNet()
            print("FaceNet embedding model initialized.")
        except Exception as e:
            print(f"Error initializing FaceNet model: {e}")
            print("Make sure you have an internet connection for the first download,")
            print("and that TensorFlow/Keras is installed correctly.")
            embedder_model = None  # Označi, da inicializacija ni uspela


def get_face_embedding(face_image_rgb_01_160x160):
    """
    Pridobi embedding za dani izrezan obraz.
    :param face_image_rgb_01_160x160: NumPy array obraza (160x160, RGB, vrednosti [0,1] float32).
    :return: NumPy array embeddinga ali None, če pride do napake.
    """
    if embedder_model is None:
        initialize_embedding_model()
        if embedder_model is None:  # Če še vedno None, inicializacija ni uspela
            print("Error: Embedding model not available.")
            return None

    if not isinstance(face_image_rgb_01_160x160, np.ndarray):
        print("Error: Input to get_face_embedding is not a NumPy array.")
        return None

    if face_image_rgb_01_160x160.shape != EXPECTED_EMBEDDING_SHAPE + (3,):
        # raise ValueError(f"Input face image must be {EXPECTED_EMBEDDING_SHAPE} and RGB. Got {face_image_rgb_01_160x160.shape}")
        print(f"Warning: Input face image to get_face_embedding is {face_image_rgb_01_160x160.shape}, "
              f"expected {EXPECTED_EMBEDDING_SHAPE + (3,)}. Attempting resize.")
        # Poskusimo rešiti z resize, če je vhod napačne velikosti. To se ne bi smelo zgoditi,
        # če je augmentacijski cevovod pravilno uporabljen.
        face_image_rgb_01_160x160 = cv2.resize(face_image_rgb_01_160x160, EXPECTED_EMBEDDING_SHAPE,
                                               interpolation=cv2.INTER_AREA)

    # keras-facenet pričakuje vhod kot float32 in interno opravi standardizacijo (z-score).
    # Prepričajmo se, da je vhod res float32.
    if face_image_rgb_01_160x160.dtype != np.float32:
        face_image_rgb_01_160x160 = face_image_rgb_01_160x160.astype(np.float32)

    # FaceNet pričakuje batch slik.
    face_batch = np.expand_dims(face_image_rgb_01_160x160, axis=0)

    try:
        embeddings = embedder_model.embeddings(face_batch)
        print(f"DEBUG: Input shape to model: {face_batch.shape}")
        print(f"DEBUG: Embedding for this face (first 5 values): {embeddings[0][:5]}")
        return embeddings[0]  # Vrnemo embedding za prvo (in edino) sliko v batchu
    except Exception as e:
        print(f"Error during embedding extraction: {e}")
        # Možne napake: TensorFlow seje, napačen vhodni format kljub preverjanju.
        return None


# Ta funkcija ni več nujno potrebna, če augmentacijski cevovod že pripravi sliko pravilno.
# Vendar je lahko koristna za obdelavo slike za prijavo, ki ne gre skozi augmentacijo.
def preprocess_face_for_embedding(face_roi_bgr):
    """
    Pripravi izrezan obraz (iz detektorja) za ekstrakcijo embeddinga.
    To vključuje pretvorbo barv, resize in normalizacijo na [0,1].
    :param face_roi_bgr: Izrezan obraz iz detektorja (BGR, poljubne velikosti, vrednosti [0,255] uint8).
    :return: NumPy array obraza (160x160, RGB, vrednosti [0,1] float32) ali None.
    """
    if face_roi_bgr is None or face_roi_bgr.size == 0:
        print("Error: Input face_roi_bgr to preprocess_face_for_embedding is empty or None.")
        return None

    if face_roi_bgr.shape[0] == 0 or face_roi_bgr.shape[1] == 0:
        print(f"Error: face_roi_bgr has zero dimension {face_roi_bgr.shape}")
        return None

    # 1. Pretvori v RGB
    try:
        face_rgb = cv2.cvtColor(face_roi_bgr, cv2.COLOR_BGR2RGB)
    except cv2.error as e:
        print(
            f"OpenCV error during BGR2RGB conversion: {e}. ROI shape: {face_roi_bgr.shape}, dtype: {face_roi_bgr.dtype}")
        # To se lahko zgodi, če je face_roi_bgr že RGB ali sivinski, ali pa poškodovan
        if len(face_roi_bgr.shape) == 2:  # Sivinska
            face_rgb = cv2.cvtColor(face_roi_bgr, cv2.COLOR_GRAY2RGB)
        elif len(face_roi_bgr.shape) == 3 and face_roi_bgr.shape[2] == 3:
            face_rgb = face_roi_bgr  # Predpostavimo, da je že RGB, če pride do napake
        else:
            return None  # Neznan format

    # 2. Resize na pričakovano velikost modela (npr. 160x160 za FaceNet)
    face_resized = cv2.resize(face_rgb, EXPECTED_EMBEDDING_SHAPE, interpolation=cv2.INTER_AREA)

    # 3. Normaliziraj vrednosti pikslov na [0, 1] in pretvori v float32
    face_normalized_01 = face_resized.astype(np.float32) / 255.0

    return face_normalized_01