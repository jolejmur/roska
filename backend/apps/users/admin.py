"""
Admin configuration for Users app
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from apps.users.models import User, UserProfile, Customer


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom User admin
    """
    list_display = ['email', 'username', 'first_name', 'last_name', 'is_active', 'is_superuser', 'date_joined']
    list_filter = ['is_active', 'is_superuser', 'is_staff', 'date_joined']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering = ['-date_joined']

    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Información Personal', {'fields': ('first_name', 'last_name')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas Importantes', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser'),
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    User Profile admin
    """
    list_display = ['user', 'phone', 'city', 'country', 'created_at']
    search_fields = ['user__email', 'phone', 'city']
    list_filter = ['country', 'created_at']
    ordering = ['-created_at']


@admin.register(Customer)
class CustomerAdmin(BaseUserAdmin):
    """
    Customer admin - extends UserAdmin to include customer-specific fields
    """
    list_display = [
        'customer_code', 'email', 'display_name', 'customer_type',
        'is_active_customer', 'credit_limit', 'created_at'
    ]
    list_filter = [
        'is_active_customer', 'customer_type', 'is_active',
        'payment_terms', 'created_at'
    ]
    search_fields = [
        'customer_code', 'email', 'username', 'first_name',
        'last_name', 'company_name', 'tax_id'
    ]
    ordering = ['-created_at']
    readonly_fields = ['customer_code', 'created_at', 'updated_at']

    fieldsets = (
        (None, {
            'fields': ('email', 'username', 'password')
        }),
        ('Información del Cliente', {
            'fields': (
                'customer_code', 'customer_type', 'tax_id',
                'company_name', 'contact_person'
            )
        }),
        ('Información Personal', {
            'fields': ('first_name', 'last_name', 'ci', 'phone')
        }),
        ('Dirección', {
            'fields': ('address', 'city', 'country')
        }),
        ('Información Financiera', {
            'fields': (
                'credit_limit', 'payment_terms', 'discount_percentage'
            )
        }),
        ('Estado y Notas', {
            'fields': ('is_active_customer', 'is_active', 'notes')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at', 'last_login', 'date_joined')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'username', 'password1', 'password2',
                'first_name', 'last_name', 'customer_type',
                'company_name', 'tax_id', 'is_active_customer'
            ),
        }),
    )

    def display_name(self, obj):
        """Display customer name"""
        return obj.display_name
    display_name.short_description = 'Nombre'
