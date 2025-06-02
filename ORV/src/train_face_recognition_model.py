import os
import sys
import datetime

# -------- Prilagoditev poti za relativne importe v paketu src --------
PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))

current_dir = os.path.dirname(os.path.abspath(__file__))  # To je vedno .../ORV/src
project_root = os.path.dirname(current_dir)  # To je vedno .../ORV

# Dodajemo koren projekta v sys.path, da lahko uporabljamo absolutne importe
if project_root not in sys.path:
    sys.path.append(project_root)


import tensorflow as tf
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau, TensorBoard

# Uporabi absolutne importe, ker smo dodali koren projekta v sys.path
from src import config  # Spremenjeno iz '. import config'
from src.data_loader import load_prepared_dataset, TripletGenerator
from src.model_definition import create_embedding_model, create_triplet_training_model, \
    get_triplet_loss_fn


def train_model():
    print("--- Začetek procesa učenja modela za prepoznavo obrazov ---")

    # 1. Nalaganje podatkov
    print("\n[KORAK 1/5] Nalaganje pripravljenih podatkov...")
    # config.FINAL_DATASET_PATH je že absolutna pot, zato je to v redu
    dataset = load_prepared_dataset(config.FINAL_DATASET_PATH)
    if dataset is None:
        print("Nalaganje podatkov ni uspelo. Prekinjam učenje.")
        return

    train_images, train_labels, val_images, val_labels, _, _ = dataset

    if train_images.shape[0] == 0 or val_images.shape[0] == 0:
        print("Učna ali validacijska množica je prazna. Prekinjam učenje.")
        return

    # 2. Priprava generatorjev podatkov
    print("\n[KORAK 2/5] Priprava generatorjev podatkov...")
    try:
        train_generator = TripletGenerator(
            train_images, train_labels,
            batch_size=config.BATCH_SIZE,
            num_triplets_per_epoch=config.NUM_TRAIN_TRIPLETS_PER_EPOCH
        )
        val_generator = TripletGenerator(
            val_images, val_labels,
            batch_size=config.BATCH_SIZE,
            num_triplets_per_epoch=config.NUM_VAL_TRIPLETS_PER_EPOCH,
            shuffle=False
        )
    except ValueError as e:
        print(f"Napaka pri ustvarjanju generatorjev: {e}")
        return

    print(f"  Train generator: {len(train_generator)} batchev na epoho.")
    print(f"  Validation generator: {len(val_generator)} batchev na epoho.")

    # 3. Definiranje modela
    print("\n[KORAK 3/5] Definiranje modelov...")
    embedding_model = create_embedding_model(
        input_shape=(config.IMG_HEIGHT, config.IMG_WIDTH, config.IMG_CHANNELS),
        embedding_dim=config.EMBEDDING_DIM
    )
    triplet_training_model = create_triplet_training_model(embedding_model)

    print("--- Struktura Embedding Modela ---")
    embedding_model.summary()
    print("\n--- Struktura Triplet Training Modela ---")
    triplet_training_model.summary()

    # 4. Kompilacija modela
    print("\n[KORAK 4/5] Kompilacija modela...")

    loss_function = get_triplet_loss_fn(
        margin_val=config.TRIPLET_MARGIN,
        emb_dim_val=config.EMBEDDING_DIM
    )

    triplet_training_model.compile(
        optimizer=Adam(learning_rate=config.LEARNING_RATE),
        loss=loss_function
    )
    print("Model uspešno kompajliran.")

    # 5. Učenje modela
    print("\n[KORAK 5/5] Začetek učenja modela...")

    checkpoint_filepath_triplet = os.path.join(config.MODEL_SAVE_DIR,
                                               f"triplet_model_best_ep{'{epoch:02d}'}_loss{'{val_loss:.2f}'}.keras")

    model_checkpoint_callback = ModelCheckpoint(
        filepath=checkpoint_filepath_triplet,
        save_weights_only=False,
        monitor='val_loss',
        mode='min',
        save_best_only=True,
        verbose=1
    )
    early_stopping_callback = EarlyStopping(
        monitor='val_loss',
        patience=10,
        verbose=1,
        restore_best_weights=True
    )
    reduce_lr_callback = ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.2,
        patience=5,
        verbose=1,
        min_lr=0.000001
    )
    log_dir_tensorboard = os.path.join(config.LOG_DIR, "fit", datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
    tensorboard_callback = TensorBoard(
        log_dir=log_dir_tensorboard,
        histogram_freq=1
    )

    callbacks_list = [
        model_checkpoint_callback,
        early_stopping_callback,
        reduce_lr_callback,
        tensorboard_callback
    ]

    history = triplet_training_model.fit(
        train_generator,
        epochs=config.EPOCHS,
        validation_data=val_generator,
        callbacks=callbacks_list,
        verbose=1
    )

    print("\n--- Učenje končano ---")

    final_embedding_model_path = os.path.join(config.MODEL_SAVE_DIR, config.EMBEDDING_MODEL_NAME)
    embedding_model.save(final_embedding_model_path)
    print(f"Končni Embedding model (z najboljšimi utežmi) shranjen v: {final_embedding_model_path}")

    print("\n--- Celoten proces učenja zaključen ---")


if __name__ == '__main__':
    gpus = tf.config.list_physical_devices('GPU')
    if gpus:
        try:
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
            print(f"Na voljo {len(gpus)} GPU(s), memory growth nastavljen.")
        except RuntimeError as e:
            print(e)
    else:
        print("GPU ni na voljo, model se bo učil na CPU.")

    train_model()