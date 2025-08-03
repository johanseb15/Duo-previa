# Frontend (Next.js)

Este directorio contiene el código del frontend de la aplicación, desarrollado con Next.js.

## Puesta en marcha local

1.  **Instalar dependencias:**
    ```bash
    npm install
    ```

2.  **Ejecutar la aplicación:**
    ```bash
    npm run dev
    ```

La aplicación estará disponible en `http://localhost:3000`.

## Despliegue en Vercel

El despliegue se automatiza a través de GitHub Actions. El workflow se encuentra en `.github/workflows/frontend-deploy.yml`.

Para que el despliegue funcione, necesitas:

1.  **Crear un proyecto en Vercel.**
2.  **Obtener un token de Vercel.**
3.  **Guardar los siguientes secretos en tu repositorio de GitHub:**
    - `VERCEL_TOKEN`: Tu token de Vercel.
    - `VERCEL_ORG_ID`: El ID de tu organización en Vercel.
    - `VERCEL_PROJECT_ID`: El ID de tu proyecto en Vercel.