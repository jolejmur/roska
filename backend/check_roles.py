"""
Script para verificar todos los roles existentes
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.permissions.models import Role

def check_roles():
    """Listar todos los roles existentes"""

    print("\n=== ROLES EXISTENTES ===\n")

    roles = Role.objects.all().order_by('id')

    for role in roles:
        print(f"ID: {role.id}")
        print(f"  Nombre: {role.name}")
        print(f"  Codigo: {role.code}")
        print(f"  Cerbos: {role.cerbos_role}")
        print(f"  is_system: {role.is_system}")
        print(f"  is_active: {role.is_active}")
        print(f"  Funciones: {role.functions.count()}")
        print()

if __name__ == '__main__':
    check_roles()
