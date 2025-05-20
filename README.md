# Pametni paketnik 📦

### Navodila za namestitev
navodila  
---

## Running the Backend Database (MongoDB with Docker)

1.  **Configure Environment Variables:**
    *   In the project's root directory (where `docker-compose.yml` is located), copy `.env.example` to `.env`:
        ```bash
        cp .env.example .env
        ```
    *   Edit the new `.env` file and fill in your `MONGO_ROOT_USER` and `MONGO_ROOT_PASSWORD`.

2.  **Start the Database:**
    *   Ensure you are in the project's root directory.
    *   Run:
        ```bash
        docker-compose up -d
        ```
    *   This will start the MongoDB database in the background.

---
