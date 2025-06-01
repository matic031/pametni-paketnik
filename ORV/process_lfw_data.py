import tensorflow_datasets as tfds
import tensorflow as tf
import numpy as np
from sklearn.model_selection import train_test_split
import os
import cv2  # Uporabljam cv2 za obdelavo slik
import matplotlib.pyplot as plt  # Za prikaz slik
import sys  # Za sys.stderr, za izpis napak
import argparse

# --- Osnovne nastavitve ---
PROJECT_DATA_DIR = os.path.join(os.getcwd(), 'data')  # Mapa, kjer se nahajajo podatki TFDS (LFW)
TARGET_IMG_HEIGHT = 64  # Ciljna višina slik po preoblikovanju
TARGET_IMG_WIDTH = 64  # Ciljna širina slik po preoblikovanju
CHANNELS = 3  # Število barvnih kanalov (RGB za barvne slike)

VAL_SPLIT_SIZE_FROM_ALL = 0.15  # Delež podatkov za validacijsko množico (od vseh)
TEST_SPLIT_SIZE_FROM_ALL = 0.15  # Delež podatkov za testno množico (od vseh)
RANDOM_STATE = 42  # Fiksno seme za ponovljivost pri delitvi podatkov


# --- Funkcija za odstranjevanje šuma ---
def denoise_image_opencv(image_uint8):  # Funkcija za zmanjšanje šuma na sliki
    """Odstrani šum iz slike (uint8 NumPy array) z Gaussovim filtrom."""  # Opis delovanja funkcije
    # Gaussov filter z jedrom 3x3 se uporabi za glajenje in zmanjšanje šuma.
    # Tretji parameter (0) pomeni, da se standardna deviacija izračuna samodejno.
    denoised_image = cv2.GaussianBlur(image_uint8, (3, 3), 0)
    return denoised_image  # Vrne obdelano sliko


def load_lfw_from_local_tfds(data_path):  # Funkcija za nalaganje LFW dataseta
    """Naloži LFW dataset iz lokalne TFDS mape."""  # Opis funkcije
    print(f"Nalaganje LFW dataseta iz lokalne mape: {data_path}...")  # Izpis poteka
    try:  # Blok za lovljenje morebitnih napak
        dataset, info = tfds.load(  # Uporaba TFDS za nalaganje
            'lfw',  # Ime dataseta
            split='train',  # Uporabi celoten dataset, ki je na voljo pod 'train'
            with_info=True,  # Pridobi tudi informacije o datasetu
            data_dir=data_path  # Specificira mapo, kjer se dataset nahaja ali kamor naj se shrani
        )
        print("LFW dataset uspešno naložen.")  # Potrditev uspešnega nalaganja
        return dataset, info  # Vrne dataset in informacije o njem
    except Exception as e:  # V primeru napake
        print(f"Napaka pri nalaganju LFW iz {data_path}: {e}")  # Izpis napake
        return None, None  # Vrne None, None


def resize_image_uint8_dict_input(features):  # Funkcija za spreminjanje velikosti slike, pričakuje slovar
    """
    Sprejme slovar 'features', vzame 'image' in 'label',
    spremeni velikost slike in zagotovi, da je uint8.
    Vrne predelan slovar.
    """  # Opis delovanja
    image = features['image']  # Vzame sliko iz slovarja
    label = features['label']  # Vzame oznako iz slovarja

    try:  # Poskusi izvesti operacije
        # Spremeni velikost slike na TARGET_IMG_HEIGHT x TARGET_IMG_WIDTH
        resized_image = tf.image.resize(image, [TARGET_IMG_HEIGHT, TARGET_IMG_WIDTH])
        # Pretvori podatkovni tip slike v uint8 (celi deli med 0 in 255)
        resized_image_uint8 = tf.cast(resized_image, tf.uint8)
    except Exception as e_resize:  # Če pride do napake med spreminjanjem velikosti ali pretvorbo
        # Izpiše napako, vključno z oznako slike in njeno originalno obliko za lažje razhroščevanje
        tf.print(
            f"NAPAKA med tf.image.resize za oznako '{label}': {e_resize}. Oblika slike je bila: {tf.shape(image)}. Ustvarjam placeholder.",
            output_stream=sys.stderr)
        # Ustvari prazno (črno) sliko kot placeholder, da se proces ne ustavi
        resized_image_uint8 = tf.zeros([TARGET_IMG_HEIGHT, TARGET_IMG_WIDTH, CHANNELS], dtype=tf.uint8)

    return {'image': resized_image_uint8, 'label': label}  # Vrne slovar s predelano sliko in originalno oznako


