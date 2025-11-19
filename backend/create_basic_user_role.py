"""
Script para crear el rol de Usuario Básico con la función Mi Perfil
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.navigation.models import Function, Category
from apps.permissions.models import Role

def create_basic_user_role():
    """Crear rol de usuario básico con función Mi Perfil"""

    # 1. Buscar o crear la categoría "Perfil"
    category, created = Category.objects.get_or_create(
        code='profile',
        defaults={
            'name': 'Perfil',
            'description': 'Funciones relacionadas con el perfil del usuario',
            'icon': 'fas fa-user-circle',
            'order': 999,  # Al final
            'is_active': True,
            'is_system': True
        }
    )
    if created:
        print(f"[OK] Categoria creada: {category.name}")
    else:
        print(f"[OK] Categoria existente: {category.name}")

    # 2. Buscar o crear la función "Mi Perfil"
    profile_function, created = Function.objects.get_or_create(
        code='my_profile',
        defaults={
            'name': 'Mi Perfil',
            'category': category,
            'url': '/profile',
            'icon': 'fas fa-user',
            'order': 1,
            'is_active': True,
            'is_system': True,  # Función de sistema
            'cerbos_resource': 'profile'
        }
    )
    if created:
        print(f"[OK] Funcion creada: {profile_function.name}")
    else:
        print(f"[OK] Funcion existente: {profile_function.name}")

    # 3. Crear el rol "Usuario Básico"
    basic_role, created = Role.objects.get_or_create(
        code='basic_user',
        defaults={
            'name': 'Usuario Básico',
            'description': 'Rol básico asignado automáticamente a todos los usuarios',
            'cerbos_role': 'basic_user',
            'is_active': True,
            'is_system': True,  # Rol de sistema, no se puede editar
            'level': 0
        }
    )
    if created:
        print(f"[OK] Rol creado: {basic_role.name}")
    else:
        print(f"[OK] Rol existente: {basic_role.name}")

    # 4. Asignar la función al rol
    if not basic_role.functions.filter(id=profile_function.id).exists():
        basic_role.functions.add(profile_function)
        print(f"[OK] Funcion '{profile_function.name}' asignada al rol '{basic_role.name}'")
    else:
        print(f"[OK] Funcion ya estaba asignada")

    print(f"\n[OK] Rol ID: {basic_role.id}")
    print(f"[OK] Todo listo! El rol '{basic_role.name}' esta configurado.")

if __name__ == '__main__':
    create_basic_user_role()
