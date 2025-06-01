import numpy as np
import os
import sys

# --- Osnovne nastavitve ---
PROJECT_DATA_DIR = os.path.join(os.getcwd(), 'data')


# Imena datotek, kot jih shranjujeta prejšnji dve skripti
# AUGMENTED_TRAIN_FILENAME_BASE = 'lfw_augmented_train_set' # Osnova imena za augmentirane
# PROCESSED_SPLITS_FILENAME_BASE = 'lfw_processed_splits'   # Osnova imena za originalne delitve

def load_final_lfw_dataset_from_separate_files(data_path,
                                               denoising_setting_for_val_test,
                                               denoising_setting_for_augmented_train):  # NOVO: ločena nastavitev za train
    """
    Naloži augmentiran učni set iz ene datoteke ter originalni
    validacijski in testni set iz druge .npz datoteke.
    """

    # Sestavi ime datoteke za originalne delitve (val/test)
    denoise_suffix_val_test = f"_denoise-{str(denoising_setting_for_val_test).lower()}"
    processed_splits_filename = f'lfw_processed_splits{denoise_suffix_val_test}.npz'
    processed_splits_filepath = os.path.join(data_path, processed_splits_filename)

    denoise_suffix_train_aug = f"_denoise-{str(denoising_setting_for_augmented_train).lower()}"

    augmented_train_filename = f'lfw_final_dataset{denoise_suffix_train_aug}.npz'

    augmented_train_filename_actual = f'lfw_augmented_train_set.npz'


    augmented_train_filepath = os.path.join(data_path,
                                            'lfw_augmented_train_set.npz')  # Fiksno ime, kot je bilo v augment_lfw_data.py

    print(f"Poskušam naložiti augmentiran učni set iz: {augmented_train_filepath}")
    print(f"Poskušam naložiti validacijski/testni set iz: {processed_splits_filepath}")

    train_images, train_labels = None, None
    val_images, val_labels, test_images, test_labels = None, None, None, None

    # 1. Nalaganje augmentiranega učnega seta
    if not os.path.exists(augmented_train_filepath):
        print(f"NAPAKA: Datoteka z augmentiranim učnim setom '{augmented_train_filepath}' ne obstaja.")
        return None, None, None, None, None, None
    try:
        aug_data = np.load(augmented_train_filepath)
        train_images = aug_data['train_images_aug']  # Ključi iz augment_lfw_data.py
        train_labels = aug_data['train_labels_aug']
        print(f"  Augmentiran učni set naložen: {train_images.shape[0]} slik.")
    except Exception as e:
        print(f"NAPAKA pri nalaganju augmentiranega učnega seta iz '{augmented_train_filepath}': {e}")
        return None, None, None, None, None, None

    # 2. Nalaganje validacijskega in testnega seta
    if not os.path.exists(processed_splits_filepath):
        print(f"NAPAKA: Datoteka z originalnimi delitvami '{processed_splits_filepath}' ne obstaja.")
        return None, None, None, None, None, None
    try:
        split_data_content = np.load(processed_splits_filepath)
        val_images = split_data_content['val_images']
        val_labels = split_data_content['val_labels']
        test_images = split_data_content['test_images']
        test_labels = split_data_content['test_labels']
        print(f"  Validacijski set naložen: {val_images.shape[0]} slik.")
        print(f"  Testni set naložen: {test_images.shape[0]} slik.")
    except Exception as e:
        print(f"NAPAKA pri nalaganju validacijskega/testnega seta iz '{processed_splits_filepath}': {e}")
        return None, None, None, None, None, None

    return train_images, train_labels, val_images, val_labels, test_images, test_labels



if __name__ == '__main__':

    DENOISING_USED_FOR_BASE_PROCESSING = True

    print(f"Nalaganje podatkov (osnovna predobdelava z odstranjevanjem šuma: {DENOISING_USED_FOR_BASE_PROCESSING})...")

    loaded_data = load_final_lfw_dataset_from_separate_files(
        data_path=PROJECT_DATA_DIR,
        denoising_setting_for_val_test=DENOISING_USED_FOR_BASE_PROCESSING,
        denoising_setting_for_augmented_train=DENOISING_USED_FOR_BASE_PROCESSING
        # Predpostavimo, da je augmentacija temeljila na istem
    )

    if loaded_data[0] is not None:
        tr_img, tr_lbl, v_img, v_lbl, te_img, te_lbl = loaded_data

        print("\nPrimeri oblik naloženih podatkov:")
        print(f"  Train images shape: {tr_img.shape}")
        print(f"  Train labels shape: {tr_lbl.shape}")
        if v_img.size > 0: print(f"  Validation images shape: {v_img.shape}")
        if te_img.size > 0: print(f"  Test images shape: {te_img.shape}")

        print("\nPodatki so pripravljeni za uporabo ")
    else:
        print("\nNalaganje podatkov ni uspelo.")