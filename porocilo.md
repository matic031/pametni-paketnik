# Poročilo - API in Integracija Sistema, 2FA

## Avtor: Matic Majerič

### Opravljene Naloge

1. **Razvoj REST API-ja za Obrazno Prepoznavo**

   - Implementacija API enpointov za registracijo in verifikacijo obraza
   - Integracija z modelom za prepoznavo obraza
   - Integracija 2FA registracije in verifikacije obraza uporabnika

2. **Docker Implementacija**

   - Kontejnerizacija face recognition API-ja
   - Konfiguracija Docker Compose za celoten sistem
   - Avtomatizacija zagona s start.sh skripto

#### API Endpointi

```javascript
POST /face/register - Registracija obraza uporabnika
POST /face/verify - Verifikacija s sliko
GET /face/status - Preverjanje stanja
DELETE /face/delete - Izbris podatkov obraza
```

#### Zagon Sistema

```bash
./start.sh
```

### Uporabljene Tehnologije

- Node.js/Express (Backend API)
- Flask (Face Recognition API)
- Docker & Docker Compose
- MongoDB (Shramba podatkov)
- JWT (Varnost)

### Rezultati

- Uspešna integracija face recognition modela
- Delujoč sistem za 2FA z obrazno prepoznavo
- Avtomatiziran zagon celotnega sistema

### Git Prispevki

```bash
git log --author="[Vaše Ime]" --pretty=format:"%h - %s" --since="1 month ago"
```

[Dodajte svoje git commit-e]
