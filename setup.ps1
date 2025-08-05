# Verifica si Python está disponible
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "`n❌ Python no se encontró. Por favor, instalá Python 3.x."
    Write-Host " Puedes descargarlo desde: https://www.python.org/downloads/"
    exit 1
}

# Verifica si el archivo requirements.txt existe
if (-not (Test-Path "backend/requirements.txt")) {
    Write-Host "`n❌ El archivo 'backend/requirements.txt' no se encontró."
    Write-Host " Asegurate de que el proyecto esté completo y que este archivo exista."
    exit 1
}

# Verifica si el compilador C++ está disponible
if (-not (Get-Command cl.exe -ErrorAction SilentlyContinue)) {
    Write-Host "`n❌ No se encontró el compilador C++ (cl.exe)."
    Write-Host " Esto es necesario para compilar dependencias como aiohttp y pydantic-core."
    Write-Host "`n➡️ Solución:"
    Write-Host "1. Descargá los Build Tools desde: https://visualstudio.microsoft.com/visual-cpp-build-tools/"
    Write-Host "2. Instalá el componente 'Desktop development with C++'."
    Write-Host "3. Reiniciá tu computadora y volvé a ejecutar este script."
    exit 1
}

Write-Host "`n✅ Compilador C++ detectado. Continuando con la instalación de dependencias..."

# Activar entorno virtual si existe
if (Test-Path ".venv") {
    Write-Host " Activando entorno virtual..."
    .\.venv\Scripts\Activate.ps1
} else {
    Write-Host "⚠️ No se encontró el entorno virtual. Creando uno..."
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
}

# Instalar dependencias
Write-Host "`n Instalando dependencias..."
pip install --upgrade pip
pip install -r backend/requirements.txt

Write-Host "`n Instalación completada con éxito."