import cv2
import numpy as np
import os

# Pot do Haar kaskade
# Pravilna pot glede na strukturo projekta: ../models_data/
script_dir = os.path.dirname(os.path.abspath(__file__))
CASCADE_PATH = os.path.join(script_dir, '..', 'models_data', 'haarcascade_frontalface_default.xml')

if not os.path.exists(CASCADE_PATH):
    # Poskusimo najti v standardni poti OpenCV, če ni lokalno
    cv2_base_dir = os.path.dirname(os.path.abspath(cv2.__file__))
    haar_cascade_path_cv2 = os.path.join(cv2_base_dir, 'data', 'haarcascade_frontalface_default.xml')
    if os.path.exists(haar_cascade_path_cv2):
        CASCADE_PATH = haar_cascade_path_cv2
        print(f"Using Haar cascade from OpenCV data folder: {CASCADE_PATH}")
    else:
        raise FileNotFoundError(
            f"Haar cascade file not found. Expected at {CASCADE_PATH} or {haar_cascade_path_cv2}. "
            "Please download it from OpenCV's GitHub and place it in 'face_auth_project/models_data/' "
            "or ensure OpenCV is correctly installed with data files."
        )
try:
    face_cascade = cv2.CascadeClassifier(CASCADE_PATH)
    if face_cascade.empty():
        raise IOError(f"Could not load Haar cascade classifier from {CASCADE_PATH}")
except Exception as e:
    print(f"Error loading Haar cascade: {e}")
    # V primeru napake, naj modul ne prepreči zagona, ampak funkcija vrne None
    face_cascade = None


def detect_face(image_np_bgr):
    """
    Zazna največji obraz na sliki z Viola-Jones.
    :param image_np_bgr: NumPy array slike (naložena z OpenCV, torej BGR format).
    :return: Izrezan obraz (NumPy array, BGR) ali None, če obraz ni najden.
             Prav tako vrne koordinate (x, y, w, h) najdenega obraza ali None.
    """
    if face_cascade is None or face_cascade.empty():
        print("Error: Face cascade classifier not loaded.")
        return None, None

    if image_np_bgr is None or image_np_bgr.size == 0:
        print("Error: Input image to detect_face is empty or None.")
        return None, None

    # Pretvori v sivinsko sliko za detekcijo
    if len(image_np_bgr.shape) == 3 and image_np_bgr.shape[2] == 3:
        gray_image = cv2.cvtColor(image_np_bgr, cv2.COLOR_BGR2GRAY)
    elif len(image_np_bgr.shape) == 2:  # Že sivinska
        gray_image = image_np_bgr
    else:
        print(f"Error: Nepričakovana oblika slike za detect_face: {image_np_bgr.shape}")
        return None, None

    # Izenači histogram za boljšo odpornost na svetlobne razmere
    gray_image = cv2.equalizeHist(gray_image)

    faces = face_cascade.detectMultiScale(
        gray_image,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(60, 60)  # Povečamo minSize za bolj robustne detekcije na tipičnih slikah za prijavo
    )

    if len(faces) == 0:
        return None, None

    # Vrnemo največji obraz
    faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)
    x, y, w, h = faces[0]

    # Izrežemo obraz iz originalne BGR slike
    # Dodamo malo "paddinga" okoli obraza, da ne odrežemo preveč las/brade
    padding_h = int(h * 0.15)  # 15% vertikalnega paddinga
    padding_w = int(w * 0.10)  # 10% horizontalnega paddinga

    y1 = max(0, y - padding_h)
    y2 = min(image_np_bgr.shape[0], y + h + padding_h)
    x1 = max(0, x - padding_w)
    x2 = min(image_np_bgr.shape[1], x + w + padding_w)

    face_roi_bgr = image_np_bgr[y1:y2, x1:x2]

    if face_roi_bgr.shape[0] == 0 or face_roi_bgr.shape[1] == 0:
        # V primeru, da padding povzroči neveljaven izrez (obraz na robu slike)
        face_roi_bgr = image_np_bgr[y:y + h, x:x + w]  # Vrnemo brez paddinga
        if face_roi_bgr.shape[0] == 0 or face_roi_bgr.shape[1] == 0:
            return None, None  # Še vedno neveljaven

    return face_roi_bgr, (x, y, w, h)