from django.core.management.base import BaseCommand
from apps.navigation.models import Category, Function
from apps.permissions.models import Role
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Crea el menú Comercial y la función Cotización y asigna permisos'

    def handle(self, *args, **kwargs):
        # 1. Crear o obtener Categoría Comercial
        category, cat_created = Category.objects.get_or_create(
            code="commercial",
            defaults={
                'name': "Comercial",
                'icon': 'fas fa-cash-register',  # Icono de Font Awesome
                'order': 3,
                'is_active': True
            }
        )
        # Actualizar el icono si la categoría ya existía
        if not cat_created and category.icon != 'fas fa-cash-register':
            category.icon = 'fas fa-cash-register'
            category.save()
            self.stdout.write(f'Icono de categoría "{category.name}" actualizado.')

        if cat_created:
            self.stdout.write(self.style.SUCCESS(f'Categoría creada: {category.name}'))
        else:
            self.stdout.write(f'Categoría ya existe: {category.name}')

        # 2. Crear o obtener Función Cotización
        function, func_created = Function.objects.get_or_create(
            code="commercial.quotation",
            defaults={
                'name': "Cotización",
                'category': category,
                'url': '/commercial/quotation',
                'icon': 'fas fa-file-invoice-dollar',  # Icono de Font Awesome
                'order': 1,
                'is_active': True,
                'is_system': False
            }
        )
        # Actualizar el icono si la función ya existía
        if not func_created and function.icon != 'fas fa-file-invoice-dollar':
            function.icon = 'fas fa-file-invoice-dollar'
            function.save()
            self.stdout.write(f'Icono de función "{function.name}" actualizado.')
        
        if func_created:
            self.stdout.write(self.style.SUCCESS(f'Función creada: {function.name}'))
        else:
            self.stdout.write(f'Función ya existe: {function.name}')

        # 3. Asignar la función al rol de Administrador
        try:
            admin_role = Role.objects.get(code='ADMIN')
            if function not in admin_role.functions.all():
                admin_role.functions.add(function)
                self.stdout.write(self.style.SUCCESS(f'Permiso de "{function.name}" asignado al rol "{admin_role.name}"'))
            else:
                self.stdout.write(f'El rol "{admin_role.name}" ya tenía permiso para "{function.name}"')

        except Role.DoesNotExist:
            self.stdout.write(self.style.ERROR('El rol con código "ADMIN" no existe. No se pudieron asignar los permisos.'))

        self.stdout.write(self.style.SUCCESS('Script finalizado. Recuerda reiniciar el backend.'))