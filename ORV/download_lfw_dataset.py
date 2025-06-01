import tensorflow_datasets as tfds
import os

def ensure_lfw_dataset_is_local(project_data_path='data'):
    # Sestavi absolutno pot do ciljne mape
    # os.getcwd() vrne trenutno delovno mapo (kjer se skripta izvaja)
    target_data_dir = os.path.join(os.getcwd(), project_data_path)

    print(f"Preverjam/prenašam LFW dataset v lokalno mapo: {target_data_dir}")

    try:
        # Poskusi naložiti dataset. Če ta mapa ne obstaja, ga bo TFDS ustvaril.
        tfds.load(
            'lfw',
            split='train',
            with_info=False,
            as_supervised=False,
            data_dir=target_data_dir,   # Ciljna mapa, kjer bo shranjen dataset
            download=True        # Prenese, če še ni na voljo
        )
        print(f"LFW dataset je uspešno preverjen/prenesen/pripravljen v mapi: {target_data_dir}")
        print(f"V tej mapi bi morali zdaj imeti podmape, kot sta 'lfw' (s TFRecordi) in 'downloads'.")

    except Exception as e:
        print(f"Prišlo je do napake med zagotavljanjem LFW dataseta: {e}")
        print("Možni vzroki:")
        print("- Ni internetne povezave za prenos.")
        print("- Ni dovoljenj za pisanje v mapo.")
        print("- Težave s TFDS strežniki ali konfiguracijo.")

if __name__ == '__main__':
    # Klic funkcije za zagotovitev, da je LFW dataset lokalno shranjen
    ensure_lfw_dataset_is_local()
    