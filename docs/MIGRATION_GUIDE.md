# Guía de Migración: FastAPI → Django REST Framework

Este documento describe el proceso de migración del proyecto desde FastAPI a Django REST Framework.

## 📊 Resumen de Cambios

| Componente | Antes (FastAPI) | Ahora (Django) |
|------------|----------------|----------------|
| Framework | FastAPI | Django REST Framework 3.14+ |
| ORM | SQLAlchemy async | Django ORM |
| Schemas | Pydantic | DRF Serializers |
| Auth | fastapi-users | Django User + Simple JWT |
| Migrations | Alembic | Django Migrations |
| Structure | app/* | backend/apps/* |

## 🗂️ Mapeo de Archivos

### Estructura Anterior (FastAPI)

```
app/
├── api/
│   ├── auth.py          → backend/apps/users/views/auth.py
│   └── users.py         → backend/apps/users/views/user.py
├── cerbos/
│   └── client.py        → backend/apps/permissions/services/cerbos_client.py
├── models/
│   └── user.py          → backend/apps/users/models/user.py
├── schemas/
│   ├── user.py          → backend/apps/users/serializers/user.py
│   └── permissions.py   → backend/apps/permissions/serializers/*
├── config.py            → backend/config/settings/*.py
├── database.py          → Django ORM (integrado)
└── main.py              → backend/config/wsgi.py + urls.py
```

### Estructura Nueva (Django)

```
backend/
├── config/              # Configuración del proyecto
│   ├── settings/       # Settings por ambiente
│   ├── urls.py         # Rutas principales
│   ├── wsgi.py         # WSGI application
│   └── asgi.py         # ASGI application
├── apps/               # Apps Django
│   ├── core/          # Base models y utils
│   ├── users/         # Gestión de usuarios
│   ├── permissions/   # Cerbos integration
│   └── navigation/    # Dynamic sidebar
├── common/            # Shared utilities
└── cerbos/            # Políticas Cerbos (sin cambios)
```

## 🔄 Migración de Código

### 1. Modelos (SQLAlchemy → Django ORM)

#### Antes (FastAPI + SQLAlchemy):

```python
# app/models/user.py
from sqlalchemy import String, Integer, ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable

class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    roles: Mapped[list[str]] = mapped_column(
        ARRAY(String),
        nullable=False,
        server_default='{"usuario"}'
    )
```

#### Ahora (Django ORM):

```python
# backend/apps/users/models/user.py
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    roles = ArrayField(
        models.CharField(max_length=50),
        default=list,
        blank=True
    )

    USERNAME_FIELD = 'email'
```

### 2. Schemas/Serializers (Pydantic → DRF)

#### Antes (Pydantic):

```python
# app/schemas/user.py
from pydantic import BaseModel, EmailStr

class UserRead(BaseModel):
    id: int
    email: EmailStr
    full_name: str | None
    is_active: bool
    is_superuser: bool
```

#### Ahora (DRF Serializers):

```python
# backend/apps/users/serializers/user.py
from rest_framework import serializers
from apps.users.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'is_active', 'is_superuser']
```

### 3. Endpoints (FastAPI Routes → DRF ViewSets)

#### Antes (FastAPI):

```python
# app/api/users.py
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter()

@router.get("/users/me", response_model=UserRead)
async def get_my_profile(current_user: User = Depends(current_active_user)):
    return current_user
```

#### Ahora (DRF ViewSet):

```python
# backend/apps/users/views/user.py
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=['get'], url_path='me')
    def get_me(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
```

### 4. Autenticación (fastapi-users → Simple JWT)

#### Antes (FastAPI):

```python
# app/api/auth.py
from fastapi import APIRouter
from app.users import fastapi_users, auth_backend

router = APIRouter()

router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/jwt"
)
```

#### Ahora (Django + Simple JWT):

```python
# backend/apps/users/views/auth.py
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

class LoginView(TokenObtainPairView):
    def post(self, request):
        # Custom login logic
        user = authenticate(...)
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        })
```

### 5. Cerbos Integration (Sin cambios mayores)

La integración con Cerbos se mantiene casi idéntica:

```python
# Antes y Ahora - Sintaxis muy similar
from apps.permissions.services.cerbos_client import cerbos_service

has_permission = cerbos_service.check_user_permission(
    user=request.user,
    resource_type='user',
    resource_id=str(user_id),
    action='update'
)
```

## 🗄️ Migración de Base de Datos

### Opción 1: Exportar/Importar Datos

```bash
# 1. Exportar datos desde FastAPI (PostgreSQL)
pg_dump -U roska_user -d roska_db > backup.sql

# 2. Crear migraciones Django
cd backend
python manage.py makemigrations
python manage.py migrate

# 3. Importar datos
psql -U roska_user -d roska_db < backup.sql
```

### Opción 2: Script de Migración Personalizado

```python
# backend/scripts/migrate_from_fastapi.py
from apps.users.models import User

# Leer datos de FastAPI
# Mapear a modelos Django
# Guardar en Django ORM
```

## 📝 Checklist de Migración

- [x] Estructura de directorios creada
- [x] Modelos Django migrados
- [x] Serializers creados
- [x] ViewSets y endpoints implementados
- [x] Autenticación JWT configurada
- [x] Cerbos integration migrada
- [x] Requirements actualizados
- [x] Docker configurado
- [ ] Tests migrados
- [ ] Documentación actualizada
- [ ] Datos migrados
- [ ] Frontend Angular conectado

## 🚨 Puntos de Atención

### 1. Cambios en URLs

| FastAPI | Django REST |
|---------|-------------|
| `/auth/jwt/login` | `/api/auth/login/` |
| `/auth/jwt/logout` | `/api/auth/logout/` |
| `/users/me` | `/api/users/me/` |
| `/users/me/permissions` | `/api/users/me/permissions/` |

### 2. Formato de Respuestas

FastAPI y DRF tienen formatos de respuesta similares, pero:

- **Paginación**: Ahora usa el formato estándar de DRF
- **Errores**: Formato de errores de DRF
- **Validación**: Mensajes de validación en formato DRF

### 3. Async vs Sync

- **FastAPI**: Todo async/await
- **Django**: Principalmente sync (aunque soporta async views)

La mayoría del código puede permanecer síncrono en Django sin problemas de rendimiento.

## 🔍 Testing Post-Migración

```bash
# Backend
cd backend
pytest

# Verificar endpoints
curl http://localhost:8000/health/
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@roskaradiadores.com","password":"admin123"}'
```

## 🎯 Próximos Pasos

1. ✅ Completar migración de backend
2. ⏳ Desarrollar frontend Angular
3. ⏳ Migrar tests
4. ⏳ Configurar CI/CD
5. ⏳ Deploy a producción

## 📚 Recursos

- [Django REST Framework Docs](https://www.django-rest-framework.org/)
- [Simple JWT Docs](https://django-rest-framework-simplejwt.readthedocs.io/)
- [Django Docs](https://docs.djangoproject.com/)
- [Cerbos Docs](https://docs.cerbos.dev/)

---

**Última actualización**: Octubre 2024
