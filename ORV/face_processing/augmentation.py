import numpy as np
import cv2
import random
import albumentations as A


# --- Definicija lastnih augmentacijskih funkcij (kot si jih podal) ---
def custom_horizontal_flip(image):
    """Ročno implementiran horizontalni flip slike (NumPy array H, W, C)."""
    return image[:, ::-1, :]


def custom_adjust_brightness(image, brightness_factor):
    """Ročno implementirana sprememba svetlosti.
    brightness_factor: > 1.0 za svetlejšo, < 1.0 za temnejšo.
    Slika mora biti normalizirana na [0,1].
    """
    augmented_image = image * brightness_factor
    return np.clip(augmented_image, 0.0, 1.0)


def custom_rotate_image(image, angle_deg):
    """Ročno implementirana rotacija slike za podan kot (v stopinjah).
       Ohrani originalne dimenzije, robovi so črni.
       Slika je NumPy array (H, W, C), normaliziran na [0,1].
    """
    if image.ndim == 2:  # Sivinska slika
        image_uint8 = (image * 255).astype(np.uint8)
        height, width = image_uint8.shape
        channels = 1
    elif image.ndim == 3:  # Barvna slika
        image_uint8 = (image * 255).astype(np.uint8)
        height, width, channels = image_uint8.shape
    else:
        raise ValueError("Slika mora biti 2D (sivinska) ali 3D (barvna)")

    center_x, center_y = width // 2, height // 2
    rotation_matrix = cv2.getRotationMatrix2D((center_x, center_y), angle_deg, 1.0)

    border_val = (0, 0, 0) if channels == 3 else 0  # Črna barva za robove

    rotated_img_uint8 = cv2.warpAffine(image_uint8, rotation_matrix, (width, height),
                                       flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=border_val)

    # Če je bila vhodna slika sivinska, poskrbimo, da ostane 2D
    if channels == 1 and rotated_img_uint8.ndim == 2:
        rotated_img_uint8 = rotated_img_uint8.reshape(height, width)
    elif channels == 3 and rotated_img_uint8.ndim == 2:  # OpenCV lahko vrne 2D za popolnoma črno sliko
        rotated_img_uint8 = cv2.cvtColor(rotated_img_uint8, cv2.COLOR_GRAY2RGB)

    return rotated_img_uint8.astype(np.float32) / 255.0


def custom_add_gaussian_noise(image, mean=0.0, std_dev=0.05):
    """Ročno implementirano dodajanje Gaussovega šuma.
       std_dev je relativno na obseg slike [0,1].
       Slika je NumPy array (H, W, C), normaliziran na [0,1].
    """
    noise = np.random.normal(mean, std_dev, image.shape).astype(np.float32)
    noisy_image = image + noise
    return np.clip(noisy_image, 0.0, 1.0)


# --- Pomožne funkcije za uporabo z Albumentations Lambda ---
def apply_custom_horizontal_flip(image, **kwargs):
    return custom_horizontal_flip(image)


def apply_custom_brightness(image, **kwargs):
    factor = random.uniform(0.7, 1.3)  # Naključni faktor svetlosti
    return custom_adjust_brightness(image, factor)


def apply_custom_rotation(image, **kwargs):
    angle = random.uniform(-15, 15)  # Naključni kot rotacije med -15 in 15 stopinj
    return custom_rotate_image(image, angle)


def apply_custom_noise(image, **kwargs):
    std = random.uniform(0.01, 0.05)  # Naključna standardna deviacija za šum
    return custom_add_gaussian_noise(image, std_dev=std)


# --- Glavni cevovod za augmentacijo izrezanega obraza ---
# Velikost slike mora biti usklajena z zahtevami embedding modela (npr. FaceNet pričakuje 160x160)
IMG_SIZE_FOR_EMBEDDING = 160

