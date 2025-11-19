@echo off
REM Script para verificar conexión a PostgreSQL, resetear DB y probar conexión con backend (Windows)

echo === Script de Verificacion y Reset de PostgreSQL ===
echo.

REM 1. Verificar que Docker este corriendo
echo [1/6] Verificando Docker...
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker no esta corriendo. Por favor inicia Docker Desktop.
    exit /b 1
)
echo [OK] Docker esta corriendo
echo.

REM 2. Verificar si el contenedor de PostgreSQL existe
echo [2/6] Verificando contenedor PostgreSQL...
docker ps -a --format "{{.Names}}" | findstr /C:"roska_db" >nul
if errorlevel 1 (
    echo Contenedor no existe. Iniciando servicios...
    docker-compose up -d db
    echo Esperando a que PostgreSQL este listo...
    timeout /t 5 /nobreak >nul
) else (
    docker ps --format "{{.Names}}" | findstr /C:"roska_db" >nul
    if errorlevel 1 (
        echo Contenedor existe pero no esta corriendo. Iniciando...
        docker-compose start db
        timeout /t 3 /nobreak >nul
    )
    echo [OK] Contenedor PostgreSQL esta corriendo
)
echo.

REM 3. Verificar conexion a PostgreSQL
echo [3/6] Verificando conexion a PostgreSQL...
docker exec roska_db pg_isready -U postgres >nul 2>&1
if errorlevel 1 (
    echo PostgreSQL no responde. Esperando...
    timeout /t 5 /nobreak >nul
    docker exec roska_db pg_isready -U postgres >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] PostgreSQL no esta disponible despues de esperar
        exit /b 1
    )
)
echo [OK] PostgreSQL esta aceptando conexiones
echo.

REM 4. Eliminar base de datos existente y crear nueva
echo [4/6] Reseteando base de datos...
echo Eliminando base de datos 'korban' si existe...

REM Terminar conexiones activas
docker exec roska_db psql -U postgres -d postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'korban' AND pid <> pg_backend_pid();" >nul 2>&1

REM Eliminar base de datos
docker exec roska_db psql -U postgres -d postgres -c "DROP DATABASE IF EXISTS korban;" >nul 2>&1
echo [OK] Base de datos eliminada

REM Crear nueva base de datos
echo Creando nueva base de datos 'korban'...
docker exec roska_db psql -U postgres -d postgres -c "CREATE DATABASE korban;" >nul 2>&1
echo [OK] Base de datos 'korban' creada exitosamente
echo.

REM 5. Verificar que la base de datos esta accesible
echo [5/6] Verificando acceso a la base de datos...
docker exec roska_db psql -U postgres -d postgres -t -c "SELECT datname FROM pg_database WHERE datname='korban';" | findstr /C:"korban" >nul
if errorlevel 1 (
    echo [ERROR] No se puede acceder a la base de datos
    exit /b 1
)
echo [OK] Base de datos 'korban' esta accesible
echo.

REM 6. Probar conexion desde backend (si existe venv)
echo [6/6] Probando conexion desde Django backend...
cd ..\backend

if exist "venv\" (
    echo Ejecutando check de Django...
    call venv\Scripts\activate.bat
    python manage.py check --database default

    echo.
    echo Ejecutando migraciones...
    python manage.py migrate

    echo.
    echo [OK] Migraciones aplicadas exitosamente
) else (
    echo Venv no encontrado en backend\. Saltando prueba de conexion Django.
)

echo.
echo === [OK] PostgreSQL esta listo para usar ===
echo Puedes conectarte con:
echo   Host: localhost
echo   Port: 5432
echo   Database: korban
echo   User: postgres
echo   Password: postgres
echo.
echo Para crear un superusuario Django:
echo   cd backend
echo   venv\Scripts\activate
echo   python manage.py createsuperuser

cd ..
