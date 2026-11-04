# Envoltorio de Windows para init_project.py (compatible con Windows PowerShell 5.1 y PowerShell 7).
# Usa el Python del sistema solo para ejecutar el generador (librería estándar) y crear .venv;
# las dependencias se instalan exclusivamente dentro del .venv del proyecto (BP-15).
param(
    [string]$ProjectName,
    [switch]$SinInstalar
)

$Script = Join-Path $PSScriptRoot "init_project.py"
$Python = Get-Command py -ErrorAction SilentlyContinue
if (-not $Python) { $Python = Get-Command python -ErrorAction SilentlyContinue }
if (-not $Python) {
    Write-Host "No se encontró Python 3 (py o python) en el PATH." -ForegroundColor Red
    exit 1
}

$PyArgs = @($Script)
if ($ProjectName) { $PyArgs += $ProjectName }
if ($SinInstalar) { $PyArgs += "--sin-instalar" }

& $Python.Source @PyArgs
exit $LASTEXITCODE
