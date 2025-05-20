# React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.

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