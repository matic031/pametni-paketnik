# FLoCIC - Kompresija sivinskih BMP slik

## Uporaba

### Kompresija
```bash
python flocic.py compress vhodna_slika.bmp izhodna_datoteka.fic
```

### Dekompresija
```bash
python flocic.py decompress vhodna_datoteka.fic izhodna_slika.bmp
```

### Testiranje na 10 slikah iz slikeBMP direktorija
```bash
python test.py
```

Rezultati testiranja se izpišejo v konzoli.
Dekompresirane slike se shranijo v `output/` direktorij.
Kompresirane datoteke se shranijo v `compressed/` direktorij.

---

### Primer Man.bmp
```bash
python flocic.py compress slikeBMP/Man.bmp Man_compressed.fic
python flocic.py decompress Man_compressed.fic Man_decompressed.bmp
```
