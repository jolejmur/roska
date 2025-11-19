"""
Script para crear el rol de Cliente con permisos de consulta
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.navigation.models import Function
from apps.permissions.models import Role

def create_customer_role():
    """Crear rol de cliente con permisos de consulta"""

    # 1. Crear el rol "Cliente"
    customer_role, created = Role.objects.get_or_create(
        code='customer',
        defaults={
            'name': 'Cliente',
            'description': 'Rol de cliente con acceso de solo lectura a su información',
            'cerbos_role': 'customer',
            'is_active': True,
            'is_system': True,  # Rol de sistema
            'level': 1  # Nivel bajo
        }
    )
    if created:
        print(f"[OK] Rol creado: {customer_role.name}")
    else:
        print(f"[OK] Rol existente: {customer_role.name}")
        # Actualizar campos si ya existe
        customer_role.cerbos_role = 'customer'
        customer_role.is_system = True
        customer_role.save()
        print(f"[OK] Rol actualizado")

    # 2. Asignar funciones básicas al rol de cliente
    # Los clientes deberían poder ver su perfil
    basic_functions = []

    try:
        profile_function = Function.objects.get(code='my_profile')
        basic_functions.append(profile_function)
    except Function.DoesNotExist:
        print("[WARNING] Función 'my_profile' no encontrada")

    # Asignar las funciones al rol
    for function in basic_functions:
        if not customer_role.functions.filter(id=function.id).exists():
            customer_role.functions.add(function)
            print(f"[OK] Función '{function.name}' asignada al rol '{customer_role.name}'")
        else:
            print(f"[OK] Función '{function.name}' ya estaba asignada")

    print(f"\n[OK] Rol ID: {customer_role.id}")
    print(f"[OK] Cerbos Role: {customer_role.cerbos_role}")
    print(f"[OK] Todo listo! El rol '{customer_role.name}' está configurado.")
    print(f"[OK] Funciones asignadas: {', '.join([f.name for f in basic_functions])}")
    print(f"\n[INFO] Los clientes se crearán con este rol automáticamente")
    print(f"[INFO] Tendrán acceso de solo lectura a su información")

if __name__ == '__main__':
    create_customer_role()
