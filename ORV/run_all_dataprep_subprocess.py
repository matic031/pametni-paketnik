import subprocess
import sys
import os  # Potreben za os.path.join

# --- Globalne nastavitve ---
PYTHON_EXECUTABLE = sys.executable  # Pot do Python interpreterja v trenutnem okolju

BASE_SCRIPT_PATH = os.getcwd()  # Trenutna delovna mapa

# Glavno stikalo za celoten cevovod
APPLY_DENOISING_PIPELINE = True  # True ali False


def run_script_with_args(script_name_no_ext, arguments_list=None):
    """Zažene podano Python skripto z argumenti."""
    script_full_path = os.path.join(BASE_SCRIPT_PATH, f"{script_name_no_ext}.py")
    command = [PYTHON_EXECUTABLE, script_full_path]

    if arguments_list:
        command.extend(arguments_list)

    print(f"  Zagon: {' '.join(command)}")
    try:
        # capture_output=True ujame stdout in stderr
        # text=True dekodira output kot tekst
        # check=True bo sprožil CalledProcessError, če skripta vrne napako (exit code != 0)
        process = subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8')
        print(f"    {script_name_no_ext}.py STDOUT:")
        if process.stdout:
            for line in process.stdout.strip().split('\n'):  # Izpis vsake vrstice posebej
                print(f"      {line}")
        print(f"    {script_name_no_ext}.py uspešno izveden.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"    NAPAKA pri izvajanju {script_name_no_ext}.py (exit code {e.returncode}):")
        print(f"    STDOUT: {e.stdout.strip()}")
        print(f"    STDERR: {e.stderr.strip()}")
        return False
    except FileNotFoundError:
        print(f"    NAPAKA: Skripta {script_full_path} ni najdena.")
        return False


def main_pipeline():
    print("--- ZAČETEK CELOTNE PRIPRAVE PODATKOV (s podprocesi) ---")

    # --- Korak 1: Zagotovi, da je LFW dataset prenesen ---
    print("\n[KORAK 1/3] Zagotavljanje lokalnega LFW dataseta...")
    if not run_script_with_args("download_lfw_dataset"):  # Ta skripta ne rabi argumentov
        print("Končujem cevovod zaradi napake v Koraku 1.")
        return
    print("[KORAK 1/3] LFW dataset je pripravljen lokalno.")

    # --- Korak 2: Predelava podatkov ---
    process_args = []
    if APPLY_DENOISING_PIPELINE:
        process_args.append("--denoise")

    print(
        f"\n[KORAK 2/3] Predelava LFW podatkov (Argumenti: {' '.join(process_args) if process_args else 'Brez --denoise'})...")
    if not run_script_with_args("process_lfw_data", process_args):
        print("Končujem cevovod zaradi napake v Koraku 2.")
        return
    print("[KORAK 2/3] Predelava LFW podatkov končana.")

    # --- Korak 3: Augmentacija učne množice ---
    augment_args = []
    if APPLY_DENOISING_PIPELINE:  # Predpostavimo, da augmentacija temelji na isti nastavitvi
        augment_args.append("--base_denoised")

    print(
        f"\n[KORAK 3/3] Augmentacija učne množice (Argumenti: {' '.join(augment_args) if augment_args else 'Brez --base_denoised'})...")
    if not run_script_with_args("augment_lfw_data", augment_args):
        print("Končujem cevovod zaradi napake v Koraku 3.")
        return
    print("[KORAK 3/3] Augmentacija končana.")

    print("\n--- CELOTNA PRIPRAVA PODATKOV USPEŠNO ZAKLJUČENA (s podprocesi) ---")


if __name__ == '__main__':
    main_pipeline()