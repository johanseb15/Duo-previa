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

## Instalación

Para obtener instrucciones detalladas sobre cómo configurar y ejecutar el proyecto en tu entorno local, consulta el archivo [`SETUP.md`](SETUP.md). Esta guía incluye:

-   Instrucciones para **Windows** (con un script de PowerShell automatizado) y **Linux/macOS**.
-   Configuración de variables de entorno.
-   Inicialización de datos de ejemplo.
-   Ejecución de pruebas.


## Despliegue Continuo (CI/CD) con GitHub Actions

Este proyecto está configurado para el despliegue automático a través de GitHub Actions. Consulta el archivo `SETUP.md` para obtener detalles sobre la configuración de secretos y los workflows de despliegue.

## Uso de PWABuilder (Post-Despliegue)

Una vez que tu frontend esté desplegado en Vercel, puedes usar la CLI de PWABuilder para generar paquetes para tiendas de aplicaciones (Android, Windows, etc.). Consulta el archivo `SETUP.md` para obtener instrucciones detalladas.
