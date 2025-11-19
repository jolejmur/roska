"""
Script para verificar la configuracion del rol basico
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.navigation.models import Function
from apps.permissions.models import Role

def verify_basic_role():
    """Verificar configuracion del rol basico"""

    print("\n=== VERIFICACION DEL ROL BASICO ===\n")

    # 1. Verificar funcion Mi Perfil
    try:
        profile_function = Function.objects.get(code='my_profile')
        print(f"[OK] Funcion: {profile_function.name}")
        print(f"    - Codigo: {profile_function.code}")
        print(f"    - URL: {profile_function.url}")
        print(f"    - Categoria: {profile_function.category}")
        print(f"    - is_system: {profile_function.is_system}")
        print(f"    - is_active: {profile_function.is_active}")
    except Function.DoesNotExist:
        print("[ERROR] La funcion 'my_profile' no existe")
        return

    # 2. Verificar rol Usuario Basico
    try:
        basic_role = Role.objects.get(code='basic_user')
        print(f"\n[OK] Rol: {basic_role.name}")
        print(f"    - Codigo: {basic_role.code}")
        print(f"    - Cerbos: {basic_role.cerbos_role}")
        print(f"    - is_system: {basic_role.is_system}")
        print(f"    - is_active: {basic_role.is_active}")

        # Verificar funciones asignadas
        functions = basic_role.functions.all()
        print(f"    - Funciones asignadas: {functions.count()}")
        for func in functions:
            print(f"      * {func.name} ({func.code})")
    except Role.DoesNotExist:
        print("[ERROR] El rol 'basic_user' no existe")
        return

    print("\n[OK] Configuracion correcta!")
    print("\nResumen:")
    print(f"- Funcion 'Mi Perfil' sin categoria: {profile_function.category is None}")
    print(f"- Rol 'Usuario Basico' es de sistema: {basic_role.is_system}")
    print(f"- Rol tiene la funcion 'Mi Perfil': {basic_role.functions.filter(code='my_profile').exists()}")

if __name__ == '__main__':
    verify_basic_role()
