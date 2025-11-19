@echo off
REM Script para verificar conexión a Cerbos, reiniciar y probar conexión con backend (Windows)

echo === Script de Verificacion y Reinicio de Cerbos ===
echo.

REM 1. Verificar que Docker este corriendo
echo [1/7] Verificando Docker...
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker no esta corriendo. Por favor inicia Docker Desktop.
    exit /b 1
)
echo [OK] Docker esta corriendo
echo.

REM 2. Verificar archivos de configuración de Cerbos
echo [2/7] Verificando archivos de configuracion de Cerbos...
if not exist "..\backend\cerbos\config.yaml" (
    echo [ERROR] No se encontro config.yaml en backend\cerbos\
    exit /b 1
)
echo [OK] Archivo de configuracion encontrado

if not exist "..\backend\cerbos\policies\" (
    echo [ERROR] No se encontro directorio de politicas en backend\cerbos\policies\
    exit /b 1
)
echo [OK] Directorio de politicas encontrado
echo.

REM 3. Detener contenedor Cerbos si está corriendo
echo [3/7] Deteniendo contenedor Cerbos existente...
docker ps --format "{{.Names}}" | findstr /C:"roska_cerbos" >nul
if not errorlevel 1 (
    docker-compose stop cerbos
    echo [OK] Contenedor Cerbos detenido
) else (
    echo Contenedor no estaba corriendo
)

REM 4. Eliminar contenedor Cerbos
echo [4/7] Eliminando contenedor Cerbos...
docker ps -a --format "{{.Names}}" | findstr /C:"roska_cerbos" >nul
if not errorlevel 1 (
    docker-compose rm -f cerbos
    echo [OK] Contenedor Cerbos eliminado
) else (
    echo No habia contenedor para eliminar
)
echo.

REM 5. Iniciar nuevo contenedor Cerbos
echo [5/7] Iniciando nuevo contenedor Cerbos...
docker-compose up -d cerbos
echo [OK] Contenedor Cerbos iniciado
echo Esperando a que Cerbos este listo...
timeout /t 5 /nobreak >nul
echo.

REM 6. Verificar salud de Cerbos
echo [6/7] Verificando health check de Cerbos...
set MAX_RETRIES=10
set RETRY_COUNT=0

:check_health
curl -s http://localhost:3592/_cerbos/health >nul 2>&1
if not errorlevel 1 (
    echo [OK] Cerbos esta saludable y respondiendo
    goto health_ok
)

set /a RETRY_COUNT+=1
if %RETRY_COUNT% geq %MAX_RETRIES% (
    echo [ERROR] Cerbos no respondio despues de %MAX_RETRIES% intentos
    echo Ver logs con: docker logs roska_cerbos
    exit /b 1
)

echo   Intento %RETRY_COUNT%/%MAX_RETRIES% - Esperando...
timeout /t 2 /nobreak >nul
goto check_health

:health_ok
echo.
echo Informacion de Cerbos:
curl -s http://localhost:3592/_cerbos/health
echo.
echo.

REM 7. Probar conexión desde backend Python
echo [7/7] Probando conexion desde Django backend...
cd ..\backend

if exist "venv\" (
    call venv\Scripts\activate.bat

    REM Crear script de prueba temporal
    (
    echo import sys
    echo import os
    echo.
    echo # Anadir el directorio actual al path
    echo sys.path.insert^(0, os.path.dirname^(os.path.abspath^(__file__^)^)^)
    echo.
    echo # Configurar Django
    echo os.environ.setdefault^('DJANGO_SETTINGS_MODULE', 'config.settings.development'^)
    echo import django
    echo django.setup^(^)
    echo.
    echo from apps.permissions.services.cerbos_client import cerbos_service
    echo.
    echo print^("Probando conexion con Cerbos..."^)
    echo try:
    echo     from cerbos.sdk.model import Principal, ResourceDesc
    echo.
    echo     principal = Principal^(
    echo         id="test_user",
    echo         roles=set^(^),
    echo         attr={"is_superuser": True, "email": "test@test.com"}
    echo     ^)
    echo.
    echo     resource = ResourceDesc^(
    echo         "user",
    echo         "test_123",
    echo         attr={}
    echo     ^)
    echo.
    echo     result = cerbos_service.client.is_allowed^(
    echo         action="read",
    echo         principal=principal,
    echo         resource=resource
    echo     ^)
    echo.
    echo     print^(f"[OK] Conexion exitosa con Cerbos!"^)
    echo     print^(f"  Test de permiso 'read': {'Permitido' if result else 'Denegado'}"^)
    echo     print^(f"  Host: {cerbos_service.client.host}"^)
    echo     sys.exit^(0^)
    echo.
    echo except Exception as e:
    echo     print^(f"[ERROR] Error al conectar con Cerbos: {e}"^)
    echo     sys.exit^(1^)
    ) > test_cerbos_connection.py

    echo Ejecutando prueba de conexion Python...
    python test_cerbos_connection.py
    if not errorlevel 1 (
        echo [OK] Django backend puede conectarse con Cerbos
    ) else (
        echo [ERROR] Django backend no puede conectarse con Cerbos
    )

    REM Limpiar archivo temporal
    del test_cerbos_connection.py

) else (
    echo Venv no encontrado en backend\. Saltando prueba de conexion Python.
)

echo.
echo === [OK] Cerbos esta listo para usar ===
echo Endpoints disponibles:
echo   HTTP API:  http://localhost:3592
echo   gRPC API:  localhost:3593
echo   Health:    http://localhost:3592/_cerbos/health
echo.
echo Para ver logs de Cerbos:
echo   docker logs roska_cerbos
echo   docker logs -f roska_cerbos  (seguir logs en tiempo real)

cd ..\scripts
