#!/bin/bash
# Script para verificar conexión a PostgreSQL, resetear DB y probar conexión con backend

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Script de Verificación y Reset de PostgreSQL ===${NC}\n"

# 1. Verificar que Docker esté corriendo
echo -e "${YELLOW}[1/6] Verificando Docker...${NC}"
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}✗ Docker no está corriendo. Por favor inicia Docker Desktop.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker está corriendo${NC}\n"

# 2. Verificar si el contenedor de PostgreSQL existe
echo -e "${YELLOW}[2/6] Verificando contenedor PostgreSQL...${NC}"
if ! docker ps -a --format '{{.Names}}' | grep -q "roska_db"; then
    echo -e "${YELLOW}○ Contenedor no existe. Iniciando servicios...${NC}"
    docker-compose up -d db
    echo -e "${GREEN}✓ Esperando a que PostgreSQL esté listo...${NC}"
    sleep 5
else
    # Verificar si está corriendo
    if ! docker ps --format '{{.Names}}' | grep -q "roska_db"; then
        echo -e "${YELLOW}○ Contenedor existe pero no está corriendo. Iniciando...${NC}"
        docker-compose start db
        sleep 3
    fi
    echo -e "${GREEN}✓ Contenedor PostgreSQL está corriendo${NC}"
fi
echo ""

# 3. Verificar conexión a PostgreSQL
echo -e "${YELLOW}[3/6] Verificando conexión a PostgreSQL...${NC}"
if docker exec roska_db pg_isready -U postgres > /dev/null 2>&1; then
    echo -e "${GREEN}✓ PostgreSQL está aceptando conexiones${NC}"
else
    echo -e "${RED}✗ PostgreSQL no responde. Esperando...${NC}"
    sleep 5
    if ! docker exec roska_db pg_isready -U postgres > /dev/null 2>&1; then
        echo -e "${RED}✗ PostgreSQL no está disponible después de esperar${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ PostgreSQL ahora está disponible${NC}"
fi
echo ""

# 4. Eliminar base de datos existente y crear nueva
echo -e "${YELLOW}[4/6] Reseteando base de datos...${NC}"
echo -e "${YELLOW}○ Eliminando base de datos 'korban' si existe...${NC}"

# Terminar conexiones activas
docker exec roska_db psql -U postgres -d postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'korban' AND pid <> pg_backend_pid();" > /dev/null 2>&1 || true

# Eliminar base de datos
docker exec roska_db psql -U postgres -d postgres -c "DROP DATABASE IF EXISTS korban;" > /dev/null 2>&1

echo -e "${GREEN}✓ Base de datos eliminada${NC}"

# Crear nueva base de datos
echo -e "${YELLOW}○ Creando nueva base de datos 'korban'...${NC}"
docker exec roska_db psql -U postgres -d postgres -c "CREATE DATABASE korban;" > /dev/null 2>&1
echo -e "${GREEN}✓ Base de datos 'korban' creada exitosamente${NC}\n"

# 5. Verificar que la base de datos está accesible
echo -e "${YELLOW}[5/6] Verificando acceso a la base de datos...${NC}"
DB_LIST=$(docker exec roska_db psql -U postgres -d postgres -t -c "SELECT datname FROM pg_database WHERE datname='korban';")
if echo "$DB_LIST" | grep -q "korban"; then
    echo -e "${GREEN}✓ Base de datos 'korban' está accesible${NC}"
else
    echo -e "${RED}✗ No se puede acceder a la base de datos${NC}"
    exit 1
fi
echo ""

# 6. Probar conexión desde backend (si existe venv)
echo -e "${YELLOW}[6/6] Probando conexión desde Django backend...${NC}"
cd ../backend

if [ -d "venv" ]; then
    # Activar venv y probar conexión
    source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null

    echo -e "${YELLOW}○ Ejecutando check de Django...${NC}"
    if python manage.py check --database default 2>&1 | grep -q "System check identified no issues"; then
        echo -e "${GREEN}✓ Django puede conectarse a PostgreSQL${NC}"
    else
        echo -e "${YELLOW}○ Ejecutando check de Django (puede tener warnings de configuración)...${NC}"
        python manage.py check --database default || true
    fi

    # Ejecutar migraciones
    echo -e "\n${YELLOW}○ Ejecutando migraciones...${NC}"
    python manage.py migrate

    echo -e "\n${GREEN}✓ Migraciones aplicadas exitosamente${NC}"
else
    echo -e "${YELLOW}○ Venv no encontrado en backend/. Saltando prueba de conexión Django.${NC}"
fi

echo -e "\n${GREEN}=== ✓ PostgreSQL está listo para usar ===${NC}"
echo -e "${YELLOW}Puedes conectarte con:${NC}"
echo -e "  Host: localhost"
echo -e "  Port: 5432"
echo -e "  Database: korban"
echo -e "  User: postgres"
echo -e "  Password: postgres"
echo ""
echo -e "${YELLOW}Para crear un superusuario Django:${NC}"
echo -e "  cd backend"
echo -e "  source venv/bin/activate  # o venv\\Scripts\\activate en Windows"
echo -e "  python manage.py createsuperuser"
