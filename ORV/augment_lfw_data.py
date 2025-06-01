import numpy as np
import cv2  # OpenCV za slikovne operacije
import os
import matplotlib.pyplot as plt
import random  # Za nekatere naključne odločitve pri augmentaciji
import sys
import argparse

# --- Osnovne nastavitve ---
PROJECT_DATA_DIR = os.path.join(os.getcwd(), 'data')  # Mapa, kjer so shranjeni .npz podatki
# Nastavimo katero datoteko s predobdelanimi podatki bomo uporabljali
#PROCESSED_DATA_FILENAME = 'lfw_processed_splits_denoise-true.npz'
PROCESSED_DATA_FILENAME = 'lfw_processed_splits_denoise-false.npz'
AUGMENTED_DATA_FILENAME = 'lfw_augmented_train_set.npz'  # Ime za shranjevanje augmentiranih podatkov

# Ciljne dimenzije slik
TARGET_IMG_HEIGHT = 64
TARGET_IMG_WIDTH = 64


# Augmentacijske funkcije

# 1. Horizontalni Flip (Zrcaljenje)
def custom_horizontal_flip(image):
    """Ročno implementiran horizontalni flip slike."""
    # image je NumPy array oblike (H, W, C)
    return image[:, ::-1, :]  # Obrne vrstni red stolpcev za vsak kanal


# 2. Sprememba Svetlosti
def custom_adjust_brightness(image, brightness_factor):
    """Ročno implementirana sprememba svetlosti.
    brightness_factor: > 1.0 za svetlejšo, < 1.0 za temnejšo.
    """
# Spremeni svetlost slike gledena faktor, omeji vrednosti (noramalizira) [0.0, 1.0]
    augmented_image = image * brightness_factor
    return np.clip(augmented_image, 0.0, 1.0)  # Omeji vrednosti na [0.0, 1.0]


# 3. Manjša Rotacija
def custom_rotate_image(image, angle_deg):
    """Ročno implementirana rotacija slike za podan kot (v stopinjah).
       Ohrani originalne dimenzije, robovi so lahko črni.
    """
    # image je NumPy array (H, W, C), normaliziran na [0,1]
    img_uint8 = (image * 255).astype(np.uint8)  # Pretvorba nazaj v uint8

    height, width = img_uint8.shape[:2]
    center_x, center_y = width // 2, height // 2

    # Dobimo rotacijsko matriko
    rotation_matrix = cv2.getRotationMatrix2D((center_x, center_y), angle_deg, 1.0)  # 1.0 je faktor skaliranja

    # Izvedemo afino transformacijo (rotacijo)
    # cv2.BORDER_CONSTANT z value=(0,0,0) zapolni robove s črno
    rotated_img_uint8 = cv2.warpAffine(img_uint8, rotation_matrix, (width, height),
                                       flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))

    return rotated_img_uint8.astype(np.float32) / 255.0  # Nazaj v float32 [0,1]


# 4. Dodajanje Gaussovega Šuma
def custom_add_gaussian_noise(image, mean=0.0, std_dev=0.05):
    """Ročno implementirano dodajanje Gaussovega šuma.
       std_dev je relativno na obseg slike [0,1].
    """
    # image je NumPy array (H, W, C), normaliziran na [0,1]
    noise = np.random.normal(mean, std_dev, image.shape).astype(np.float32)
    noisy_image = image + noise
    return np.clip(noisy_image, 0.0, 1.0)  # Omeji vrednosti


# 5. Kontrast (dodatna, če želiš več kot 4)
def custom_adjust_contrast(image, contrast_factor):
    """Ročno implementirana sprememba kontrasta.
       contrast_factor > 1.0 za večji kontrast.
       Slika mora biti normalizirana na [0,1].
    """
    # f(x) = factor * (x - 0.5) + 0.5  (0.5 je srednja vrednost sivin/barv)
    augmented_image = contrast_factor * (image - 0.5) + 0.5
    return np.clip(augmented_image, 0.0, 1.0)


# Funkcija za prikaz originalne in augmentirane slike
def display_original_and_augmented(original, augmented_list, aug_titles, main_title="Primeri Augmentacij"):
    """Prikaže originalno sliko in seznam njenih augmentiranih različic."""
    num_augmented = len(augmented_list)
    if num_augmented == 0:
        print("Ni augmentiranih slik za prikaz.")
        return

    plt.figure(figsize=(3 * (num_augmented + 1), 4))  # Prilagodi velikost glede na število slik
    plt.suptitle(main_title, fontsize=16)

    # Prikaz originala
    plt.subplot(1, num_augmented + 1, 1)
    plt.imshow(original)
    plt.title("Original")
    plt.axis('off')

    # Prikaz augmentiranih
    for i, (aug_img, title) in enumerate(zip(augmented_list, aug_titles)):
        plt.subplot(1, num_augmented + 1, i + 2)
        plt.imshow(aug_img)
        plt.title(title)
        plt.axis('off')

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.show()


