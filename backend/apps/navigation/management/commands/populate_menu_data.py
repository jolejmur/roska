"""
Management command to populate database with sample menu data
Creates functions, roles, and assigns them to users
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.navigation.models import Function
from apps.permissions.models import Role, RoleAssignment

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate database with sample menu functions, roles, and assignments'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting data population...'))

        # Create Functions (Menu Items)
        self.stdout.write('Creating menu functions...')

        # Root level functions - Solo lo esencial
        profile_func, _ = Function.objects.get_or_create(
            code='profile',
            defaults={
                'name': 'Mi Perfil',
                'url': '/profile',
                'icon': 'fas fa-user-circle',
                'order': 0,
                'is_active': True
            }
        )
        self.stdout.write(f'  [OK] Created: {profile_func.name}')

        # Parent menu for user management (especificamente pedido)
        users_parent, _ = Function.objects.get_or_create(
            code='users_management',
            defaults={
                'name': 'Gestion de Usuarios',
                'url': None,
                'icon': 'fas fa-users',
                'order': 20,
                'is_active': True
            }
        )
        self.stdout.write(f'  [OK] Created: {users_parent.name}')

        # Children of user management
        users_list, _ = Function.objects.get_or_create(
            code='users.list',
            defaults={
                'name': 'Usuarios',
                'url': '/users',
                'icon': 'fas fa-user-friends',
                'parent': users_parent,
                'order': 0,
                'is_active': True
            }
        )
        self.stdout.write(f'    [OK] Created child: {users_list.name}')

        roles_list, _ = Function.objects.get_or_create(
            code='roles.list',
            defaults={
                'name': 'Roles',
                'url': '/roles',
                'icon': 'fas fa-user-tag',
                'parent': users_parent,
                'order': 10,
                'is_active': True
            }
        )
        self.stdout.write(f'    [OK] Created child: {roles_list.name}')

        functions_list, _ = Function.objects.get_or_create(
            code='functions.list',
            defaults={
                'name': 'Funciones',
                'url': '/functions',
                'icon': 'fas fa-list-ul',
                'parent': users_parent,
                'order': 20,
                'is_active': True
            }
        )
        self.stdout.write(f'    [OK] Created child: {functions_list.name}')

        # Create Roles
        self.stdout.write('\nCreating roles...')

        admin_role, _ = Role.objects.get_or_create(
            code='ADMIN',
            defaults={
                'name': 'Administrador',
                'description': 'Acceso completo al sistema',
                'cerbos_role': 'admin',
                'is_active': True,
                'is_system': True,
                'level': 100
            }
        )
        self.stdout.write(f'  [OK] Created role: {admin_role.name}')

        # Assign all functions to admin role
        admin_role.functions.set([
            profile_func,
            users_parent,
            users_list,
            roles_list,
            functions_list
        ])
        self.stdout.write(f'    [OK] Assigned {admin_role.functions.count()} functions to {admin_role.name}')

        user_role, _ = Role.objects.get_or_create(
            code='USER',
            defaults={
                'name': 'Usuario Regular',
                'description': 'Acceso basico al sistema - solo perfil',
                'cerbos_role': 'user',
                'is_active': True,
                'is_system': True,
                'level': 10
            }
        )
        self.stdout.write(f'  [OK] Created role: {user_role.name}')

        # Assign only profile to regular users
        user_role.functions.set([
            profile_func
        ])
        self.stdout.write(f'    [OK] Assigned {user_role.functions.count()} functions to {user_role.name}')

        # Assign admin role to superuser
        self.stdout.write('\nAssigning roles to users...')

        try:
            admin_user = User.objects.get(username='admin')

            # Check if role assignment already exists
            assignment, created = RoleAssignment.objects.get_or_create(
                user=admin_user,
                role=admin_role,
                defaults={
                    'is_active': True,
                    'assigned_by': admin_user
                }
            )

            if created:
                self.stdout.write(f'  [OK] Assigned role "{admin_role.name}" to user "{admin_user.email}"')
            else:
                self.stdout.write(f'  [INFO] Role "{admin_role.name}" already assigned to "{admin_user.email}"')

        except User.DoesNotExist:
            self.stdout.write(self.style.WARNING('  [WARN] Admin user not found. Please create superuser first.'))

        self.stdout.write(self.style.SUCCESS('\n[SUCCESS] Data population completed successfully!'))
        self.stdout.write('\nSummary:')
        self.stdout.write(f'  - Functions created: {Function.objects.count()}')
        self.stdout.write(f'  - Roles created: {Role.objects.count()}')
        self.stdout.write(f'  - Role assignments: {RoleAssignment.objects.filter(is_active=True).count()}')
