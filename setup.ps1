$logFile = "setup.log"
function Log {
    param ([string]$message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $entry = "$timestamp - $message"
    Write-Host $message
    Add-Content -Path $logFile -Value $entry
}

Log "`n Iniciando instalación limpia de Duo-previa..."

# Verificar Rust y Cargo
Log "`n Verificando instalación de Rust y Cargo..."
if (-not (Get-Command cargo -ErrorAction SilentlyContinue)) {
    Log "❌ Cargo no está instalado o no está en el PATH."
    Log "➡️ Instalalo desde https://rustup.rs y reiniciá PowerShell."
    exit
} else {
    Log "✅ Rust y Cargo están disponibles."
}

# Backend
Log "`n Instalando dependencias del backend..."
if (Test-Path "backend") {
    cd backend
    if (Test-Path "requirements.txt") {
        try {
            pip install -r requirements.txt 2>&1 | Tee-Object -Variable pipOutput
            $pipOutput | Add-Content -Path $logFile
        } catch {
            Log "❌ Error al instalar dependencias del backend: $_"
            exit
        }
    } else {
        Log "❌ No se encontró requirements.txt en backend."
        exit
    }

    if (-not (Test-Path ".env")) {
        Log "⚠️ backend/.env no encontrado."
    } else {
        Log "✅ backend/.env encontrado."
    }

    Log "`n Lanzando backend..."
    Start-Process powershell -ArgumentList "uvicorn main:app --reload --host 0.0.0.0 --port 8000" -WindowStyle Hidden
    Start-Sleep -Seconds 5
    cd ..
} else {
    Log "❌ Carpeta 'backend' no encontrada."
    exit
}

# Frontend
Log "`n Instalando dependencias del frontend..."
if (Test-Path "frontend") {
    cd frontend
    if (Test-Path "package.json") {
        try {
            npm install 2>&1 | Tee-Object -Variable npmOutput
            $npmOutput | Add-Content -Path $logFile
        } catch {
            Log "❌ Error al instalar dependencias del frontend: $_"
            exit
        }
    } else {
        Log "❌ No se encontró package.json en frontend."
        exit
    }

    Log "`n Lanzando frontend..."
    Start-Process powershell -ArgumentList "npm run dev" -WindowStyle Hidden
    Start-Sleep -Seconds 5
    cd ..
} else {
    Log "❌ Carpeta 'frontend' no encontrada."
    exit
}

Log "`n✅ Instalación completa. Duo-previa está corriendo."
Log " Backend: http://localhost:8000"
Log " Frontend: http://localhost:5173"