# augment_lfw_data.py
import numpy as np
import cv2
import os
import matplotlib.pyplot as plt
import random
import argparse
import albumentations as A

# --- Osnovne nastavitve ---
PROJECT_DATA_DIR = os.path.join(os.getcwd(), 'data')
TARGET_IMG_HEIGHT = 64
TARGET_IMG_WIDTH = 64


# --- Ročno napisane Augmentacijske Funkcije (4 zahtevane) ---

def custom_horizontal_flip(image):
    """Ročno implementiran horizontalni flip."""
    return image[:, ::-1, :]


def custom_adjust_brightness(image, brightness_factor):
    """Ročno implementirana sprememba svetlosti."""
    augmented_image = image * brightness_factor
    return np.clip(augmented_image, 0.0, 1.0)


def custom_rotate_image(image, angle_deg):
    """Ročno implementirana rotacija slike."""
    height, width = image.shape[:2]
    center = (width // 2, height // 2)
    rotation_matrix = cv2.getRotationMatrix2D(center, angle_deg, 1.0)
    rotated_img = cv2.warpAffine(image, rotation_matrix, (width, height), flags=cv2.INTER_LINEAR,
                                 borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))
    return rotated_img


def custom_add_gaussian_noise(image, mean=0.0, std_dev=0.05):
    """Ročno implementirano dodajanje Gaussovega šuma."""
    noise = np.random.normal(mean, std_dev, image.shape).astype(np.float32)
    noisy_image = image + noise
    return np.clip(noisy_image, 0.0, 1.0)


# --- Albumentations Augmentacijski Cevovod ---

def random_small_occlusion(image, **kwargs):
    """
    Lambda funkcija za Albumentations: na sliko doda majhen črn pravokotnik (okluzija).
    """
    img_h, img_w = image.shape[:2]
    # Velikost okluzije je med 5% in 15% velikosti slike
    occ_h = random.randint(int(img_h * 0.05), int(img_h * 0.15))
    occ_w = random.randint(int(img_w * 0.05), int(img_w * 0.15))
    # Naključna pozicija
    x1 = random.randint(0, img_w - occ_w)
    y1 = random.randint(0, img_h - occ_h)
    # Uporabi črno barvo za okluzijo
    image[y1:y1 + occ_h, x1:x1 + occ_w] = 0
    return image


def get_train_augmentations(img_height=TARGET_IMG_HEIGHT, img_width=TARGET_IMG_WIDTH):
    """
    Definira in vrne sestavljen (Compose) objekt transformacij iz Albumentations.
    """
    return A.Compose([
        A.Rotate(limit=15, p=0.7, border_mode=cv2.BORDER_CONSTANT, value=0),
        A.ShiftScaleRotate(shift_limit=0.06, scale_limit=0.1, rotate_limit=0, p=0.7, border_mode=cv2.BORDER_CONSTANT),
        A.RandomBrightnessContrast(brightness_limit=0.2, contrast_limit=0.2, p=0.7),
        A.HueSaturationValue(hue_shift_limit=10, sat_shift_limit=20, val_shift_limit=10, p=0.5),
        A.Perspective(scale=(0.02, 0.05), p=0.3),
        A.GaussNoise(var_limit=(10.0, 50.0), mean=0, p=0.4),
        A.MotionBlur(blur_limit=5, p=0.3),
        A.GridDistortion(num_steps=5, distort_limit=0.1, p=0.3, border_mode=cv2.BORDER_CONSTANT),
        A.Lambda(image=random_small_occlusion, name="RandomSmallOcclusion", p=0.5),
    ],
        p=1.0)  # p=1.0 za Compose pomeni, da se bo vsaj ena izmed notranjih transformacij (z lastnim p) verjetno zgodila.


def display_augmented_examples(original, manual_augs, alb_augs):
    """Prikaže originalno sliko in primere obeh vrst augmentacij."""
    num_manual = len(manual_augs)
    num_alb = len(alb_augs)
    total_plots = 1 + num_manual + num_alb

    plt.figure(figsize=(3 * total_plots, 4))
    plt.suptitle("Primeri Augmentacij (Ročne in Albumentations)", fontsize=16)

    plt.subplot(1, total_plots, 1)
    plt.imshow(original)
    plt.title("Original (Obrezan)")
    plt.axis('off')

    for i, (img, title) in enumerate(manual_augs):
        plt.subplot(1, total_plots, 2 + i)
        plt.imshow(img)
        plt.title(f"Ročna: {title}")
        plt.axis('off')

    for i, img in enumerate(alb_augs):
        plt.subplot(1, total_plots, 2 + num_manual + i)
        plt.imshow(img)
        plt.title(f"Albumentations {i + 1}")
        plt.axis('off')

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.show()


