# Duo Previa - PWA con React, FastAPI y Vertex AI

Este proyecto es una Progressive Web App (PWA) completa con un frontend en React, un backend en FastAPI y una integración con Google Cloud Vertex AI para capacidades de IA generativa. 

## Arquitectura

- **Frontend**: Desarrollado con React (Vite) y estilizado con Tailwind CSS. Implementa funcionalidades PWA para una experiencia de usuario mejorada, incluyendo capacidad offline y la posibilidad de ser instalada en dispositivos.
- **Backend**: Construido con FastAPI (Python), proporcionando una API RESTful para la comunicación con el frontend y la interacción con la base de datos y servicios de IA.
- **IA**: Integración con Google Cloud Vertex AI para utilizar modelos generativos (como Gemini) para la generación de texto.
- **Base de Datos**: Preparado para MongoDB (la conexión se gestiona mediante variables de entorno).
- **CI/CD**: Configurado con GitHub Actions para el despliegue continuo del frontend a Vercel y del backend a Google Cloud Run.

## Estructura del Proyecto

```
. Duo-previa/
├── .github/
│   └── workflows/
│       ├── backend-deploy.yml
│       └── frontend-deploy.yml
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
├── frontend/
│   ├── public/
│   │   └── manifest.json
│   ├── src/
│   │   ├── App.jsx
│   │   └── index.css
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── package.json
│   └── ... (otros archivos generados por Vite)
└── README.md
```

## Configuración del Entorno Local

### Backend

1.  **Navega al directorio `backend`:**
    ```bash
    cd backend
    ```
2.  **Crea un entorno virtual e instala las dependencias:**
    ```bash
    python -m venv venv
    .env\Scripts\activate  # En Windows
    # source venv/bin/activate # En macOS/Linux
    pip install -r requirements.txt
    ```
3.  **Crea un archivo `.env`:**
    Copia el contenido de `.env.example` a un nuevo archivo llamado `.env` en el directorio `backend` y rellena las variables:
    ```
    MONGODB_URI=
    GCP_PROJECT_ID=tu-id-de-proyecto-gcp
    GCP_REGION=us-central1 # O tu región de GCP
    ```
    Asegúrate de que tu cuenta de servicio de GCP (usada para `GCP_SA_KEY` en CI/CD) tenga el rol `Vertex AI User` (`roles/aiplatform.user`) para que el backend pueda interactuar con Vertex AI.
4.  **Inicia el servidor FastAPI:**
    ```bash
    uvicorn main:app --reload --host 0.0.0.0 --port 8080
    ```
    El backend estará disponible en `http://localhost:8080`.

### Frontend

1.  **Navega al directorio `frontend`:**
    ```bash
    cd frontend
    ```
2.  **Instala las dependencias:**
    ```bash
    npm install
    ```
3.  **Inicia el servidor de desarrollo de Vite:**
    ```bash
    npm run dev
    ```
    El frontend estará disponible en `http://localhost:5173` (o el puerto que Vite asigne). Las llamadas a `/api` serán redirigidas al backend en `http://localhost:8080` gracias a la configuración de proxy en `vite.config.js`.

## Despliegue Continuo (CI/CD) con GitHub Actions

Este proyecto está configurado para el despliegue automático a través de GitHub Actions.

### Secretos de GitHub

Para que los workflows de CI/CD funcionen correctamente, necesitas configurar los siguientes secretos en tu repositorio de GitHub (Settings -> Secrets and variables -> Actions):

-   **`VERCEL_TOKEN`**: Token de API personal de Vercel para el despliegue del frontend.
-   **`VERCEL_ORG_ID`**: ID de tu organización de Vercel.
-   **`VERCEL_PROJECT_ID`**: ID de tu proyecto de Vercel.
-   **`GCP_SA_KEY`**: La clave JSON de tu cuenta de servicio de Google Cloud. Esta cuenta debe tener los permisos necesarios para desplegar en Cloud Run y acceder a Vertex AI (rol `Vertex AI User`).
-   **`GCP_PROJECT_ID`**: El ID de tu proyecto de Google Cloud.

### Workflows

-   **`frontend-deploy.yml`**: Se activa en cada `push` a la rama `main` en el directorio `frontend/`. Construye y despliega la PWA a Vercel.
-   **`backend-deploy.yml`**: Se activa en cada `push` a la rama `main` en el directorio `backend/`. Construye la imagen Docker del backend y la despliega a Google Cloud Run.

## Uso de PWABuilder (Post-Despliegue)

Una vez que tu frontend esté desplegado en Vercel, puedes usar la CLI de PWABuilder para generar paquetes para tiendas de aplicaciones (Android, Windows, etc.):

1.  **Instala la CLI de PWABuilder globalmente:**
    ```bash
    npm install -g @pwabuilder/cli
    ```
2.  **Ejecuta PWABuilder apuntando a la URL de tu aplicación desplegada:**
    ```bash
    pwabuilder <URL_DE_TU_APP_EN_VERCEL> -d . -p android,windows
    ```
    Esto generará los paquetes listos para subir a las respectivas tiendas.
