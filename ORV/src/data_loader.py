# src/data_loader.py
import numpy as np
import os
import random
from collections import defaultdict
import tensorflow as tf  # Dodaj tf import, če še ni
from tensorflow.keras.utils import Sequence
from src import config  # Spremenjeno iz 'from . import config'


def load_prepared_dataset(data_path=config.FINAL_DATASET_PATH):
    # ... (ostalo ostane enako) ...
    if not os.path.exists(data_path):
        print(f"NAPAKA: Datoteka '{data_path}' ne obstaja.")
        print("Prosim, preveri, ali je datoteka na pravi poti in ali so prejšnje skripte uspešno tekle.")
        return None
    try:
        data = np.load(data_path)
        train_images = data['train_images']
        train_labels = data['train_labels']
        val_images = data['val_images']
        val_labels = data['val_labels']
        test_images = data['test_images']
        test_labels = data['test_labels']

        if train_labels.dtype == 'S15' or (train_labels.size > 0 and isinstance(train_labels[0], bytes)):
            train_labels = np.array([label.decode('utf-8') for label in train_labels])
            val_labels = np.array([label.decode('utf-8') for label in val_labels])
            test_labels = np.array([label.decode('utf-8') for label in test_labels])

        print(f"Podatki uspešno naloženi iz {data_path}")
        print(f"  Učna množica: {train_images.shape[0]} slik")
        print(f"  Validacijska množica: {val_images.shape[0]} slik")
        print(f"  Testna množica: {test_images.shape[0]} slik")
        return train_images, train_labels, val_images, val_labels, test_images, test_labels
    except Exception as e:
        print(f"NAPAKA pri nalaganju podatkov iz '{data_path}': {e}")
        return None


class TripletGenerator(Sequence):
    def __init__(self, images, labels, batch_size, num_triplets_per_epoch, shuffle=True, **kwargs):  # Dodaj **kwargs
        super().__init__(**kwargs)  # <<<--- POMEMBNO: Klic super().__init__
        self.images = images
        self.labels = labels
        self.batch_size = batch_size
        self.num_triplets_to_generate = num_triplets_per_epoch
        self.shuffle = shuffle

        self.label_to_indices = defaultdict(list)
        for idx, label in enumerate(self.labels):
            self.label_to_indices[label].append(idx)

        self.unique_labels = list(self.label_to_indices.keys())
        self.labels_with_multiple_samples = [
            label for label in self.unique_labels if len(self.label_to_indices[label]) >= 2
        ]
        if not self.labels_with_multiple_samples:
            raise ValueError("Ni dovolj vzorcev z vsaj dvema slikama na oznako za ustvarjanje trojčkov.")

        self.indexes = np.arange(self.num_triplets_to_generate)
        if self.shuffle:
            np.random.shuffle(self.indexes)

    def __len__(self):
        return int(np.ceil(self.num_triplets_to_generate / self.batch_size))

    def __getitem__(self, index):
        batch_anchors_list = []
        batch_positives_list = []
        batch_negatives_list = []

        # Določi dejansko število trojčkov za ta batch (lahko je manjše za zadnji batch)
        current_batch_size = self.batch_size
        if (index + 1) * self.batch_size > self.num_triplets_to_generate:
            current_batch_size = self.num_triplets_to_generate - index * self.batch_size

        for _ in range(current_batch_size):  # Spremenjeno, da generira točno current_batch_size
            anchor_label = random.choice(self.labels_with_multiple_samples)
            idx_a, idx_p = random.sample(self.label_to_indices[anchor_label], 2)

            negative_label = random.choice(self.unique_labels)
            while negative_label == anchor_label:
                negative_label = random.choice(self.unique_labels)
            idx_n = random.choice(self.label_to_indices[negative_label])

            batch_anchors_list.append(self.images[idx_a])
            batch_positives_list.append(self.images[idx_p])
            batch_negatives_list.append(self.images[idx_n])

        # Pretvori sezname v NumPy arraye
        batch_anchors_np = np.array(batch_anchors_list, dtype=np.float32)
        batch_positives_np = np.array(batch_positives_list, dtype=np.float32)
        batch_negatives_np = np.array(batch_negatives_list, dtype=np.float32)

        # Model za učenje s triplet loss pričakuje vhode kot TUPLE NumPy arrayev
        # in y_true (ki ga ne bomo uporabljali direktno v izračunu izgube)
        return (batch_anchors_np, batch_positives_np, batch_negatives_np), np.zeros(current_batch_size,
                                                                                    dtype=np.float32)

    def on_epoch_end(self):
        if self.shuffle:
            # Ker se trojčki generirajo naključno v __getitem__,
            # ni potrebe po premeščanju self.indexes, če ti ne predstavljajo
            # specifičnih anchorjev, ampak samo število generacij.
            pass


if __name__ == '__main__':
    # ... (testni del ostane enak, vendar preveri, če še vedno deluje po spremembah)
    dataset = load_prepared_dataset()
    if dataset:
        train_images, train_labels, val_images, val_labels, _, _ = dataset

        print(f"\nTestiranje TripletGenerator za učno množico:")
        if train_images.shape[0] > 0 and len(train_labels) > 0:
            try:
                train_generator = TripletGenerator(
                    train_images, train_labels,
                    batch_size=config.BATCH_SIZE,
                    num_triplets_per_epoch=100
                )
                print(f"Število batchev v train_generator: {len(train_generator)}")

                sample_batch_x, sample_batch_y = train_generator[0]
                print(f"Tip sample_batch_x: {type(sample_batch_x)}")
                print(f"Dolžina sample_batch_x (če je tuple): {len(sample_batch_x)}")
                print(f"Oblika anchor batch: {sample_batch_x[0].shape}")
                print(f"Oblika positive batch: {sample_batch_x[1].shape}")
                print(f"Oblika negative batch: {sample_batch_x[2].shape}")
                print(f"Oblika y_true batch: {sample_batch_y.shape}")
            except ValueError as e:
                print(f"Napaka pri inicializaciji TripletGenerator (train): {e}")
        else:
            print("Učna množica je prazna, preskakujem test TripletGeneratorja zanjo.")

        # ... (podobno za val_generator)