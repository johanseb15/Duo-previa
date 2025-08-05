# EnvSetup.psm1

function Test-Command {
    param([string]$cmd)
    $null -ne (Get-Command $cmd -ErrorAction SilentlyContinue)
}

function Check-CL {
    Write-Host "`n Verificando compilador C++ (cl.exe)..."
    if (-not (Test-Command "cl.exe")) {
        Write-Warning "❌ No se encontró el compilador C++ (cl.exe)."
        $response = Read-Host "¿Querés instalar los Build Tools automáticamente? (s/n)"
        if ($response -eq "s") {
            Install-BuildTools
        } else {
            Write-Host "➡ Descargalos manualmente desde: https://visualstudio.microsoft.com/visual-cpp-build-tools/"
        }
        return $false
    }
    Write-Host "✅ cl.exe está disponible."
    return $true
}

function Install-BuildTools {
    $installerUrl = "https://aka.ms/vs/17/release/vs_BuildTools.exe"
    $installerPath = "$env:TEMP\vs_BuildTools.exe"
    Invoke-WebRequest -Uri $installerUrl -OutFile $installerPath
    Start-Process -FilePath $installerPath -ArgumentList \
        "--quiet --wait --norestart --nocache --installPath \"C:\BuildTools\" --add Microsoft.VisualStudio.Workload.VCTools" \
        -Verb RunAs
}

function Check-Python {
    Write-Host "`n Verificando Python..."
    if (-not (Test-Command "python")) {
        Write-Warning "❌ Python no está instalado."
        Write-Host "➡ Descargalo desde: https://www.python.org/downloads/"
        return $false
    }
    Write-Host "✅ Python está disponible: $(python --version)"
    return $true
}

function Check-Node {
    Write-Host "`n Verificando Node.js..."
    if (-not (Test-Command "node")) {
        Write-Warning "❌ Node.js no está instalado."
        Write-Host "➡ Descargalo desde: https://nodejs.org/"
        return $false
    }
    Write-Host "✅ Node.js está disponible: $(node --version)"
    return $true
}

function Check-Git {
    Write-Host "`n Verificando Git..."
    if (-not (Test-Command "git")) {
        Write-Warning "❌ Git no está instalado."
        Write-Host "➡ Descargalo desde: https://git-scm.com/downloads"
        return $false
    }
    Write-Host "✅ Git está disponible: $(git --version)"
    return $true
}

function Check-Venv {
    Write-Host "`n Verificando entorno virtual..."
    if (-not (Test-Path ".venv")) {
        Write-Host " No se encontró '.venv'. Creando entorno virtual..."
        python -m venv .venv
    }

    $activateScript = ".\.venv\Scripts\Activate.ps1"
    if (Test-Path $activateScript) {
        Write-Host "✅ Activando entorno virtual..."
        & $activateScript
    } else {
        Write-Warning "❌ No se pudo activar el entorno virtual."
    }
}

function Confirm-Continue {
    $response = Read-Host "`n¿Querés continuar con la instalación? (s/n)"
    return $response -eq "s"
}

function Run-EnvironmentSetup {
    Write-Host "`n Iniciando verificación del entorno..."

    $checks = @(
        Check-CL,
        Check-Python,
        Check-Node,
        Check-Git
    )

    $allOk = $true
    foreach ($check in $checks) {
        if (-not (& $check)) {
            $allOk = $false
        }
    }

    if (-not $allOk) {
        Write-Warning "`n⚠️ Faltan componentes necesarios. Instalalos y volvé a ejecutar el script."
        return
    }

    Check-Venv

    if (Confirm-Continue) {
        Write-Host "`n Instalando dependencias..."
        pip install -r requirements.txt
        Write-Host "`n✅ Instalación completada."
    } else {
        Write-Host "`n⏹ Instalación cancelada por el usuario."
    }
}
