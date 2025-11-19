"""
User model based on UML diagram
User = Persona (todos son usuarios: empleados, clientes, proveedores, etc.)
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from apps.core.models import TimeStampedModel


class User(AbstractUser, TimeStampedModel):
    """
    Custom User model.
    Extends Django's AbstractUser with created_at/updated_at timestamps.

    Fields from AbstractUser:
    - username: VARCHAR(150) unique
    - email: VARCHAR(254) unique
    - password: VARCHAR(128)
    - first_name: VARCHAR(150)
    - last_name: VARCHAR(150)
    - is_active: BOOLEAN
    - is_staff: BOOLEAN
    - is_superuser: BOOLEAN
    - date_joined: TIMESTAMP
    - last_login: TIMESTAMP nullable

    Additional fields from TimeStampedModel:
    - created_at: TIMESTAMP
    - updated_at: TIMESTAMP
    """
    # User Types
    class UserType(models.TextChoices):
        EMPLOYEE = 'EMPLOYEE', 'Empleado'
        CUSTOMER = 'CUSTOMER', 'Cliente'
        SUPPLIER = 'SUPPLIER', 'Proveedor'
        OTHER = 'OTHER', 'Otro'

    # Override email to make it unique and required
    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name='Email',
        db_index=True
    )

    # Campos de Persona (comunes a todos)
    ci = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        verbose_name='Cédula de Identidad',
        db_index=True,
        help_text='Cédula de identidad o documento de identidad'
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Teléfono',
        help_text='Número de teléfono de contacto'
    )

    profile_picture = models.ImageField(
        upload_to='profile_pictures/%Y/%m/',
        blank=True,
        null=True,
        verbose_name='Foto de perfil',
        help_text='Foto de perfil del usuario'
    )

    address = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Dirección',
        help_text='Dirección completa'
    )

    city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Ciudad'
    )

    country = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='País',
        default='Bolivia'
    )

    birth_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='Fecha de nacimiento'
    )

    user_type = models.CharField(
        max_length=20,
        choices=UserType.choices,
        default=UserType.OTHER,
        verbose_name='Tipo de usuario',
        help_text='Clasificación del usuario en el sistema'
    )

    # We'll use email as the main identifier
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'users_user'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['email']),
            models.Index(fields=['is_active']),
            models.Index(fields=['ci']),
            models.Index(fields=['user_type']),
        ]

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    @property
    def full_name(self):
        """Retorna el nombre completo del usuario"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

    def get_full_name(self):
        """Método requerido por Django"""
        return self.full_name

    def save(self, *args, **kwargs):
        """Override save to auto-generate username from email if not provided"""
        if not self.username:
            self.username = self.email.split('@')[0]
        super().save(*args, **kwargs)