# Funkcija preprocess_image (resize in float normalizacija) trenutno ni direktno uporabljena v glavnem toku,
# ker se odstranjevanje šuma izvaja na uint8 slikah. Lahko služi kot referenca.
def preprocess_image(image, label):
    """Spremeni velikost slike in jo normalizira v float32 [0,1]."""
    image = tf.image.resize(image, [TARGET_IMG_HEIGHT, TARGET_IMG_WIDTH])
    image = tf.cast(image, tf.float32) / 255.0
    return image, label


def dataset_to_numpy_internal(dataset, num_samples=None, apply_denoising_flag=False):  # Interna funkcija za pretvorbo
    """
    Interna funkcija za pretvorbo tf.data.Dataset v NumPy arraye (slike, oznake).
    Vključuje spreminjanje velikosti, opcijsko odstranjevanje šuma in normalizacijo.
    """  # Opis funkcije
    print(
        f"Interno predprocesiranje (resize, opc. denoise, normalize)... Denoising: {apply_denoising_flag}")  # Izpis statusa

    # Uporabi .map() za paralelno spreminjanje velikosti slik in pretvorbo v uint8
    dataset = dataset.map(resize_image_uint8_dict_input, num_parallel_calls=tf.data.AUTOTUNE)

    if num_samples:  # Če je podano število vzorcev, omeji dataset
        dataset = dataset.take(num_samples)

    temp_images_list_uint8 = []  # Začasni seznam za uint8 slike
    labels_list_bytes = []  # Začasni seznam za oznake (kot bajti)
    print("Pretvarjanje v NumPy (uint8)...")  # Statusni izpis
    processed_count = 0  # Števec obdelanih slik
    skipped_placeholders = 0  # Števec preskočenih placeholderjev

    for features_dict in dataset:  # Iteracija čez vsak element (slovar) v datasetu
        image_uint8_tensor = features_dict['image']  # Vzemi slikovni tenzor
        label_bytes_tensor = features_dict['label']  # Vzemi tenzor z oznako

        # Preveri, ali je slika placeholder (sestavljena samo iz ničel)
        if tf.reduce_all(tf.equal(image_uint8_tensor, 0)) and \
                image_uint8_tensor.shape == (TARGET_IMG_HEIGHT, TARGET_IMG_WIDTH, CHANNELS):
            skipped_placeholders += 1  # Povečaj števec preskočenih
            continue  # Preskoči ta primerek in nadaljuj z naslednjim

        temp_images_list_uint8.append(image_uint8_tensor.numpy())  # Pretvori tenzor v NumPy array in dodaj na seznam
        labels_list_bytes.append(label_bytes_tensor.numpy())  # Enako za oznako
        processed_count += 1  # Povečaj števec obdelanih
        if processed_count > 0 and processed_count % 1000 == 0: print(
            f"  Pretvorjenih {processed_count} slik v NumPy...")  # Občasni izpis napredka

    if not temp_images_list_uint8:  # Če po filtriranju ni ostalo nobenih slik
        print("Ni bilo veljavnih slik po resize in filtriranju placeholderjev.")
        return np.array([]), np.array([])  # Vrni prazna arraya

    images_np_uint8 = np.array(temp_images_list_uint8)  # Pretvori seznam slik v NumPy array
    labels_np_bytes = np.array(labels_list_bytes)  # Pretvori seznam oznak v NumPy array
    print(
        f"Dejansko število slik po filtriranju: {images_np_uint8.shape[0]} (preskočenih: {skipped_placeholders})")  # Izpis statistike

    processed_images_final_float32 = []  # Seznam za končne, normalizirane float32 slike
    print("Opcijsko odstranjevanje šuma in normalizacija...")  # Statusni izpis
    for i in range(images_np_uint8.shape[0]):  # Iteracija čez vse uint8 slike
        current_img_uint8 = images_np_uint8[i]  # Trenutna uint8 slika
        if apply_denoising_flag:  # Če je vklopljeno odstranjevanje šuma
            current_img_uint8 = denoise_image_opencv(current_img_uint8)  # Uporabi funkcijo za odstranjevanje šuma

        # Pretvori v float32 in normaliziraj vrednosti pikslov na obseg [0.0, 1.0]
        img_normalized_float32 = current_img_uint8.astype(np.float32) / 255.0
        processed_images_final_float32.append(img_normalized_float32)  # Dodaj na seznam
        if i > 0 and i % 1000 == 0: print(f"  Normaliziranih {i} slik...")  # Občasni izpis napredka
    print(f"  Normaliziranih {len(processed_images_final_float32)} slik (skupaj).")  # Končni izpis normaliziranih
    return np.array(processed_images_final_float32), labels_np_bytes  # Vrne arraye slik in oznak


