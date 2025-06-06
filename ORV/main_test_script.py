import cv2
import numpy as np
import os
import shutil

# Uvozi funkcije iz tvojih modulov
from face_processing.detection import detect_face
from face_processing.augmentation import generate_augmented_faces, IMG_SIZE_FOR_EMBEDDING
from face_processing.embedding_model import initialize_embedding_model, get_face_embedding, \
    preprocess_face_for_embedding
from user_management.db import (
    register_user_embeddings,
    verify_user_by_embedding,
    is_user_registered,
    delete_user,
    VERIFICATION_THRESHOLD,
    _load_embeddings_from_file  # Za ponovno nalaganje, če je potrebno
)

# Inicializiraj embedding model ob zagonu skripte
initialize_embedding_model()

# Direktorij za testne slike
TEST_IMAGE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_images")
os.makedirs(TEST_IMAGE_DIR, exist_ok=True)


def _get_image_path(filename):
    return os.path.join(TEST_IMAGE_DIR, filename)


def create_dummy_image_if_not_exists(image_path, text="Dummy"):
    """Ustvari preprosto sliko, če ne obstaja, za lažje testiranje."""
    if not os.path.exists(image_path):
        print(f"Creating dummy image: {image_path}")
        dummy_img = np.zeros((200, 200, 3), dtype=np.uint8)
        cv2.putText(dummy_img, text, (30, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.imwrite(image_path, dummy_img)
        return True
    return False


def register_user_from_image(image_filename, user_id, num_augmentations=10):
    """Registrira uporabnika na podlagi ene slike."""
    print(f"\n--- Attempting to register user '{user_id}' from '{image_filename}' ---")
    image_path = _get_image_path(image_filename)
    if not os.path.exists(image_path):
        print(f"Image not found: {image_path}. Cannot register.")
        return False

    original_image_bgr = cv2.imread(image_path)
    if original_image_bgr is None:
        print(f"Could not read image: {image_path}")
        return False

    face_roi_bgr, _ = detect_face(original_image_bgr)
    if face_roi_bgr is None:
        print(f"No face detected in {image_filename} for user {user_id}.")
        return False

    print(f"Face detected for {user_id}. ROI shape: {face_roi_bgr.shape}. Augmenting...")

    # Pripravi obraz za augmentacijo: RGB, normaliziran na [0,1]
    face_roi_rgb = cv2.cvtColor(face_roi_bgr, cv2.COLOR_BGR2RGB)
    face_roi_rgb_normalized = face_roi_rgb.astype(np.float32) / 255.0

    augmented_face_images_rgb_01_160x160 = generate_augmented_faces(
        face_roi_rgb_normalized,
        num_augmentations=num_augmentations
    )

    if not augmented_face_images_rgb_01_160x160:
        print(f"No augmented faces generated for {user_id}.")
        return False

    print(
        f"Generated {len(augmented_face_images_rgb_01_160x160)} face versions for {user_id}. Extracting embeddings...")

    user_face_embeddings = []
    for i, aug_face_np in enumerate(augmented_face_images_rgb_01_160x160):
        # `generate_augmented_faces` bi moral vrniti slike v pravilnem formatu (160x160, RGB, [0,1])
        embedding = get_face_embedding(aug_face_np)
        if embedding is not None:
            user_face_embeddings.append(embedding)
        else:
            print(f"  Warning: Could not get embedding for augmented face {i + 1} for user {user_id}")

    if not user_face_embeddings:
        print(f"Could not generate any embeddings for user {user_id} from {image_filename}")
        return False

    register_user_embeddings(user_id, user_face_embeddings)
    return True


def login_user_with_image(image_filename, user_id_to_verify):
    """Poskusi prijaviti uporabnika s sliko."""
    print(f"\n--- Attempting to login user '{user_id_to_verify}' with image '{image_filename}' ---")
    image_path = _get_image_path(image_filename)

    if not is_user_registered(user_id_to_verify):
        print(f"User '{user_id_to_verify}' is not registered. Cannot verify.")
        return False, 0.0

    if not os.path.exists(image_path):
        print(f"Login image not found: {image_path}. Cannot verify.")
        return False, 0.0

    login_image_bgr = cv2.imread(image_path)
    if login_image_bgr is None:
        print(f"Could not read login image: {image_path}")
        return False, 0.0

    face_roi_bgr, _ = detect_face(login_image_bgr)
    if face_roi_bgr is None:
        print(f"No face detected in login image {image_filename} for user {user_id_to_verify}.")
        return False, 0.0

    print(f"Face detected in login image. ROI shape: {face_roi_bgr.shape}. Preprocessing for embedding...")

    # Pripravi obraz za ekstrakcijo embeddinga (BGR [0,255] -> RGB [0,1] 160x160)
    query_face_processed_rgb_01_160x160 = preprocess_face_for_embedding(face_roi_bgr)
    if query_face_processed_rgb_01_160x160 is None:
        print(f"Could not preprocess face from login image for {user_id_to_verify}.")
        return False, 0.0

    query_embedding = get_face_embedding(query_face_processed_rgb_01_160x160)
    if query_embedding is None:
        print(f"Could not extract embedding from login image for {user_id_to_verify}.")
        return False, 0.0

    is_verified, similarity = verify_user_by_embedding(user_id_to_verify, query_embedding)

    result_text = "VERIFIED" if is_verified else "NOT VERIFIED"
    print(
        f"Login result for '{user_id_to_verify}': {result_text}. Similarity: {similarity:.4f} (Threshold: {VERIFICATION_THRESHOLD})")
    return is_verified, similarity


if __name__ == "__main__":
    print("Starting Face Authentication Test Script...")
    print(f"Using FaceNet model for embeddings (expects {IMG_SIZE_FOR_EMBEDDING}x{IMG_SIZE_FOR_EMBEDDING} RGB images).")
    print(f"Verification threshold set to: {VERIFICATION_THRESHOLD}")

    # Počisti prejšnje registracije za čist začetek testa
    if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data_storage", "user_embeddings.json")):
        os.remove(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data_storage", "user_embeddings.json"))
        print("Cleared previous user embeddings.")
    _load_embeddings_from_file()  # Ponovno naloži (prazno) stanje

    # Pripravi testne slike (ustvari dummy, če ne obstajajo)
    # ZAMENJAJ 'userA_reg.jpg' itd. z dejanskimi imeni tvojih slik!
    # Priporočam slike resničnih oseb za boljši test.
    user_a_reg_file = "Tomi_Cigula1.png"
    user_a_login_file = "Tomi_Cigula8.png"  # Slika iste osebe A, drugačna slika/poza
    user_b_reg_file = "Aaron_Peirsol_0001.jpg"
    user_b_login_file = "Aaron_Peirsol_0002.jpg"  # Slika osebe B

    create_dummy_image_if_not_exists(_get_image_path(user_a_reg_file), "User A Reg")
    create_dummy_image_if_not_exists(_get_image_path(user_a_login_file), "User A Login")
    create_dummy_image_if_not_exists(_get_image_path(user_b_reg_file), "User B Reg")
    create_dummy_image_if_not_exists(_get_image_path(user_b_login_file), "User B Login")

    # --- Scenarij 1: Registracija uporabnikov ---
    register_user_from_image(user_a_reg_file, "userA")
    register_user_from_image(user_b_reg_file, "userB")

    # --- Scenarij 2: Pravilna prijava ---
    login_user_with_image(user_a_login_file, "userA")
    login_user_with_image(user_b_login_file, "userB")

    # --- Scenarij 3: Napačna prijava (imposter) ---
    # Uporabnik B se poskusi prijaviti kot uporabnik A
    login_user_with_image(user_b_login_file, "userA")
    # Uporabnik A se poskusi prijaviti kot uporabnik B
    login_user_with_image(user_a_login_file, "userB")

    # --- Scenarij 4: Prijava neregistriranega uporabnika ---
    login_user_with_image(user_a_login_file, "userC_not_registered")

    # --- Scenarij 5: Brisanje uporabnika in poskus prijave ---
    print("\n--- Deleting User A ---")
    delete_user("userA")
    login_user_with_image(user_a_login_file, "userA")  # Poskus prijave po brisanju

    print("\nTest script finished.")