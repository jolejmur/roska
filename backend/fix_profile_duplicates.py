"""
Script para limpiar funciones duplicadas de Mi Perfil
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.navigation.models import Function
from apps.permissions.models import Role

def fix_profile_duplicates():
    """Limpiar duplicados de la función Mi Perfil"""

    print("[INFO] Buscando funciones duplicadas de Mi Perfil...")

    # Buscar las funciones duplicadas
    try:
        old_profile = Function.objects.get(id=14, code='profile')
        correct_profile = Function.objects.get(id=19, code='my_profile')
    except Function.DoesNotExist as e:
        print(f"[ERROR] No se encontraron las funciones: {e}")
        return

    print(f"[OK] Función antigua encontrada: ID {old_profile.id} - {old_profile.code}")
    print(f"[OK] Función correcta encontrada: ID {correct_profile.id} - {correct_profile.code}")

    # Obtener todos los roles asignados a la función antigua
    old_roles = list(old_profile.roles.all())
    print(f"\n[INFO] Roles asignados a la función antigua '{old_profile.code}':")
    for role in old_roles:
        print(f"  - {role.name} ({role.code})")

    # Obtener todos los roles asignados a la función correcta
    correct_roles = list(correct_profile.roles.all())
    print(f"\n[INFO] Roles asignados a la función correcta '{correct_profile.code}':")
    for role in correct_roles:
        print(f"  - {role.name} ({role.code})")

    # Reasignar todos los roles a la función correcta
    print(f"\n[INFO] Reasignando roles a la función correcta '{correct_profile.code}'...")
    for role in old_roles:
        if role not in correct_roles:
            correct_profile.roles.add(role)
            print(f"[OK] Rol '{role.name}' asignado a '{correct_profile.code}'")
        else:
            print(f"[OK] Rol '{role.name}' ya estaba asignado")

    # Asegurar que TODOS los roles tengan Mi Perfil (es una función básica)
    all_roles = Role.objects.filter(is_active=True)
    print(f"\n[INFO] Asegurando que todos los roles activos tengan 'Mi Perfil'...")
    for role in all_roles:
        if not correct_profile.roles.filter(id=role.id).exists():
            correct_profile.roles.add(role)
            print(f"[OK] Rol '{role.name}' agregado a 'Mi Perfil'")

    # Eliminar la función antigua
    print(f"\n[INFO] Eliminando función duplicada '{old_profile.code}' (ID {old_profile.id})...")
    old_profile.delete()
    print(f"[OK] Función duplicada eliminada")

    # Verificar que la función correcta no tenga categoría
    if correct_profile.category is not None:
        print(f"\n[WARNING] La función 'Mi Perfil' tiene una categoría asignada: {correct_profile.category}")
        correct_profile.category = None
        correct_profile.save()
        print(f"[OK] Categoría removida de 'Mi Perfil'")
    else:
        print(f"\n[OK] La función 'Mi Perfil' no tiene categoría (correcto)")

    # Mostrar resumen final
    final_roles = list(correct_profile.roles.all())
    print(f"\n[OK] ¡Duplicados eliminados!")
    print(f"[OK] Función correcta: {correct_profile.code} (ID {correct_profile.id})")
    print(f"[OK] URL: {correct_profile.url}")
    print(f"[OK] Categoría: {correct_profile.category}")
    print(f"[OK] Roles con acceso: {', '.join([r.name for r in final_roles])}")

if __name__ == '__main__':
    fix_profile_duplicates()
