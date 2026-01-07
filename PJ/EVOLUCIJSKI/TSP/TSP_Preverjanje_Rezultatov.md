# TSP - Preverjanje Pravilnosti Rezultatov

## Kaj je TSP (Trgovski Potnik)
Problem trgovskega potnika - najdi najkrajšo pot, ki obišče vsa mesta natanko enkrat in se vrne na začetek.

## Kako Preveriti Rezultate

### 1. Osnovni Testi
```
Prva generacija: visoke razdalje (slabi rezultati)
Zadnja generacija: nižje razdalje (boljši rezultati)
```

### 2. Znani Optimalni Rezultati
| Instanca | Optimalna Razdalja | Tvoj Rezultat Naj Bo |
|----------|-------------------|---------------------|
| bays29   | 2020             | 2020-2500           |
| eil101   | 629              | 629-800             |
| a280     | 2579             | 2579-3200           |
| pr1002   | 259045           | 259045-320000       |
| dca1389  | ~80000           | 80000-120000        |

### 3. Kaj Gledati Pri Rezultatih

**✅ Pravilno:**
- Rezultati se izboljšujejo skozi generacije
- Končne razdalje so v zgornjih mejah
- Algoritem konča v ~1000×dimension evaluacij
- Isti seed → isti rezultati

**❌ Napačno:**
- Razdalje rastejo namesto padajo
- Rezultati > 10× optimalne vrednosti
- Algoritem se nikoli ne konča
- Različni rezultati z istim seedom

### 4. Preverjanje Implementacije

**Datoteke:**
- `.tsp` datoteke so pravilno prebrane
- Število mest se ujema z DIMENSION
- Razdalje niso 0 ali neskončne

**Algoritem:**
- Populacija: 100 osebkov
- Križanje: 80% verjetnost
- Mutacija: 10% verjetnost
- Elitizem: najboljši preživi

### 5. Tipične Napake

**Problem:** Vsi rezultati enaki
**Vzrok:** RandomUtils ni pravilno uporabljen

**Problem:** Razdalje previsoke
**Vzrok:** Napaka v calculateDistance()

**Problem:** Algoritem se nikoli ne konča
**Vzrok:** Napaka v while zanki (evaluacije)

### 6. Demonstracija Profesorju

1. **Pokaži datoteke:** "Podpiram EXPLICIT in EUC_2D formate"
2. **Pokaži teste:** "30 ponovitev za vsako instanco"
3. **Pokaži rezultate:** "Rezultati so v pričakovanih mejah"
4. **Pokaži izboljšave:** "Algoritem konvergira k boljšim rešitvam"

### 7. Ključne Besede za Razlago

- **Elitizem:** Najboljši ostane v naslednji generaciji
- **PMX križanje:** Ohranja permutacije (vsa mesta enkrat)
- **Swap mutacija:** Zamenja dve mesti v poti
- **Tournament selekcija:** Izbere boljšega od dveh naključnih

## Hitro Preverjanje
```bash
java TSPTest
# Pričakuj: 150 rezultatov (5 instanc × 30 ponovitev)
# Čas: 5-30 minut odvisno od velikosti
```