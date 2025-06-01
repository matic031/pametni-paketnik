import numpy as np
import os
import sys

# --- Osnovne nastavitve ---
PROJECT_DATA_DIR = os.path.join(os.getcwd(), 'data')  # Mapa, kjer so shranjeni .npz podatki


def load_complete_lfw_dataset(data_path, denoising_was_applied):  # Preimenovana funkcija
    """
    Naloži celoten pripravljen LFW dataset (augmentiran učni, originalni val/test)
    iz ene same .npz datoteke.
    """

    # Sestavi ime datoteke na podlagi informacije o odstranjevanju šuma
    denoise_suffix = f"_denoise-{str(denoising_was_applied).lower()}"
    # To je ime datoteke, ki jo je shranila augment_lfw_data.py in vsebuje VSE sete
    final_dataset_filename = f'lfw_final_dataset{denoise_suffix}.npz'
    final_dataset_filepath = os.path.join(data_path, final_dataset_filename)

    print(f"Poskušam naložiti celoten dataset iz: {final_dataset_filepath}")

    if not os.path.exists(final_dataset_filepath):
        print(f"NAPAKA: Datoteka '{final_dataset_filepath}' ne obstaja.")
        print("Prosim, preveri, ali sta skripti 'process_lfw_data.py' in 'augment_lfw_data.py' bili pravilno izvedeni,")
        print("in da 'augment_lfw_data.py' shrani vse sete v to datoteko.")
        return None, None, None, None, None, None

    try:
        data = np.load(final_dataset_filepath)

        # Preverimo, ali so vsi pričakovani ključi prisotni
        expected_keys = ['train_images', 'train_labels', 'val_images', 'val_labels', 'test_images', 'test_labels']
        if not all(key in data for key in expected_keys):
            print(f"NAPAKA: Vsi pričakovani ključi niso bili najdeni v '{final_dataset_filepath}'.")
            print(f"Najdeni ključi: {list(data.keys())}")
            print(f"Pričakovani ključi: {expected_keys}")
            return None, None, None, None, None, None

        train_images = data['train_images']  # To bi morali biti augmentirani učni podatki
        train_labels = data['train_labels']
        val_images = data['val_images']  # Originalni validacijski
        val_labels = data['val_labels']
        test_images = data['test_images']  # Originalni testni
        test_labels = data['test_labels']

        print("Podatkovne množice uspešno naložene:")
        print(f"  Učna množica (augmentirana): {train_images.shape[0]} slik, oblika slik: {train_images.shape[1:]}")
        print(f"  Validacijska množica: {val_images.shape[0]} slik, oblika slik: {val_images.shape[1:]}")
        print(f"  Testna množica: {test_images.shape[0]} slik, oblika slik: {test_images.shape[1:]}")

        return train_images, train_labels, val_images, val_labels, test_images, test_labels

    except Exception as e:
        print(f"NAPAKA pri nalaganju podatkov iz '{final_dataset_filepath}': {e}")
        return None, None, None, None, None, None


if __name__ == '__main__':

    # s podatki, ki so bili osnovani na predobdelavi z odstranjevanjem šuma ali brez.
    DENOISING_SETTING = True  # Nastavi na False, če želiš set brez predhodnega denoisinga

    print(f"Nalaganje končnega dataseta (osnova z odstranjevanjem šuma: {DENOISING_SETTING})...")

    loaded_data = load_complete_lfw_dataset(  # Kličemo novo, poenostavljeno funkcijo
        data_path=PROJECT_DATA_DIR,
        denoising_was_applied=DENOISING_SETTING
    )

    if loaded_data[0] is not None:  # Preveri, če je prva vrnjena vrednost (train_images) različna od None
        tr_img, tr_lbl, v_img, v_lbl, te_img, te_lbl = loaded_data

        print("\nPrimeri oblik naloženih podatkov:")
        print(f"  Train images shape: {tr_img.shape}")
        print(f"  Train labels shape: {tr_lbl.shape}")
        if v_img.size > 0:
            print(f"  Validation images shape: {v_img.shape}")
        else:
            print("  Validacijska množica je prazna ali ni bila naložena.")
        if te_img.size > 0:
            print(f"  Test images shape: {te_img.shape}")
        else:
            print("  Testna množica je prazna ali ni bila naložena.")

        print("\nPodatki so pripravljeni za uporabo.")
    else:
        print("\nNalaganje podatkov ni uspelo.")