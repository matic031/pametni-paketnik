import numpy as np
import json
import os
from sklearn.metrics.pairwise import cosine_similarity

# Pot do datoteke za shranjevanje
# Pravilna pot glede na strukturo projekta: ../data_storage/
script_dir = os.path.dirname(os.path.abspath(__file__))
DATA_STORAGE_DIR = os.path.join(script_dir, '..', 'data_storage')
USER_DATA_FILE = os.path.join(DATA_STORAGE_DIR, 'user_embeddings.json')

# Zagotovi, da direktorij data_storage obstaja
os.makedirs(DATA_STORAGE_DIR, exist_ok=True)

user_embeddings_store_cache = {}  # Cache v pomnilniku
VERIFICATION_THRESHOLD = 0.65  # Prag za kosinusno podobnost (začni s tem, prilagajaj!)


def _load_embeddings_from_file():
    global user_embeddings_store_cache
    if os.path.exists(USER_DATA_FILE):
        try:
            with open(USER_DATA_FILE, 'r') as f:
                data_from_file = json.load(f)
                user_embeddings_store_cache = {
                    user_id: [np.array(emb, dtype=np.float32) for emb in embeddings_list]
                    for user_id, embeddings_list in data_from_file.items()

                }
            print(f"Loaded {len(user_embeddings_store_cache)} users from {USER_DATA_FILE}")
        except Exception as e:
            print(f"Could not load embeddings from file: {e}. Starting with an empty store.")
            user_embeddings_store_cache = {}
    else:
        print(f"Embeddings file {USER_DATA_FILE} not found. Starting with an empty store.")
        user_embeddings_store_cache = {}


def _save_embeddings_to_file():
    # Pretvorimo NumPy arraye v sezname za JSON serializacijo
    data_to_save = {
        user_id: [emb.tolist() for emb in embeddings_list]
        for user_id, embeddings_list in user_embeddings_store_cache.items()
    }
    try:
        with open(USER_DATA_FILE, 'w') as f:
            json.dump(data_to_save, f, indent=4)
        print(f"Saved embeddings to {USER_DATA_FILE}")
    except Exception as e:
        print(f"Error saving embeddings to file: {e}")


# Naloži ob zagonu modula
_load_embeddings_from_file()


def register_user_embeddings(user_id, embeddings_list):
    """Shrani/posodobi seznam embeddingov za uporabnika."""
    if not all(isinstance(e, np.ndarray) for e in embeddings_list):
        raise ValueError("All embeddings in the list must be NumPy arrays.")
    user_embeddings_store_cache[user_id] = embeddings_list
    _save_embeddings_to_file()
    print(f"Registered/updated embeddings for user: {user_id} with {len(embeddings_list)} embeddings.")


def get_user_embeddings(user_id):
    """Pridobi shranjene embeddinge za uporabnika."""
    return user_embeddings_store_cache.get(user_id, [])


def verify_user_by_embedding(user_id_to_verify, query_embedding_np):
    """
    Preveri, ali dani query_embedding pripada uporabniku.
    :return: (bool, float) - (Ali je verifikacija uspešna, najvišja dosežena podobnost)
    """
    stored_embeddings = get_user_embeddings(user_id_to_verify)
    if not stored_embeddings:
        print(f"No embeddings found for user: {user_id_to_verify}. Cannot verify.")
        return False, 0.0

    if not isinstance(query_embedding_np, np.ndarray):
        print("Error: query_embedding must be a NumPy array.")
        return False, 0.0

    query_embedding_np = query_embedding_np.reshape(1, -1)  # Zahtevana oblika za cosine_similarity

    max_similarity = -1.0  # Začni z negativno vrednostjo, ker je kosinusna podobnost lahko negativna
    for ref_embedding_np in stored_embeddings:
        ref_embedding_np = ref_embedding_np.reshape(1, -1)
        print(f"DEBUG: Verifying {user_id_to_verify}")
        print(f"DEBUG: Query embedding (first 5): {query_embedding_np[0][:5]}")
        if stored_embeddings:
            print(f"DEBUG: Ref embedding 0 for {user_id_to_verify} (first 5): {stored_embeddings[0][:5]}")
        try:
            similarity = cosine_similarity(query_embedding_np, ref_embedding_np)[0][0]
            if similarity > max_similarity:
                max_similarity = similarity
        except Exception as e:
            print(f"Error calculating similarity: {e}")
            # To se lahko zgodi, če so embeddingi poškodovani ali napačne oblike
            continue  # Preskoči ta embedding

    print(
        f"Verification for {user_id_to_verify}: Max similarity = {max_similarity:.4f}, Threshold = {VERIFICATION_THRESHOLD}")
    if max_similarity >= VERIFICATION_THRESHOLD:
        return True, max_similarity
    else:
        return False, max_similarity


def is_user_registered(user_id):
    return user_id in user_embeddings_store_cache


def delete_user(user_id):
    if user_id in user_embeddings_store_cache:
        del user_embeddings_store_cache[user_id]
        _save_embeddings_to_file()
        print(f"Deleted user {user_id} from store.")
        return True
    print(f"User {user_id} not found for deletion.")
    return False