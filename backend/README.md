# Roska Radiadores Backend

Django REST Framework backend for Roska Radiadores management system.

## Features

- Django 5.0 with Django REST Framework
- JWT Authentication with Simple JWT
- Cerbos for fine-grained permissions
- PostgreSQL database
- Celery for async tasks
- Docker support

## Project Structure

```
backend/
├── config/                 # Django project configuration
│   ├── settings/          # Settings modules (base, dev, prod, test)
│   ├── urls.py            # Main URL configuration
│   ├── wsgi.py            # WSGI configuration
│   └── asgi.py            # ASGI configuration
├── apps/                   # Django applications
│   ├── core/              # Core functionality (base models, utilities)
│   ├── users/             # User management and authentication
│   ├── permissions/       # Cerbos integration
│   └── navigation/        # Dynamic navigation/sidebar
├── common/                 # Shared utilities
│   ├── middleware/        # Custom middleware
│   ├── pagination/        # Custom pagination
│   └── utils/             # Helper functions
├── cerbos/                 # Cerbos policies
├── requirements/           # Python requirements
├── tests/                  # Integration and E2E tests
└── manage.py              # Django management script
```

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis (for Celery)
- Cerbos (running on ports 3592/3593)

### Installation

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements/development.txt
```

3. Copy environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Create superuser:
```bash
python manage.py createsuperuser
```

6. Run development server:
```bash
python manage.py runserver
```

## Docker Setup

```bash
# From project root
docker-compose up -d
```

## API Documentation

- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/

## Testing

```bash
pytest
```

## Migration from FastAPI

This project was migrated from FastAPI. Key changes:

- FastAPI → Django REST Framework
- Pydantic schemas → DRF Serializers
- SQLAlchemy → Django ORM
- fastapi-users → Django User model with JWT
- All Cerbos integration preserved

## License

Proprietary
