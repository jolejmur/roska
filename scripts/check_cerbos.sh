#!/bin/bash
# Script para verificar conexión a Cerbos, reiniciar y probar conexión con backend

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Script de Verificación y Reinicio de Cerbos ===${NC}\n"

# 1. Verificar que Docker esté corriendo
echo -e "${YELLOW}[1/7] Verificando Docker...${NC}"
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}✗ Docker no está corriendo. Por favor inicia Docker Desktop.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker está corriendo${NC}\n"

# 2. Verificar archivos de configuración de Cerbos
echo -e "${YELLOW}[2/7] Verificando archivos de configuración de Cerbos...${NC}"
CERBOS_CONFIG="../backend/cerbos/config.yaml"
CERBOS_POLICIES="../backend/cerbos/policies"

if [ ! -f "$CERBOS_CONFIG" ]; then
    echo -e "${RED}✗ No se encontró config.yaml en backend/cerbos/${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Archivo de configuración encontrado${NC}"

if [ ! -d "$CERBOS_POLICIES" ]; then
    echo -e "${RED}✗ No se encontró directorio de políticas en backend/cerbos/policies/${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Directorio de políticas encontrado${NC}"

# Contar políticas
POLICY_COUNT=$(find "$CERBOS_POLICIES" -name "*.yaml" -o -name "*.yml" | wc -l)
echo -e "${BLUE}  → Políticas encontradas: $POLICY_COUNT${NC}\n"

# 3. Detener contenedor Cerbos si está corriendo
echo -e "${YELLOW}[3/7] Deteniendo contenedor Cerbos existente...${NC}"
if docker ps --format '{{.Names}}' | grep -q "roska_cerbos"; then
    docker-compose stop cerbos
    echo -e "${GREEN}✓ Contenedor Cerbos detenido${NC}"
else
    echo -e "${BLUE}  → Contenedor no estaba corriendo${NC}"
fi

# 4. Eliminar contenedor Cerbos
echo -e "${YELLOW}[4/7] Eliminando contenedor Cerbos...${NC}"
if docker ps -a --format '{{.Names}}' | grep -q "roska_cerbos"; then
    docker-compose rm -f cerbos
    echo -e "${GREEN}✓ Contenedor Cerbos eliminado${NC}"
else
    echo -e "${BLUE}  → No había contenedor para eliminar${NC}"
fi
echo ""

# 5. Iniciar nuevo contenedor Cerbos
echo -e "${YELLOW}[5/7] Iniciando nuevo contenedor Cerbos...${NC}"
docker-compose up -d cerbos
echo -e "${GREEN}✓ Contenedor Cerbos iniciado${NC}"
echo -e "${YELLOW}○ Esperando a que Cerbos esté listo...${NC}"
sleep 5
echo ""

# 6. Verificar salud de Cerbos
echo -e "${YELLOW}[6/7] Verificando health check de Cerbos...${NC}"
MAX_RETRIES=10
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:3592/_cerbos/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Cerbos está saludable y respondiendo${NC}"
        break
    else
        RETRY_COUNT=$((RETRY_COUNT + 1))
        echo -e "${YELLOW}  → Intento $RETRY_COUNT/$MAX_RETRIES - Esperando...${NC}"
        sleep 2
    fi
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo -e "${RED}✗ Cerbos no respondió después de $MAX_RETRIES intentos${NC}"
    echo -e "${YELLOW}Ver logs con: docker logs roska_cerbos${NC}"
    exit 1
fi
echo ""

# Obtener información de Cerbos
echo -e "${BLUE}Información de Cerbos:${NC}"
CERBOS_INFO=$(curl -s http://localhost:3592/_cerbos/health 2>/dev/null)
echo -e "${BLUE}$CERBOS_INFO${NC}\n"

# 7. Probar conexión desde backend Python
echo -e "${YELLOW}[7/7] Probando conexión desde Django backend...${NC}"
cd ../backend

if [ -d "venv" ]; then
    # Activar venv
    source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null

    # Crear script de prueba temporal
    cat > test_cerbos_connection.py << 'EOF'
import sys
import os

# Añadir el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
import django
django.setup()

from apps.permissions.services.cerbos_client import cerbos_service

print("Probando conexión con Cerbos...")
try:
    # Crear un principal de prueba
    from cerbos.sdk.model import Principal, ResourceDesc

    principal = Principal(
        id="test_user",
        roles=set(),
        attr={"is_superuser": True, "email": "test@test.com"}
    )

    resource = ResourceDesc(
        "user",
        "test_123",
        attr={}
    )

    # Intentar verificar un permiso
    result = cerbos_service.client.is_allowed(
        action="read",
        principal=principal,
        resource=resource
    )

    print(f"✓ Conexión exitosa con Cerbos!")
    print(f"  → Test de permiso 'read': {'Permitido' if result else 'Denegado'}")
    print(f"  → Host: {cerbos_service.client.host}")
    sys.exit(0)

except Exception as e:
    print(f"✗ Error al conectar con Cerbos: {e}")
    sys.exit(1)
EOF

    echo -e "${YELLOW}○ Ejecutando prueba de conexión Python...${NC}"
    if python test_cerbos_connection.py; then
        echo -e "${GREEN}✓ Django backend puede conectarse con Cerbos${NC}"
    else
        echo -e "${RED}✗ Django backend no puede conectarse con Cerbos${NC}"
    fi

    # Limpiar archivo temporal
    rm -f test_cerbos_connection.py

else
    echo -e "${YELLOW}○ Venv no encontrado en backend/. Saltando prueba de conexión Python.${NC}"
fi

echo -e "\n${GREEN}=== ✓ Cerbos está listo para usar ===${NC}"
echo -e "${YELLOW}Endpoints disponibles:${NC}"
echo -e "  HTTP API:  http://localhost:3592"
echo -e "  gRPC API:  localhost:3593"
echo -e "  Health:    http://localhost:3592/_cerbos/health"
echo ""
echo -e "${YELLOW}Para ver logs de Cerbos:${NC}"
echo -e "  docker logs roska_cerbos"
echo -e "  docker logs -f roska_cerbos  (seguir logs en tiempo real)"
