import os

# --- Poti ---
BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)  # Starš src, torej face_recognition_project
DATA_DIR = os.path.join(BASE_DIR, "data")
MODEL_SAVE_DIR = os.path.join(BASE_DIR, "models")
LOG_DIR = os.path.join(BASE_DIR, "logs")

# Ustvari mape, če ne obstajajo
os.makedirs(MODEL_SAVE_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# --- Nastavitve podatkov ---
# Izberi, kateri dataset uporabiti glede na predhodno denoising nastavitev
# Spremeni to vrednost na True, če uporabljaš podatke, ki so bili denoised
DENOISING_WAS_APPLIED = False
FINAL_DATASET_FILENAME = (
    f"lfw_final_dataset_denoise-{str(DENOISING_WAS_APPLIED).lower()}.npz"
)
FINAL_DATASET_PATH = os.path.join(DATA_DIR, FINAL_DATASET_FILENAME)

# --- Nastavitve slik ---
IMG_HEIGHT = 64
IMG_WIDTH = 64
IMG_CHANNELS = 3

# --- Nastavitve modela in učenja ---
EMBEDDING_DIM = 128  # Dimenzionalnost izhodnega embedding vektorja
TRIPLET_MARGIN = 0.25  # Margin za triplet loss

# --- Hiperparametri učenja ---
LEARNING_RATE = 0.001  # Prilagojeno za Adam in triplet loss
BATCH_SIZE = 32
EPOCHS = 30  # Začni z manjšim številom za testiranje, npr. 10-20, potem povečaj

# Število trojčkov za generiranje na epoho (za TripletGenerator)
# Lahko je večje od dejanskega števila slik, saj se trojčki lahko ponavljajo
# ali pa manjše, če želimo hitrejše epohe na začetku.
# Če je None, bo generator poskusil ustvariti batch-e iz vseh možnih anchorjev.
# Za začetek je dobro imeti fiksno število, da so epohe primerljive.
# Npr., če imamo 10000 učnih slik, je to lahko 10000 ali 20000 itd.
NUM_TRAIN_TRIPLETS_PER_EPOCH = 20000  # Število trojčkov za eno epoho učenja
NUM_VAL_TRIPLETS_PER_EPOCH = 5000  # Število trojčkov za eno epoho validacije

# --- Nastavitve za shranjevanje modela ---
EMBEDDING_MODEL_NAME = f"face_embedding_model_dim{EMBEDDING_DIM}.keras"
TRIPLET_TRAINING_MODEL_NAME = f"face_triplet_training_model_dim{EMBEDDING_DIM}.keras"