def load_and_preprocess_lfw(data_path, num_samples=None,
                            apply_denoising=False):  # Glavna funkcija za nalaganje in predobdelavo
    """
    Naloži LFW dataset, ga predprocesira (resize, opc. denoise, normalize)
    in vrne kot NumPy arraye.
    """  # Opis funkcije
    lfw_tf_dataset, _ = load_lfw_from_local_tfds(data_path)  # Naloži dataset
    if not lfw_tf_dataset:  # Če nalaganje ni uspelo
        print("LFW dataset ni bil naložen. Prekinjam predobdelavo.")
        return np.array([]), np.array([])  # Vrni prazna arraya

    images_np, labels_np = dataset_to_numpy_internal(
        lfw_tf_dataset,
        num_samples=num_samples,
        apply_denoising_flag=apply_denoising  # Pravilno ime argumenta
    )
    return images_np, labels_np  # Vrne predprocesirane slike in oznake


def split_data_into_sets(all_images, all_labels, val_share, test_share, rnd_state):  # Funkcija za delitev podatkov
    """
    Razdeli podane slike in oznake na učno, validacijsko in testno množico.
    val_share in test_share sta deleža od celotne množice.
    """  # Opis funkcije
    if all_images.size == 0:  # Če ni podatkov
        print("Ni podatkov za delitev.")
        return (np.array([]), np.array([]), np.array([]), np.array([]), np.array([]), np.array([]))

    print("\nDelitev podatkov na učno, validacijsko in testno množico...")  # Statusni izpis

    remaining_size = val_share + test_share  # Izračunaj skupni delež za validacijo in test
    if remaining_size >= 1.0:  # Preverjanje smiselnosti deležev
        print("NAPAKA: Vsota val_share in test_share mora biti manjša od 1.0.")
        return all_images, all_labels, np.array([]), np.array([]), np.array([]), np.array([])

    # Določitev minimalnega števila vzorcev za smiselno delitev
    min_samples_needed = 2
    # Logika za določanje min_samples_needed, odvisno od deležev
    if val_share > 0 and test_share > 0 and (1.0 - remaining_size) > 0:
        min_samples_needed = max(2, int(1.0 / min(val_share, test_share, 1.0 - remaining_size)))
    elif val_share > 0 or test_share > 0:
        min_samples_needed = 2

    if all_images.shape[0] < min_samples_needed:  # Če je premalo slik
        print(
            f"Premalo slik ({all_images.shape[0]}) za smiselno delitev (potrebno vsaj {min_samples_needed}). Vsi podatki bodo v učni množici.")
        return all_images, all_labels, np.array([]), np.array([]), np.array([]), np.array([])

    try:  # Blok za lovljenje napak pri delitvi
        # Prva delitev: train vs (validation + test)
        train_images, remaining_images, train_labels, remaining_labels = train_test_split(
            all_images, all_labels,
            test_size=remaining_size,
            random_state=rnd_state
        )

        # Druga delitev: validation vs test (iz 'remaining' množice)
        if remaining_images.shape[0] < 2 or (val_share == 0 and test_share == 0):
            # Posebna obravnava, če je preostanek premajhen ali če ni potrebe po nadaljnji delitvi
            if val_share > 0:
                val_images, val_labels = (remaining_images, remaining_labels) if remaining_images.size > 0 else (
                np.array([]), np.array([]))
            else:
                val_images, val_labels = np.array([]), np.array([])
            if test_share > 0:
                test_images, test_labels = (remaining_images, remaining_labels) if (
                            val_share == 0 and remaining_images.size > 0) else (np.array([]), np.array([]))
            else:
                test_images, test_labels = np.array([]), np.array([])
            # Popravek, če je ostal samo en primerek in oba deleža sta > 0
            if remaining_images.shape[0] == 1 and val_share > 0 and test_share > 0:
                if val_share >= test_share:
                    val_images, val_labels = remaining_images, remaining_labels; test_images, test_labels = np.array(
                        []), np.array([])
                else:
                    test_images, test_labels = remaining_images, remaining_labels; val_images, val_labels = np.array(
                        []), np.array([])

        elif val_share == 0:  # Vse preostalo gre v test
            val_images, val_labels = np.array([]), np.array([])
            test_images, test_labels = remaining_images, remaining_labels
        elif test_share == 0:  # Vse preostalo gre v val
            test_images, test_labels = np.array([]), np.array([])
            val_images, val_labels = remaining_images, remaining_labels
        else:  # Standardna druga delitev
            relative_test_size_from_remaining = test_share / remaining_size
            val_images, test_images, val_labels, test_labels = train_test_split(
                remaining_images, remaining_labels,
                test_size=relative_test_size_from_remaining,
                random_state=rnd_state
            )

        print(f"  Učna množica: {train_images.shape[0]} slik")  # Izpis velikosti množic
        print(f"  Validacijska množica: {val_images.shape[0]} slik")
        print(f"  Testna množica: {test_images.shape[0]} slik")
        return train_images, train_labels, val_images, val_labels, test_images, test_labels

    except ValueError as e_split:  # V primeru napake pri delitvi
        print(f"Napaka pri delitvi podatkov: {e_split}")
        return all_images, all_labels, np.array([]), np.array([]), np.array([]), np.array([])


