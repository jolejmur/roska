# Roska Radiadores - Sistema de Gestión

Sistema de gestión empresarial con backend Django REST Framework y frontend Angular 17.

## 📋 Características

- **Backend**: Django REST Framework con autenticación JWT
- **Frontend**: Angular 17 standalone con Signals
- **Permisos**: Cerbos para control de acceso fino
- **Base de datos**: PostgreSQL 15
- **Cache/Queue**: Redis + Celery
- **Contenedores**: Docker y Docker Compose

## 🏗️ Arquitectura del Proyecto

```
roska_radiadores/
├── backend/                    # Django REST API
│   ├── config/                # Configuración Django
│   ├── apps/                  # Aplicaciones Django
│   │   ├── core/             # Modelos base y utilidades
│   │   ├── users/            # Gestión de usuarios
│   │   ├── permissions/      # Integración Cerbos
│   │   └── navigation/       # Sidebar dinámico
│   ├── common/               # Utilidades compartidas
│   ├── cerbos/               # Políticas de Cerbos
│   └── requirements/         # Dependencias Python
│
├── frontend/                   # Angular SPA
│   ├── src/app/
│   │   ├── core/            # Servicios singleton
│   │   ├── shared/          # Componentes compartidos
│   │   └── features/        # Módulos lazy-loaded
│   └── src/environments/    # Configuración de entornos
│
├── docker/                     # Dockerfiles
├── docs/                       # Documentación
└── docker-compose.yml         # Orquestación de servicios
```

## 🚀 Inicio Rápido

### Prerequisitos

- Docker y Docker Compose
- Python 3.11+ (para desarrollo local sin Docker)
- Node.js 20+ (para desarrollo local sin Docker)
- PostgreSQL 15+ (para desarrollo local sin Docker)

### Con Docker (Recomendado)

1. Clonar el repositorio:
```bash
git clone <repository-url>
cd roska_radiadores
```

2. Copiar variables de entorno:
```bash
cp backend/.env.example backend/.env
# Editar backend/.env con tu configuración
```

3. Iniciar servicios:
```bash
docker-compose up -d
```

4. Acceder a las aplicaciones:
- **Frontend**: http://localhost:4200
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs/
- **Admin**: http://localhost:8000/admin/
- **Cerbos**: http://localhost:3592

### Credenciales por defecto
- **Email**: admin@roskaradiadores.com
- **Password**: admin123

## 🛠️ Desarrollo Local sin Docker

### Backend

```bash
cd backend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements/development.txt

# Configurar variables de entorno
cp .env.example .env

# Ejecutar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Iniciar servidor
python manage.py runserver
```

### Frontend

```bash
cd frontend

# Instalar dependencias
npm install

# Iniciar servidor de desarrollo
npm start
```

## 🔒 Sistema de Permisos con Cerbos

Cerbos proporciona control de acceso fino. Las políticas se definen en `backend/cerbos/policies/`.

### Ejemplo de uso en Django:

```python
from apps.permissions.services.cerbos_client import cerbos_service

# Verificar permiso
has_permission = cerbos_service.check_user_permission(
    user=request.user,
    resource_type='user',
    resource_id=str(user_id),
    action='update'
)
```

## 🧪 Testing

### Backend

```bash
cd backend
pytest
```

### Frontend

```bash
cd frontend
npm test
```

## 📚 Documentación

- [Documentación Backend](./backend/README.md)
- [Documentación Frontend](./frontend/README.md)
- [Guía de Migración desde FastAPI](./docs/MIGRATION_GUIDE.md)

## 🔄 Migración desde FastAPI

Este proyecto fue migrado desde FastAPI a Django REST Framework. Ver [MIGRATION_GUIDE.md](./docs/MIGRATION_GUIDE.md) para más detalles.

### Cambios principales:
- FastAPI → Django REST Framework
- Pydantic → Django ORM + DRF Serializers
- SQLAlchemy async → Django ORM
- fastapi-users → Django User model con JWT
- Cerbos integration preservada 100%

## 🚢 Despliegue

### Producción con Docker

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 📄 Licencia

Propietario - Todos los derechos reservados

---

**Versión**: 1.0.0
**Última actualización**: Octubre 2024
