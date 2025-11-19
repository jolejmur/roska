"""
Management command to populate database with categories and functions
Creates the complete navigation structure with Cerbos integration
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.navigation.models import Category, Function
from apps.permissions.models import Role, RoleAssignment

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate database with categories, functions, roles, and assignments'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting navigation data population...'))

        # ========================================
        # 1. CREATE CATEGORIES
        # ========================================
        self.stdout.write('\n' + '='*50)
        self.stdout.write('Creating categories...')
        self.stdout.write('='*50)

        admin_category, _ = Category.objects.get_or_create(
            code='administration',
            defaults={
                'name': 'Administración',
                'description': 'Gestión administrativa del sistema',
                'icon': 'fas fa-cogs',
                'color': '#3498db',
                'order': 10,
                'is_active': True,
                'is_system': True
            }
        )
        self.stdout.write(f'  [OK] Created category: {admin_category.name}')

        user_management_category, _ = Category.objects.get_or_create(
            code='user_management',
            defaults={
                'name': 'Gestión de Usuarios',
                'description': 'Administración de usuarios, roles y permisos',
                'icon': 'fas fa-users',
                'color': '#2ecc71',
                'order': 20,
                'is_active': True,
                'is_system': True
            }
        )
        self.stdout.write(f'  [OK] Created category: {user_management_category.name}')

        # ========================================
        # 2. CREATE FUNCTIONS WITH CERBOS RESOURCES
        # ========================================
        self.stdout.write('\n' + '='*50)
        self.stdout.write('Creating functions with Cerbos integration...')
        self.stdout.write('='*50)

        # Mi Perfil (no category - always visible)
        profile_func, _ = Function.objects.get_or_create(
            code='profile',
            defaults={
                'name': 'Mi Perfil',
                'url': '/profile',
                'icon': 'fas fa-user-circle',
                'category': None,  # No category - root level
                'cerbos_resource': None,  # Everyone can access their profile
                'order': 0,
                'is_active': True,
                'is_system': True
            }
        )
        self.stdout.write(f'  [OK] Created function: {profile_func.name}')

        # Usuarios function (with cerbos_resource='user')
        users_func, _ = Function.objects.get_or_create(
            code='users.list',
            defaults={
                'name': 'Usuarios',
                'url': '/users',
                'icon': 'fas fa-user-friends',
                'category': user_management_category,
                'cerbos_resource': 'user',  # Links to Cerbos user policy
                'order': 10,
                'is_active': True,
                'is_system': True
            }
        )
        self.stdout.write(f'  [OK] Created function: {users_func.name} (cerbos_resource=user)')

        # Roles function (with cerbos_resource='role')
        roles_func, _ = Function.objects.get_or_create(
            code='roles.list',
            defaults={
                'name': 'Roles',
                'url': '/roles',
                'icon': 'fas fa-user-tag',
                'category': user_management_category,
                'cerbos_resource': 'role',  # Links to Cerbos role policy
                'order': 20,
                'is_active': True,
                'is_system': True
            }
        )
        self.stdout.write(f'  [OK] Created function: {roles_func.name} (cerbos_resource=role)')

        # Functions function (with cerbos_resource='function')
        functions_func, _ = Function.objects.get_or_create(
            code='functions.list',
            defaults={
                'name': 'Funciones',
                'url': '/functions',
                'icon': 'fas fa-list-ul',
                'category': admin_category,
                'cerbos_resource': 'function',  # Links to Cerbos function policy
                'order': 10,
                'is_active': True,
                'is_system': True
            }
        )
        self.stdout.write(f'  [OK] Created function: {functions_func.name} (cerbos_resource=function)')

        # Categories function (with cerbos_resource='category')
        categories_func, _ = Function.objects.get_or_create(
            code='categories.list',
            defaults={
                'name': 'Categorías',
                'url': '/categories',
                'icon': 'fas fa-folder-open',
                'category': admin_category,
                'cerbos_resource': 'category',  # Links to Cerbos category policy
                'order': 20,
                'is_active': True,
                'is_system': True
            }
        )
        self.stdout.write(f'  [OK] Created function: {categories_func.name} (cerbos_resource=category)')

        # ========================================
        # 3. CREATE ROLES
        # ========================================
        self.stdout.write('\n' + '='*50)
        self.stdout.write('Creating roles...')
        self.stdout.write('='*50)

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
            users_func,
            roles_func,
            functions_func,
            categories_func
        ])
        self.stdout.write(f'    -> Assigned {admin_role.functions.count()} functions to {admin_role.name}')

        user_role, _ = Role.objects.get_or_create(
            code='USER',
            defaults={
                'name': 'Usuario Regular',
                'description': 'Acceso básico al sistema - solo perfil',
                'cerbos_role': 'user',
                'is_active': True,
                'is_system': True,
                'level': 10
            }
        )
        self.stdout.write(f'  [OK] Created role: {user_role.name}')

        # Assign only profile to regular users
        user_role.functions.set([profile_func])
        self.stdout.write(f'    -> Assigned {user_role.functions.count()} functions to {user_role.name}')

        # ========================================
        # 4. ASSIGN ADMIN ROLE TO SUPERUSER
        # ========================================
        self.stdout.write('\n' + '='*50)
        self.stdout.write('Assigning roles to users...')
        self.stdout.write('='*50)

        try:
            # Try to find any superuser
            admin_user = User.objects.filter(is_superuser=True).first()

            if not admin_user:
                # Try to find user named 'admin'
                admin_user = User.objects.filter(username='admin').first()

            if admin_user:
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
            else:
                self.stdout.write(self.style.WARNING('  [WARN] No superuser found. Please create a superuser first.'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  [ERROR] Error assigning roles: {e}'))

        # ========================================
        # 5. SUMMARY
        # ========================================
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('[SUCCESS] Navigation data population completed!'))
        self.stdout.write('='*50)
        self.stdout.write(f'\nSummary:')
        self.stdout.write(f'  - Categories: {Category.objects.count()}')
        self.stdout.write(f'  - Functions: {Function.objects.count()}')
        self.stdout.write(f'  - Roles: {Role.objects.count()}')
        self.stdout.write(f'  - Active assignments: {RoleAssignment.objects.filter(is_active=True).count()}')

        self.stdout.write(f'\nCreated Functions with Cerbos Resources:')
        for func in Function.objects.all().order_by('category__order', 'order'):
            category_name = func.category.name if func.category else "Root"
            resource = func.cerbos_resource or "N/A"
            self.stdout.write(f'  - {func.name} ({category_name}) -> cerbos_resource: {resource}')
