"""
Script para actualizar la funcion Mi Perfil - remover categoria
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.navigation.models import Function

def update_profile_function():
    """Actualizar funcion Mi Perfil para que no tenga categoria"""

    try:
        profile_function = Function.objects.get(code='my_profile')
        profile_function.category = None
        profile_function.save()
        print(f"[OK] Funcion '{profile_function.name}' actualizada - categoria removida")
        print(f"[OK] Categoria actual: {profile_function.category}")
    except Function.DoesNotExist:
        print("[ERROR] La funcion 'my_profile' no existe")

if __name__ == '__main__':
    update_profile_function()