# Ta transformacija bo uporabljena za generiranje več različic ENE registracijske slike
# Predpostavka: vhodna slika za ta cevovod je že izrezan obraz, normaliziran na [0,1] float32, RGB
face_augmentations_for_registration = A.Compose([
    # Resize in Pad najprej, da so vse slike enake velikosti pred ostalimi augmentacijami
    # To je pomembno, da se augmentacije, ki so odvisne od velikosti, obnašajo predvidljivo.
    A.SmallestMaxSize(max_size=IMG_SIZE_FOR_EMBEDDING, interpolation=cv2.INTER_AREA),
    A.PadIfNeeded(min_height=IMG_SIZE_FOR_EMBEDDING, min_width=IMG_SIZE_FOR_EMBEDDING,
                  border_mode=cv2.BORDER_CONSTANT),
    A.CenterCrop(height=IMG_SIZE_FOR_EMBEDDING, width=IMG_SIZE_FOR_EMBEDDING),

    # Tvoje lastne augmentacije
    A.Lambda(image=apply_custom_horizontal_flip, name="CustomHorizontalFlip", p=0.5),
    A.Lambda(image=apply_custom_brightness, name="CustomBrightness", p=0.4),  # p je verjetnost uporabe
    A.Lambda(image=apply_custom_rotation, name="CustomRotation", p=0.4),
    A.Lambda(image=apply_custom_noise, name="CustomGaussianNoise", p=0.3),

    # Dodatne augmentacije iz Albumentations
    A.RandomBrightnessContrast(brightness_limit=0.15, contrast_limit=0.15, p=0.4),
    A.HueSaturationValue(hue_shift_limit=8, sat_shift_limit=15, val_shift_limit=8, p=0.3),
    # A.GaussNoise(var_limit=(5.0/255.0, 30.0/255.0), mean=0, p=0.2), # Lahko podvoji tvojo funkcijo
    A.MotionBlur(blur_limit=3, p=0.2),

    # Zagotovimo, da je output vedno pravilne oblike in tipa za embedding model
    # A.PadIfNeeded in CenterCrop na začetku to že večinoma zagotovita.
    # Normalizacija za FaceNet je ponavadi specifična (z-score), kar knjižnica `keras-facenet`
    # naredi interno, če je vhod float32. Zato tukaj ne rabimo eksplicitne `A.Normalize`.
])


def generate_augmented_faces(face_image_rgb_normalized, num_augmentations=5):
    """
    Generira več augmentiranih različic izrezanega obraza.
    :param face_image_rgb_normalized: NumPy array izrezanega obraza (RGB, vrednosti [0,1], poljubna velikost).
    :param num_augmentations: Število augmentiranih slik za generiranje (vključno z originalno).
    :return: Seznam NumPy arrayev augmentiranih obrazov (vsak 160x160, RGB, [0,1]).
    """
    augmented_list = []

    # Prva slika v seznamu bo originalna, le prilagojena na pravo velikost.
    # Uporabimo samo del cevovoda za resize/crop.
    base_transform = A.Compose([
        A.SmallestMaxSize(max_size=IMG_SIZE_FOR_EMBEDDING, interpolation=cv2.INTER_AREA),
        A.PadIfNeeded(min_height=IMG_SIZE_FOR_EMBEDDING, min_width=IMG_SIZE_FOR_EMBEDDING,
                      border_mode=cv2.BORDER_CONSTANT),
        A.CenterCrop(height=IMG_SIZE_FOR_EMBEDDING, width=IMG_SIZE_FOR_EMBEDDING),
    ])

    if face_image_rgb_normalized is None or face_image_rgb_normalized.size == 0:
        print("Warning: Empty face image provided to generate_augmented_faces.")
        return []

    # Preverimo, da vhod ni prazen po dimenzijah
    if face_image_rgb_normalized.shape[0] == 0 or face_image_rgb_normalized.shape[1] == 0:
        print(f"Warning: Face image has zero dimension: {face_image_rgb_normalized.shape}")
        return []

    processed_original = base_transform(image=face_image_rgb_normalized.copy())['image']
    augmented_list.append(processed_original)

    # Generiraj preostale augmentirane slike
    for _ in range(num_augmentations - 1):  # -1 ker smo original že dodali
        # Vedno uporabi originalno sliko (pred resize/crop za base) kot vhod v polni augmentacijski cevovod
        # Ker face_augmentations_for_registration že vsebuje resize/crop, mu lahko damo originalno
        augmented = face_augmentations_for_registration(image=face_image_rgb_normalized.copy())
        augmented_list.append(augmented['image'])

    return augmented_list