def save_splits_to_npz(path, filename_prefix="lfw_processed_splits", denoise_info="",
                       **kwargs):  # Funkcija za shranjevanje
    """Shrani podane podatkovne množice v .npz datoteko."""  # Opis
    if not kwargs:  # Če ni podanih argumentov za shranjevanje
        print("Ni podatkov za shranjevanje.")
        return

    if 'train_images' not in kwargs or kwargs['train_images'].size == 0:  # Preveri, ali obstaja učna množica
        print("Učna množica (train_images) je prazna ali manjka. Podatki ne bodo shranjeni.")
        return

    output_filename = f'{filename_prefix}{denoise_info}.npz'  # Sestavi ime datoteke
    output_path = os.path.join(path, output_filename)  # Sestavi polno pot

    np.savez_compressed(output_path, **kwargs)  # Shrani podatke v stisnjeno .npz datoteko
    print(f"\nPodatkovne množice shranjene v {output_path}")  # Izpis poti


def display_sample_numpy_images(images, labels, count=5, title="Vzorčne slike"):  # Funkcija za prikaz slik
    """Prikaže nekaj vzorčnih slik iz NumPy arraya."""  # Opis
    if images.size == 0: print(f"{title}: Ni slik za prikaz."); return  # Preverjanje praznega arraya
    actual_count = min(count, len(images))  # Dejansko število slik za prikaz
    if actual_count == 0: print(f"{title}: Ni slik za prikaz (actual_count je 0)."); return  # Dodatno preverjanje
    plt.figure(figsize=(12, 4 if actual_count <= 5 else 8));
    plt.suptitle(title)  # Ustvari figuro
    indices = np.random.choice(len(images), actual_count, replace=False)  # Naključna izbira indeksov
    cols = min(actual_count, 5);
    rows = int(np.ceil(len(indices) / cols))  # Izračun vrstic in stolpcev za prikaz
    for i, idx in enumerate(indices):  # Iteracija za prikaz vsake slike
        plt.subplot(rows, cols, i + 1)  # Ustvari podgraf
        if images[idx].ndim == 3:
            plt.imshow(images[idx])  # Prikaži sliko, če ima pravilne dimenzije
        else:
            plt.imshow(np.zeros((TARGET_IMG_HEIGHT, TARGET_IMG_WIDTH, CHANNELS))); print(
                f"Opozorilo: Slika na indeksu {idx} za prikaz nima 3 dimenzij, oblika: {images[idx].shape}")
        label_str = labels[idx].decode('utf-8', errors='ignore') if isinstance(labels[idx], bytes) else str(
            labels[idx])  # Priprava oznake
        plt.title(f"{label_str[:15]}");
        plt.axis('off')  # Nastavi naslov podgrafa in skrij osi
    plt.tight_layout(rect=[0, 0, 1, 0.95]);
    plt.show()  # Prilagodi postavitev in prikaži


