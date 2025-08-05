# setup.ps1

function Test-Port {
    param ([int]$Port)
    $tcp = New-Object System.Net.Sockets.TcpClient
    try {
        $tcp.Connect("localhost", $Port)
        $tcp.Close()
        return $true
    } catch {
        return $false
    }
}

function Test-MongoConnection {
    try {
        $envVars = Get-Content "./backend/.env" | Where-Object { $_ -match "^MONGODB_URL=" }
        $mongoUrl = $envVars -replace "MONGODB_URL=", ""
        python -c "from motor.motor_asyncio import AsyncIOMotorClient; import asyncio; async def test(): client = AsyncIOMotorClient('$mongoUrl'); await client.server_info(); print('✅ MongoDB conectado'); asyncio.run(test())"        
return $true
    } catch {
        Write-Host "❌ Error al conectar con MongoDB" -ForegroundColor Red
        return $false
    }
}

Write-Host " Iniciando instalación limpia de Duo-previa..." -ForegroundColor Cyan

# Backend
Write-Host "`n Instalando dependencias del backend..." -ForegroundColor Yellow
cd backend
pip install -r requirements.txt

# .env
if (-Not (Test-Path ".env")) {
    Write-Host "`n⚠️ backend/.env no encontrado. Creando desde .env.example..." -ForegroundColor Red
    Copy-Item ".env.example" ".env"
} else {
    Write-Host "`n✅ backend/.env encontrado." -ForegroundColor Green
}

# Lanzar backend
Write-Host "`n Lanzando backend..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "cd backend; uvicorn main:app --reload --host 0.0.0.0 --port 8000"
Start-Sleep -Seconds 10
if (Test-Port -Port 8000) {
    Write-Host "✅ Backend corriendo en http://localhost:8000" -ForegroundColor Green
} else {
    Write-Host "❌ Backend no respondió en el puerto 8000" -ForegroundColor Red
}

# MongoDB
Write-Host "`n Verificando conexión a MongoDB..." -ForegroundColor Yellow
Test-MongoConnection

# Datos de ejemplo
Write-Host "`n Inicializando datos de ejemplo..." -ForegroundColor Yellow
python init_sample_data.py

# Frontend
Write-Host "`n Instalando dependencias del frontend..." -ForegroundColor Yellow
cd ../frontend
npm install

# Lanzar frontend
Write-Host "`n Lanzando frontend..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "npm run dev"
Start-Sleep -Seconds 10
if (Test-Port -Port 5173) {
    Write-Host "✅ Frontend corriendo en http://localhost:5173" -ForegroundColor Green
} else {
    Write-Host "❌ Frontend no respondió en el puerto 5173" -ForegroundColor Red
}

Write-Host "`n Instalación completa. Duo-previa está corriendo." -ForegroundColor Cyan