def run_augmentation(base_denoised_setting):
        """
        Naloži predobdelan učni set, izvede augmentacijo in shrani rezultate.
        Prav tako shrani originalne validacijske in testne sete skupaj z augmentiranim učnim setom.
        """
        denoise_suffix_for_input = f"_denoise-{str(base_denoised_setting).lower()}"
        processed_data_filename = f'lfw_processed_splits{denoise_suffix_for_input}.npz'
        processed_data_path = os.path.join(PROJECT_DATA_DIR, processed_data_filename)

        if not os.path.exists(processed_data_path):
            print(f"NAPAKA: Datoteka s predobdelanimi podatki '{processed_data_path}' ne obstaja.")
            print("Prosim, najprej zaženi skripto 'process_lfw_data.py' s pravilno nastavitvijo za denoising.")
            return False  # Vrne False za neuspeh

        print(f"Nalaganje predobdelanih podatkov iz: {processed_data_path}")
        data = np.load(processed_data_path)
        train_images_orig = data['train_images']
        train_labels_orig = data['train_labels']
        # Naložimo tudi val in test sete, da jih shranimo skupaj z augmentiranim train setom
        val_images = data['val_images']
        val_labels = data['val_labels']
        test_images = data['test_images']
        test_labels = data['test_labels']

        print(f"Učna množica (original) naložena: {train_images_orig.shape[0]} slik.")

        if train_images_orig.size == 0:
            print("Učna množica je prazna. Augmentacija ni mogoča.")
            return False

        augmented_images_list = []
        augmented_labels_list = []

        print(f"\nZačenjam augmentacijo na {train_images_orig.shape[0]} učnih slikah...")

        for i in range(train_images_orig.shape[0]):
            original_image = train_images_orig[i]
            original_label = train_labels_orig[i]

            augmented_images_list.append(original_image)
            augmented_labels_list.append(original_label)

            choice = random.randint(1, 5)
            augmented_image_single = None

            if choice == 1:
                augmented_image_single = custom_horizontal_flip(original_image.copy())
            elif choice == 2:
                factor = random.uniform(0.7, 1.3)
                augmented_image_single = custom_adjust_brightness(original_image.copy(), factor)
            elif choice == 3:
                angle = random.uniform(-15, 15)
                augmented_image_single = custom_rotate_image(original_image.copy(), angle)
            elif choice == 4:
                std = random.uniform(0.01, 0.08)
                augmented_image_single = custom_add_gaussian_noise(original_image.copy(), std_dev=std)
            elif choice == 5:
                factor = random.uniform(0.6, 1.4)
                augmented_image_single = custom_adjust_contrast(original_image.copy(), factor)

            if augmented_image_single is not None:
                augmented_images_list.append(augmented_image_single)
                augmented_labels_list.append(original_label)

            if (i + 1) % 500 == 0:
                print(
                    f"  Augmentiranih {i + 1} originalnih slik (trenutno {len(augmented_images_list)} slik v novem setu)...")

        train_images_aug = np.array(augmented_images_list)
        train_labels_aug = np.array(augmented_labels_list)

        print(f"\nKončano augmentiranje. Originalni učni set: {train_images_orig.shape[0]} slik.")
        print(f"Novi (augmentirani) učni set: {train_images_aug.shape[0]} slik.")

        if train_images_orig.shape[0] > 0:  # Preverimo, če originalni train set ni prazen
            num_to_show = min(3, train_images_orig.shape[0])  # Pokaži manj, če je set majhen
            if num_to_show > 0:
                random_indices = np.random.choice(train_images_orig.shape[0], num_to_show, replace=False)
                for original_idx in random_indices:
                    original_display_img = train_images_orig[original_idx]
                    aug_list_display = [
                        custom_horizontal_flip(original_display_img.copy()),
                        custom_adjust_brightness(original_display_img.copy(), 1.2),
                        custom_rotate_image(original_display_img.copy(), 10),
                        custom_add_gaussian_noise(original_display_img.copy(), std_dev=0.05)
                    ]
                    aug_titles_display = ["Flip", "Svetlost (1.2)", "Rotacija (10d)", "Gaussov šum"]
                    label_display = train_labels_orig[original_idx].decode('utf-8', errors='ignore')
                    display_original_and_augmented(original_display_img, aug_list_display, aug_titles_display,
                                                   main_title=f"Augmentacije za: {label_display[:20]}")

        # Shranjevanje augmentiranega učnega nabora SKUPAJ z originalnimi val in test seti
        denoise_suffix_for_output = f"_denoise-{str(base_denoised_setting).lower()}"
        final_output_filename = f'lfw_final_dataset{denoise_suffix_for_output}.npz'  # Ime, ki ga pričakuje load_final...
        final_output_path = os.path.join(PROJECT_DATA_DIR, final_output_filename)

        if train_images_aug.size > 0:
            np.savez_compressed(final_output_path,
                                train_images=train_images_aug, train_labels=train_labels_aug,
                                val_images=val_images, val_labels=val_labels,
                                test_images=test_images, test_labels=test_labels)
            print(f"\nKončni dataset (z augmentirano učno množico) shranjen v: {final_output_path}")
            return True  # Vrne True za uspeh
        else:
            print("\nAugmentirana učna množica je prazna, podatki niso bili shranjeni.")
            return False


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Augmentacija LFW učnega dataseta.")
    parser.add_argument(
        '--base_denoised',
        action='store_true',  # Če je podan --base_denoised, bo vrednost True
        help="Označuje, da je bil osnovni dataset (iz katerega se augmentira) obdelan z odstranjevanjem šuma."
    )
    args = parser.parse_args()

    DENOISING_SETTING_FOR_INPUT_MAIN = args.base_denoised  # Vrednost iz argumenta
    print(f"Augmentacija se bo izvedla na osnovi dataseta z denoising={DENOISING_SETTING_FOR_INPUT_MAIN}")



    run_augmentation(base_denoised_setting=DENOISING_SETTING_FOR_INPUT_MAIN)
