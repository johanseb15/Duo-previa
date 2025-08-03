# Backend (FastAPI)

Este directorio contiene el código del backend de la aplicación, desarrollado con FastAPI.

## Puesta en marcha local

1.  **Crear un entorno virtual:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    ```

2.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configurar variables de entorno:**
    - Renombra `.env.example` a `.env`.
    - Añade tu cadena de conexión de MongoDB Atlas a la variable `MONGODB_URI`.

4.  **Ejecutar la aplicación:**
    ```bash
    uvicorn main:app --reload
    ```

La API estará disponible en `http://127.0.0.1:8000`.

## Despliegue en Google Cloud Run

El despliegue se automatiza a través de GitHub Actions. El workflow se encuentra en `.github/workflows/backend-deploy.yml`.

Para que el despliegue funcione, necesitas:

1.  **Crear un proyecto en Google Cloud Platform.**
2.  **Habilitar las APIs de Cloud Build y Cloud Run.**
3.  **Crear una cuenta de servicio con los permisos necesarios** (Cloud Build Editor, Cloud Run Admin, Service Account User) y generar una clave JSON.
4.  **Guardar la clave JSON como un secreto en tu repositorio de GitHub** con el nombre `GCP_SA_KEY`.
5.  **Actualizar `cloudbuild.yaml`** con el ID de tu proyecto de GCP y el nombre de tu servicio de Cloud Run.