def run_processing(apply_denoising_main_flag, show_plots=True):  # Dodan argument show_plots
    """
    Glavna funkcija za izvedbo celotnega procesa predobdelave podatkov.
    """
    print(f"*** Začenjam procesiranje LFW podatkov (Odstranjevanje šuma: {apply_denoising_main_flag}) ***")

    all_images_processed_np, all_labels_processed_np = load_and_preprocess_lfw(
        data_path=PROJECT_DATA_DIR,
        num_samples=None,
        apply_denoising=apply_denoising_main_flag
    )

    if all_images_processed_np.size > 0:
        print(f"\nOblika vseh predprocesiranih slik: {all_images_processed_np.shape}")
        print(f"Oblika vseh oznak: {all_labels_processed_np.shape}")
        if all_labels_processed_np.size > 0:
            print(f"Primer prve oznake: {all_labels_processed_np[0].decode('utf-8', errors='ignore')}")

        if show_plots:  # Opcijski prikaz
            display_sample_numpy_images(all_images_processed_np, all_labels_processed_np, count=10,
                                        title=f"VSE SLIKE po predobdelavi (Denoise: {apply_denoising_main_flag})")

        train_img, train_lbl, val_img, val_lbl, test_img, test_lbl = split_data_into_sets(
            all_images_processed_np, all_labels_processed_np,
            val_share=VAL_SPLIT_SIZE_FROM_ALL,
            test_share=TEST_SPLIT_SIZE_FROM_ALL,
            rnd_state=RANDOM_STATE
        )

        if show_plots:  # Opcijski prikaz
            display_sample_numpy_images(train_img, train_lbl, count=max(1, min(3, len(train_img))),
                                        title=f"UČNA (Denoise: {apply_denoising_main_flag})")
            display_sample_numpy_images(val_img, val_lbl, count=max(1, min(3, len(val_img))),
                                        title=f"VALIDACIJSKA (Denoise: {apply_denoising_main_flag})")
            display_sample_numpy_images(test_img, test_lbl, count=max(1, min(3, len(test_img))),
                                        title=f"TESTNA (Denoise: {apply_denoising_main_flag})")

        denoise_suffix = f"_denoise-{str(apply_denoising_main_flag).lower()}"
        save_splits_to_npz(
            path=PROJECT_DATA_DIR,
            filename_prefix="lfw_processed_splits",
            denoise_info=denoise_suffix,
            train_images=train_img, train_labels=train_lbl,
            val_images=val_img, val_labels=val_lbl,
            test_images=test_img, test_labels=test_lbl
        )
        return True  # Vrne True za uspeh
    else:
        print("Ni bilo naloženih nobenih slik po predobdelavi, nadaljnja obdelava ni mogoča.")
        return False  # Vrne False za neuspeh


if __name__ == '__main__':  # Začetek glavnega dela, ki se izvede ob zagonu skripte
    parser = argparse.ArgumentParser(description="Predelava LFW dataseta.")
    parser.add_argument(
        '--denoise',
        action='store_true',  # Če je podan --denoise, bo args.denoise True
        help="Vklopi odstranjevanje šuma med predobdelavo."
    )
    parser.add_argument(
        '--no_plots',  # Nov argument za izklop prikazov
        action='store_true',
        help="Izklopi prikazovanje slik z matplotlib."
    )
    args = parser.parse_args()

    APPLY_DENOISING_FROM_ARGS = args.denoise
    SHOW_PLOTS_FLAG = not args.no_plots  # Če je --no_plots podan, bo show_plots False

    print(f"Argument --denoise je nastavljen na: {APPLY_DENOISING_FROM_ARGS}")
    print(f"Argument --no_plots je nastavljen na: {args.no_plots} (Prikaz slik: {SHOW_PLOTS_FLAG})")


    run_processing(apply_denoising_main_flag=APPLY_DENOISING_FROM_ARGS, show_plots=SHOW_PLOTS_FLAG)
