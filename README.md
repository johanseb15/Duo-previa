# Duo Previa - PWA con React, FastAPI y Vertex AI

Este proyecto es una Progressive Web App (PWA) completa con un frontend en React, un backend en FastAPI y una integración con Google Cloud Vertex AI para capacidades de IA generativa.

## Arquitectura

- **Frontend**: Desarrollado con React (Vite) y estilizado con Tailwind CSS. Implementa funcionalidades PWA para una experiencia de usuario mejorada, incluyendo capacidad offline y la posibilidad de ser instalada en dispositivos.
- **Backend**: Construido con FastAPI (Python), proporcionando una API RESTful para la comunicación con el frontend y la interacción con la base de datos y servicios de IA.
- **IA**: Integración con Google Cloud Vertex AI para utilizar modelos generativos (como Gemini) para la generación de texto.
- **Base de Datos**: MongoDB (la conexión se gestiona mediante variables de entorno).
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
│   │   ├── App.tsx
│   │   └── index.css
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── package.json
│   └── ... (otros archivos generados por Vite)
├── SETUP.md
├── setup.sh
└── README.md
```

## Configuración del Entorno Local

Sigue estos pasos para configurar y ejecutar el proyecto localmente:

1.  **Clona el repositorio:**
    ```bash
    git clone https://github.com/johanseb15/Duo-previa.git
    cd Duo-previa
    ```

2.  **Ejecuta el script de configuración inicial:**
    Este script instalará todas las dependencias necesarias para el frontend y el backend.
    ```bash
    # En Linux/macOS, asegúrate de que sea ejecutable:
    # chmod +x setup.sh
    ./setup.sh
    ```

3.  **Configura las variables de entorno:**
    Crea un archivo `.env` en la carpeta `backend/` y configura las variables de entorno necesarias para la conexión a la base de datos y otros servicios. Puedes usar `backend/.env.example` como referencia.

4.  **Inicia el Backend:**
    ```bash
    cd backend
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
    ```

5.  **Inicia el Frontend:**
    ```bash
    cd frontend
    npm run dev
    ```

Para una configuración más detallada, incluyendo la inicialización de datos de ejemplo y la ejecución de pruebas, consulta el archivo `SETUP.md` en la raíz del proyecto.

## Despliegue Continuo (CI/CD) con GitHub Actions

Este proyecto está configurado para el despliegue automático a través de GitHub Actions. Consulta el archivo `SETUP.md` para obtener detalles sobre la configuración de secretos y los workflows de despliegue.

## Uso de PWABuilder (Post-Despliegue)

Una vez que tu frontend esté desplegado en Vercel, puedes usar la CLI de PWABuilder para generar paquetes para tiendas de aplicaciones (Android, Windows, etc.). Consulta el archivo `SETUP.md` para obtener instrucciones detalladas.
