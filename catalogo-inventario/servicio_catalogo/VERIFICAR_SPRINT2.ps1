# Ejecutar dentro de servicio_catalogo. No altera MongoDB ni crea commits.
$ErrorActionPreference = 'Stop'
$raiz = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $raiz
try {
    if (-not $env:DJANGO_SECRET_KEY) {
        $env:DJANGO_SECRET_KEY = (& python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
    }
    $resultados = @()
    Write-Host "`n=== Django check ===" -ForegroundColor Cyan
    & python manage.py check
    $resultados += [PSCustomObject]@{Prueba='Django check';ExitCode=$LASTEXITCODE}

    Write-Host "`n=== Pruebas API completas ===" -ForegroundColor Cyan
    & python manage.py test productos -v 2
    $resultados += [PSCustomObject]@{Prueba='Django HTTP y validaciones';ExitCode=$LASTEXITCODE}

    Write-Host "`n=== Pruebas inventario ===" -ForegroundColor Cyan
    Push-Location ..
    try {
        & python -B -m unittest -v test_operaciones_stock
        $resultados += [PSCustomObject]@{Prueba='Inventario';ExitCode=$LASTEXITCODE}
    }
    finally { Pop-Location }

    Write-Host "`n=== Rutas Django ===" -ForegroundColor Cyan
    & python manage.py shell -c "from django.urls import resolve; rutas=['/api/productos/4/', '/api/productos/', '/api/reservas/', '/api/reservas/RES-001/consolidar/', '/api/reservas/RES-001/liberar/']; print([(ruta, resolve(ruta).url_name) for ruta in rutas])"
    $resultados += [PSCustomObject]@{Prueba='Rutas API';ExitCode=$LASTEXITCODE}

    Write-Host "`n=== Rama Git ===" -ForegroundColor Cyan
    & git -c core.longpaths=true branch --show-current
    Write-Host "`n=== Archivos modificados ===" -ForegroundColor Cyan
    & git -c core.longpaths=true status --short
    Write-Host "`n=== Ultimos 12 commits ===" -ForegroundColor Cyan
    & git -c core.longpaths=true log -12 --oneline
    Write-Host "`n=== Resumen de validaciones ===" -ForegroundColor Cyan
    $resultados | Format-Table -AutoSize
    if (($resultados | Where-Object { $_.ExitCode -ne 0 }).Count -gt 0) {
        Write-Host 'Hay comprobaciones pendientes o fallidas. NO realizar commit aun.' -ForegroundColor Red
        exit 1
    }
    Write-Host 'Comprobaciones automatizadas OK. Revisar estado Git y dependencias reales.' -ForegroundColor Green
}
finally { Pop-Location }
