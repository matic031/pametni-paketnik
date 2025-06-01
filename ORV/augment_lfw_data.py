import numpy as np
import cv2  # OpenCV za slikovne operacije
import os
import matplotlib.pyplot as plt
import random  # Za nekatere naključne odločitve pri augmentaciji
import sys

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


if __name__ == '__main__':
    # 1. Nalaganje predobdelanih podatkov
    processed_data_path = os.path.join(PROJECT_DATA_DIR, PROCESSED_DATA_FILENAME)

    if not os.path.exists(processed_data_path):
        print(f"NAPAKA: Datoteka s predobdelanimi podatki '{processed_data_path}' ne obstaja.")
        print("Prosim, najprej zaženi skripto 'process_lfw_data.py'.")
        sys.exit()  # Uporabi sys.exit() za izhod iz skripte

    print(f"Nalaganje predobdelanih podatkov iz: {processed_data_path}")
    data = np.load(processed_data_path)
    train_images = data['train_images']  # Slike so že normalizirane float32 [0,1]
    train_labels = data['train_labels']


    print(f"Učna množica naložena: {train_images.shape[0]} slik.")

    if train_images.size == 0:
        print("Učna množica je prazna. Augmentacija ni mogoča.")
        sys.exit()

    # 2. Priprava za augmentacijo
    augmented_images_list = []
    augmented_labels_list = []

    # vsako sliko augmetiramo samo enkrat.

    print(f"\nZačenjam augmentacijo na {train_images.shape[0]} učnih slikah...")

    for i in range(train_images.shape[0]):
        original_image = train_images[i]
        original_label = train_labels[i]

        # Dodaj originalno sliko in oznako na seznam
        augmented_images_list.append(original_image)
        augmented_labels_list.append(original_label)

        # Izberi naključno eno od naših augmentacij za to sliko
        # ali pa uporabi sekvenco/kombinacijo.

        choice = random.randint(1, 5)  # Če imamo 5 augmentacij

        augmented_image_single = None

        if choice == 1:
            # Horizontalni flip
            augmented_image_single = custom_horizontal_flip(original_image.copy())
        elif choice == 2:
            # Sprememba svetlosti
            factor = random.uniform(0.7, 1.3)  # Naključni faktor med 0.7 in 1.3
            augmented_image_single = custom_adjust_brightness(original_image.copy(), factor)
        elif choice == 3:
            # Manjša rotacija (npr. med -15 in +15 stopinj)
            angle = random.uniform(-15, 15)
            augmented_image_single = custom_rotate_image(original_image.copy(), angle)
        elif choice == 4:
            # Dodajanje Gaussovega šuma
            std = random.uniform(0.01, 0.08)  # Manjši std_dev za manj opazen šum
            augmented_image_single = custom_add_gaussian_noise(original_image.copy(), std_dev=std)
        elif choice == 5:
            # Sprememba kontrasta
            factor = random.uniform(0.6, 1.4)
            augmented_image_single = custom_adjust_contrast(original_image.copy(), factor)

        if augmented_image_single is not None:
            augmented_images_list.append(augmented_image_single)
            augmented_labels_list.append(original_label)  # Oznaka ostane ista

        if (i + 1) % 500 == 0:
            print(
                f"  Augmentiranih {i + 1} originalnih slik (trenutno {len(augmented_images_list)} slik v novem setu)...")

    augmented_train_images = np.array(augmented_images_list)
    augmented_train_labels = np.array(augmented_labels_list)

    print(f"\nKončano augmentiranje. Originalni učni set: {train_images.shape[0]} slik.")
    print(f"Novi (augmentirani) učni set: {augmented_train_images.shape[0]} slik.")

    #  Prikaz nekaj primerov. Slike augmentiramo z vsemi funkcijami za prikaz rezultatov.
    if augmented_train_images.shape[0] > train_images.shape[0]:  # Če smo dejansko kaj dodali
        num_to_show = 5
        random_indices = np.random.choice(train_images.shape[0], num_to_show, replace=False)

        for original_idx in random_indices:
            # Najdi originalno sliko
            original_display_img = train_images[original_idx]

            # Za boljši prikaz:
            display_idx_orig = original_idx  # Indeks originala v train_images

            # Izvedemo nekaj augmentacij na tem specifičnem originalu za prikaz
            aug_list_display = []
            aug_titles_display = []

            aug_list_display.append(custom_horizontal_flip(original_display_img.copy()))
            aug_titles_display.append("Flip")

            aug_list_display.append(custom_adjust_brightness(original_display_img.copy(), 1.2))
            aug_titles_display.append("Svetlost (1.2)")

            aug_list_display.append(custom_rotate_image(original_display_img.copy(), 10))
            aug_titles_display.append("Rotacija (10d)")

            aug_list_display.append(custom_add_gaussian_noise(original_display_img.copy(), std_dev=0.05))
            aug_titles_display.append("Gaussov šum")

            label_display = train_labels[display_idx_orig].decode('utf-8', errors='ignore')
            display_original_and_augmented(original_display_img, aug_list_display, aug_titles_display,
                                           main_title=f"Augmentacije za: {label_display[:20]}")
            if num_to_show == 0: break  # En primer za prikaz
            num_to_show -= 1

    #Shranjevanje augmentiranega učnega nabora
    augmented_output_path = os.path.join(PROJECT_DATA_DIR, AUGMENTED_DATA_FILENAME)
    np.savez_compressed(augmented_output_path,
                        train_images_aug=augmented_train_images,
                        train_labels_aug=augmented_train_labels)
    print(f"\nAugmentiran učni nabor shranjen v: {augmented_output_path}")