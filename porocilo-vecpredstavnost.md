# Poročilo: FLoCIC kompresija v projektu Pametni Paketnik

**Avtor:** Matic Majerič
**Predmet:** Večpredstavnost
**Datum:** 25. januar 2026

---

## Opis integracije

Algoritem **FLoCIC** (Fast Lossless COmpression for Images using interpolative Coding) je bil integriran v sistem za prepoznavo obrazov (**ORV modul**) projekta Pametni Paketnik. Kompresija se uporablja za **arhiviranje sivinskih slik obrazov** uporabnikov ob registraciji.

### Lokacija implementacije

| Datoteka | Opis |
|----------|------|
| `compression/flocic.py` | FLoCIC algoritem (JPEG-LS + interpolativno kodiranje) |
| `compression/image_compressor.py` | Wrapper za integracijo z face recognition |
| `compression/test.py` | Testiranje kompresije na vzorcnih slikah |
| `ORV/face_recognition_api.py` | Integracija v REST API |

---

## Zaslonske slike

### 1. FLoCIC algoritem - interpolativno kodiranje

![FLoCIC algoritem](./screenshots/1.png)

*Jedro FLoCIC algoritma: JPEG-LS MED prediktor in interpolativno kodiranje.*

---

### 2. Integracija v Face Recognition API

![Integracija v API](./screenshots/2.png)

*Klic kompresije ob registraciji uporabnika v `face_recognition_api.py`.*

---

### 3. API odgovor s podatki o kompresiji

![API odgovor](./screenshots/3.png)

*REST API vrne razmerje kompresije pri uspešni registraciji.*

---

### 4. Shramba kompresiranih slik

![Kompresiran arhiv](./screenshots/4.png)

*Kompresirane slike (.fic) se shranjujejo v `data_storage/compressed_faces/`.*

---

### 5. Statistika kompresije

![Statistika](./screenshots/5.png)

*Endpoint `/compression/stats` vrne statistiko prihranjenega prostora.*

---

## Rezultati

- **Povprečno razmerje kompresije:** ~2-3x za sivinske slike obrazov 128x128
- **Brezizgubna kompresija:** Dekompresirana slika je identična originalu
- **Avtomatsko arhiviranje:** Vsaka registracija uporabnika shrani kompresirano sliko
