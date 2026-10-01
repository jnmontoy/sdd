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