def run_augmentation(base_denoised_setting):
    """
    Naloži predobdelane (obrezane) sete, izvede hibridno augmentacijo in shrani končni dataset.
    """
    denoise_suffix = f"_denoise-{str(base_denoised_setting).lower()}"
    processed_data_filename = f'lfw_processed_splits{denoise_suffix}.npz'
    processed_data_path = os.path.join(PROJECT_DATA_DIR, processed_data_filename)

    if not os.path.exists(processed_data_path):
        print(f"NAPAKA: Datoteka '{processed_data_path}' ne obstaja.")
        print("Prosim, najprej zaženi skripto 'process_lfw_data.py' za detekcijo in obrezovanje obrazov.")
        return False

    print(f"Nalaganje predobdelanih (obrezanih) podatkov iz: {processed_data_path}")
    data = np.load(processed_data_path)
    train_images_orig = data['train_images']
    train_labels_orig = data['train_labels']
    val_images = data['val_images']
    val_labels = data['val_labels']
    test_images = data['test_images']
    test_labels = data['test_labels']

    print(f"Učna množica (original) naložena: {train_images_orig.shape[0]} slik.")

    augmented_images_list = []
    augmented_labels_list = []

    # Pridobi cevovod augmentacij iz Albumentations
    alb_augmentations = get_train_augmentations()

    # Število augmentacij na sliko
    MANUAL_AUG_PER_IMAGE = 2  # Ustvari 2 sliki z ročnimi metodami
    ALB_AUG_PER_IMAGE = 4  # Ustvari 4 slike z Albumentations

    print(f"\nZačenjam augmentacijo na {train_images_orig.shape[0]} učnih slikah...")

    for i in range(train_images_orig.shape[0]):
        original_image = train_images_orig[i]
        original_label = train_labels_orig[i]

        # 1. Dodaj originalno sliko
        augmented_images_list.append(original_image)
        augmented_labels_list.append(original_label)

        # 2. Generiraj augmentacije z ROČNIMI funkcijami
        for _ in range(MANUAL_AUG_PER_IMAGE):
            img_temp = original_image.copy()

            # Naključno izberi eno ali dve ročni transformaciji
            if random.random() < 0.5:
                img_temp = custom_horizontal_flip(img_temp)
            if random.random() < 0.5:
                img_temp = custom_rotate_image(img_temp, random.uniform(-10, 10))
            if random.random() < 0.5:
                img_temp = custom_adjust_brightness(img_temp, random.uniform(0.7, 1.3))
            if random.random() < 0.3:
                img_temp = custom_add_gaussian_noise(img_temp, std_dev=random.uniform(0.01, 0.06))

            augmented_images_list.append(np.clip(img_temp, 0.0, 1.0))
            augmented_labels_list.append(original_label)

        # 3. Generiraj augmentacije z ALBUMENTATIONS
        # Albumentations pričakuje uint8 sliko [0, 255]
        original_image_uint8 = (original_image * 255).astype(np.uint8)
        for _ in range(ALB_AUG_PER_IMAGE):
            augmented = alb_augmentations(image=original_image_uint8)['image']
            # Pretvorba nazaj v float32 [0.0, 1.0]
            augmented_float = augmented.astype(np.float32) / 255.0
            augmented_images_list.append(augmented_float)
            augmented_labels_list.append(original_label)

        if (i + 1) % 500 == 0:
            print(f"  Augmentiranih {i + 1} originalnih slik (trenutno {len(augmented_images_list)} slik)...")

    train_images_aug = np.array(augmented_images_list)
    train_labels_aug = np.array(augmented_labels_list)

    print(f"\nKončano augmentiranje. Originalni učni set: {train_images_orig.shape[0]} slik.")
    print(f"Novi (augmentirani) učni set: {train_images_aug.shape[0]} slik.")

    # Prikaz primerov za eno sliko
    if train_images_orig.shape[0] > 0:
        idx = random.randint(0, train_images_orig.shape[0] - 1)
        display_img_orig = train_images_orig[idx]
        display_img_orig_uint8 = (display_img_orig * 255).astype(np.uint8)

        manual_examples = [
            (custom_horizontal_flip(display_img_orig.copy()), "Flip"),
            (custom_rotate_image(display_img_orig.copy(), 12), "Rotacija")
        ]
        alb_examples = [alb_augmentations(image=display_img_orig_uint8)['image'].astype(np.float32) / 255.0 for _ in
                        range(2)]

        display_augmented_examples(display_img_orig, manual_examples, alb_examples)

    # Shranjevanje končnega dataseta
    final_output_filename = f'lfw_final_dataset{denoise_suffix}.npz'
    final_output_path = os.path.join(PROJECT_DATA_DIR, final_output_filename)

    np.savez_compressed(final_output_path,
                        train_images=train_images_aug, train_labels=train_labels_aug,
                        val_images=val_images, val_labels=val_labels,
                        test_images=test_images, test_labels=test_labels)
    print(f"\nKončni dataset shranjen v: {final_output_path}")
    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Augmentacija LFW učnega dataseta.")
    parser.add_argument(
        '--base_denoised',
        action='store_true',
        help="Označuje, da je bil osnovni dataset obdelan z odstranjevanjem šuma."
    )
    args = parser.parse_args()

    print(f"Augmentacija se bo izvedla na osnovi dataseta z denoising={args.base_denoised}")
    run_augmentation(base_denoised_setting=args.base_denoised)