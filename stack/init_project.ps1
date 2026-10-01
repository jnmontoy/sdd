# ==============================================================================
# SCRIPT DE INICIALIZACIÓN AUTOMATIZADA DE PROYECTO — JOLIFOODS (SDD)
# ==============================================================================
# Permite crear el esqueleto completo de un nuevo proyecto a partir de .sdd

param(
    [string]$ProjectName
)

if (-not $ProjectName) {
    Write-Host "======================================================================" -ForegroundColor Cyan
    Write-Host "  INICIALIZADOR DE PROYECTO CORPORATIVO — JOLIFOODS (SDD)" -ForegroundColor Green
    Write-Host "======================================================================" -ForegroundColor Cyan
    $ProjectName = Read-Host "`n[Paso 0] Ingrese el nombre del nuevo proyecto o módulo"
}

if (-not $ProjectName) {
    Write-Host "El nombre no puede estar vacío." -ForegroundColor Red
    exit 1
}

$CurrentDir = Split-Path -Parent $MyInvocation.MyCommand.Path
python "$CurrentDir\init_project.py" "$ProjectName"

$Slug = ($ProjectName.ToLower() -replace '[^a-z0-9_\-\s]', '') -replace '[\s\-]+', '_'
$ProjectDir = Join-Path (Split-Path -Parent (Split-Path -Parent $CurrentDir)) $Slug
$VenvPython = Join-Path $ProjectDir ".venv\Scripts\python.exe"

if (Test-Path $VenvPython) {
    Write-Host "`n[VERIFICACIÓN] Entorno virtual verificado en: $VenvPython" -ForegroundColor Green
    Write-Host "[OK] Aislamiento garantizado. Cero dependencias en el Python global del equipo.`n" -ForegroundColor Green
} else {
    Write-Host "`n[ADVERTENCIA] No se detectó $VenvPython. Creando manualmente..." -ForegroundColor Yellow
    python -m venv (Join-Path $ProjectDir ".venv")
    if (Test-Path $VenvPython) {
        Write-Host "[OK] Entorno virtual .venv creado. Instalando requirements.txt..." -ForegroundColor Green
        & $VenvPython -m pip install -r (Join-Path $ProjectDir "backend\requirements.txt")
    }
}

