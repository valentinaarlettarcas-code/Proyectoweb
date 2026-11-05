
# Verificacion del microservicio de Catalogo e Inventario.
# Ejecutar desde PowerShell.
# No modifica MongoDB ni realiza commits.

$ErrorActionPreference = 'Stop'

# Carpeta en la que se encuentra este script.
$raiz = $PSScriptRoot

# Seleccionar el interprete de Python.
# Prioridad:
# 1. Variable CATALOGO_PYTHON
# 2. Entorno virtual catalogo-web
# 3. Python disponible en PATH
$rutaVenv = Join-Path $HOME '.venvs\catalogo-web\Scripts\python.exe'

if ($env:CATALOGO_PYTHON) {
    $python = $env:CATALOGO_PYTHON
}
elseif (Test-Path $rutaVenv) {
    $python = $rutaVenv
}
else {
    $python = 'python'
}

# Variable temporal necesaria para Django.
if (-not $env:DJANGO_SECRET_KEY) {
    $env:DJANGO_SECRET_KEY = (
        [guid]::NewGuid().ToString('N') +
        [guid]::NewGuid().ToString('N')
    )
}

# Almacenar los resultados de cada comprobacion.
$resultados = @()

Push-Location $raiz

try {

    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host " VERIFICACION DE CATALOGO E INVENTARIO" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan

    Write-Host "`nDirectorio del servicio:" -ForegroundColor Yellow
    Write-Host (Get-Location).Path

    Write-Host "`nInterprete de Python:" -ForegroundColor Yellow
    & $python --version

    if ($LASTEXITCODE -ne 0) {
        throw "No fue posible ejecutar Python."
    }

    # ---------------------------------------------
    # 1. Comprobacion de Django
    # ---------------------------------------------

    Write-Host "`n=== Django check ===" -ForegroundColor Cyan

    & $python -B manage.py check

    $resultados += [PSCustomObject]@{
        Prueba   = 'Django check'
        ExitCode = $LASTEXITCODE
    }

    # ---------------------------------------------
    # 2. Pruebas HTTP y validaciones de Django
    # ---------------------------------------------

    Write-Host "`n=== Pruebas API completas ===" -ForegroundColor Cyan

    & $python -B manage.py test productos -v 2

    $resultados += [PSCustomObject]@{
        Prueba   = 'Django HTTP y validaciones'
        ExitCode = $LASTEXITCODE
    }

    # ---------------------------------------------
    # 3. Pruebas de inventario
    # ---------------------------------------------

    Write-Host "`n=== Pruebas inventario ===" -ForegroundColor Cyan

    Write-Host "Directorio de pruebas: $((Get-Location).Path)"

    # Los modulos ahora estan dentro de servicio_catalogo.
    # NO cambiar a la carpeta superior.

    & $python -B -m unittest -v test_operaciones_stock

    $resultados += [PSCustomObject]@{
        Prueba   = 'Inventario'
        ExitCode = $LASTEXITCODE
    }


    # ---------------------------------------------
    # 4. Comprobacion de rutas Django
    # ---------------------------------------------

    Write-Host "`n=== Rutas Django ===" -ForegroundColor Cyan

    $codigoRutas = @'
from django.urls import resolve

rutas = [
    '/api/productos/4/',
    '/api/productos/',
    '/api/reservas/',
    '/api/reservas/RES-001/consolidar/',
    '/api/reservas/RES-001/liberar/',
]

for ruta in rutas:
    resultado = resolve(ruta)
    print(ruta, '->', resultado.url_name)
'@

    & $python -B manage.py shell -c $codigoRutas

    $resultados += [PSCustomObject]@{
        Prueba   = 'Rutas API'
        ExitCode = $LASTEXITCODE
    }


    # ---------------------------------------------
    # 5. Informacion de Git
    # ---------------------------------------------

    Write-Host "`n=== Rama Git ===" -ForegroundColor Cyan

    & git branch --show-current

    Write-Host "`n=== Archivos modificados ===" -ForegroundColor Cyan

    & git -c core.longpaths=true status --short

    Write-Host "`n=== Ultimos 12 commits ===" -ForegroundColor Cyan

    & git -c core.longpaths=true log -12 --oneline

    # ---------------------------------------------
    # 6. Resumen de validaciones
    # ---------------------------------------------

    Write-Host "`n=== Resumen de validaciones ===" -ForegroundColor Cyan

    $resultados | Format-Table -AutoSize

    # Contar comprobaciones con codigo de error.
    $fallidas = @(
        $resultados | Where-Object {
            $null -eq $_.ExitCode -or [int]$_.ExitCode -ne 0
        }
    )

    if ($fallidas.Count -gt 0) {

        Write-Host "`nCOMPROBACIONES FALLIDAS:" -ForegroundColor Red

        $fallidas | Format-Table -AutoSize

        Write-Host "No realizar commit hasta corregir los errores." -ForegroundColor Red

    }
    else {

        Write-Host "`nTODAS LAS COMPROBACIONES AUTOMATIZADAS FUERON EXITOSAS." -ForegroundColor Green

        Write-Host "Revisar Git y dependencias reales antes del commit." -ForegroundColor Green
    }

}
finally {
    # Volver al directorio desde donde se ejecuto.
    Pop-Location
}

# Finalizar con codigo de error si alguna prueba fallo.
if ($fallidas.Count -gt 0) {
    exit 1
}

exit 0
