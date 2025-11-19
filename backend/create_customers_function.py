"""
Script para crear la función de Clientes y asignarla a roles de admin
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.navigation.models import Function, Category
from apps.permissions.models import Role

def create_customers_function():
    """Crear función de Clientes y asignarla a roles administrativos"""

    # 1. Buscar o crear la categoría "Gestión"
    category, created = Category.objects.get_or_create(
        code='management',
        defaults={
            'name': 'Gestión',
            'description': 'Funciones de gestión del sistema',
            'icon': 'fas fa-cogs',
            'order': 10,
            'is_active': True,
            'is_system': True
        }
    )
    if created:
        print(f"[OK] Categoría creada: {category.name}")
    else:
        print(f"[OK] Categoría existente: {category.name}")

    # 2. Crear la función "Clientes"
    customers_function, created = Function.objects.get_or_create(
        code='customers',
        defaults={
            'name': 'Clientes',
            'category': category,
            'url': '/customers',
            'icon': 'fas fa-user-friends',
            'order': 20,
            'is_active': True,
            'is_system': False,
            'cerbos_resource': 'customer'
        }
    )
    if created:
        print(f"[OK] Función creada: {customers_function.name}")
    else:
        print(f"[OK] Función existente: {customers_function.name}")
        # Actualizar campos si ya existe
        customers_function.category = category
        customers_function.url = '/customers'
        customers_function.icon = 'fas fa-user-friends'
        customers_function.cerbos_resource = 'customer'
        customers_function.save()
        print(f"[OK] Función actualizada")

    # 3. Asignar la función a roles administrativos
    admin_roles = []

    # Buscar roles administrativos (diferentes variaciones posibles)
    for code in ['ADMIN', 'admin', 'superadmin', 'administrator', 'staff']:
        try:
            role = Role.objects.get(code=code)
            admin_roles.append(role)
            print(f"[OK] Rol encontrado: {role.name} ({role.code})")
        except Role.DoesNotExist:
            pass

    if not admin_roles:
        print("[WARNING] No se encontraron roles administrativos")
        print("[INFO] La función fue creada pero no se asignó a ningún rol")
        print("[INFO] Por favor, asigne manualmente la función a los roles apropiados")

    # 4. Asignar la función a los roles encontrados
    for role in admin_roles:
        if not role.functions.filter(id=customers_function.id).exists():
            role.functions.add(customers_function)
            print(f"[OK] Función '{customers_function.name}' asignada al rol '{role.name}'")
        else:
            print(f"[OK] Función ya asignada al rol '{role.name}'")

    print(f"\n[OK] Función ID: {customers_function.id}")
    print(f"[OK] URL: {customers_function.url}")
    print(f"[OK] Todo listo! La función 'Clientes' está configurada.")
    print(f"[OK] Roles con acceso: {', '.join([r.name for r in admin_roles])}")

if __name__ == '__main__':
    create_customers_function()
