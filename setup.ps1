Write-Host "`n Iniciando instalación limpia de Duo-previa..."

# Verificar Rust y Cargo
Write-Host "`n Verificando instalación de Rust y Cargo..."
if (-not (Get-Command cargo -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Cargo no está instalado o no está en el PATH."
    Write-Host "➡️ Instalalo desde https://rustup.rs y reiniciá PowerShell."
    exit
} else {
    Write-Host "✅ Rust y Cargo están disponibles."
}

# Backend
Write-Host "`n Instalando dependencias del backend..."
if (Test-Path "backend") {
    cd backend
    if (Test-Path "requirements.txt") {
        pip install -r requirements.txt
    } else {
        Write-Host "❌ No se encontró requirements.txt en backend."
        exit
    }

    # Verificar archivo .env
    if (-not (Test-Path ".env")) {
        Write-Host "⚠️ backend/.env no encontrado. Crealo manualmente si es necesario."
    } else {
        Write-Host "✅ backend/.env encontrado."
    }

    # Lanzar backend
    Write-Host "`n Lanzando backend en puerto 8000..."
    Start-Process powershell -ArgumentList "uvicorn main:app --reload --host 0.0.0.0 --port 8000" -WindowStyle Hidden
    Start-Sleep -Seconds 5
    cd ..
} else {
    Write-Host "❌ Carpeta 'backend' no encontrada."
    exit
}

# Frontend
Write-Host "`n Instalando dependencias del frontend..."
if (Test-Path "frontend") {
    cd frontend
    if (Test-Path "package.json") {
        npm install
    } else {
        Write-Host "❌ No se encontró package.json en frontend."
        exit
    }

    Write-Host "`n Lanzando frontend en puerto 5173..."
    Start-Process powershell -ArgumentList "npm run dev" -WindowStyle Hidden
    Start-Sleep -Seconds 5
    cd ..
} else {
    Write-Host "❌ Carpeta 'frontend' no encontrada."
    exit
}

Write-Host "`n✅ Instalación completa. Duo-previa está corriendo."
Write-Host " Backend: http://localhost:8000"
Write-Host " Frontend: http://localhost:5173"
