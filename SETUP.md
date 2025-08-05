# Instalación de Duo-previa (Windows)

Este proyecto incluye un script automatizado para configurar el entorno local en Windows.

## Requisitos

- Python 3.11+
- Node.js 18+
- PowerShell 5+
- MongoDB Atlas (o local)
- Git

## Instalación rápida

1.  Clona el repositorio:
    ```bash
    git clone https://github.com/johanseb15/Duo-previa.git
    cd Duo-previa
    ```
2.  Ejecuta el script:
    ```powershell
    Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
    .\setup.ps1
    ```

## ¿Qué hace el script?

- Instala dependencias del backend y frontend.
- Verifica y crea `.env` si falta.
- Lanza servidores en nuevas ventanas.
- Verifica conexión a MongoDB.
- Inicializa datos de ejemplo.
- Valida puertos 8000 y 5173.

## Pruebas

Para ejecutar tests del backend:

```bash
cd backend
pytest
```