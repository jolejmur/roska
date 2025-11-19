"""
Management command to clear all menu data
Removes all functions, non-system roles, and role assignments
"""
from django.core.management.base import BaseCommand
from apps.navigation.models import Function
from apps.permissions.models import Role, RoleAssignment


class Command(BaseCommand):
    help = 'Clear all menu functions and role assignments'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Clearing all menu data...'))

        # Delete all role assignments
        count = RoleAssignment.objects.count()
        RoleAssignment.objects.all().delete()
        self.stdout.write(f'  [OK] Deleted {count} role assignments')

        # Delete all functions
        count = Function.objects.count()
        Function.objects.all().delete()
        self.stdout.write(f'  [OK] Deleted {count} functions')

        # Delete non-system roles or update system roles
        system_roles = Role.objects.filter(is_system=True)
        for role in system_roles:
            role.functions.clear()
            self.stdout.write(f'  [OK] Cleared functions from system role: {role.name}')

        self.stdout.write(self.style.SUCCESS('\n[SUCCESS] Menu data cleared successfully!'))
