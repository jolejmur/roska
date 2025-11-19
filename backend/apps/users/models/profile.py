"""
User Profile model based on UML diagram
"""
from django.db import models
from apps.core.models import TimeStampedModel


class UserProfile(TimeStampedModel):
    """
    Extended user profile information.
    OneToOne relationship with User model.

    Fields according to UML diagram:
    - user_id: BigInteger (FK to users_user) unique
    - phone: VARCHAR(20) nullable
    - mobile: VARCHAR(20) nullable
    - avatar: VARCHAR(255) nullable
    - bio: TEXT nullable
    - birth_date: DATE nullable
    - document_type: VARCHAR(20) nullable (DNI, PASAPORTE, etc.)
    - document_number: VARCHAR(50) nullable
    - address: VARCHAR(255) nullable
    - city: VARCHAR(100) nullable
    - state: VARCHAR(100) nullable
    - country: VARCHAR(100) (default 'BO')
    - postal_code: VARCHAR(20) nullable
    - latitude: DECIMAL(10,7) nullable
    - longitude: DECIMAL(10,7) nullable
    - language: VARCHAR(10) (default 'es')
    - timezone: VARCHAR(50) (default 'America/La_Paz')
    - created_at: TIMESTAMP
    - updated_at: TIMESTAMP
    """
    user = models.OneToOneField(
        'users.User',
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='Usuario',
        db_index=True
    )

    # Contact information
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Teléfono'
    )

    mobile = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Móvil'
    )

    # Profile picture
    avatar = models.ImageField(
        upload_to='avatars/',
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Avatar'
    )

    # Personal information
    bio = models.TextField(
        blank=True,
        null=True,
        verbose_name='Biografía'
    )

    birth_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='Fecha de nacimiento'
    )

    # Identification documents
    document_type = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Tipo de documento',
        help_text='DNI, CI, PASAPORTE, etc.'
    )

    document_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Número de documento',
        db_index=True
    )

    # Address information
    address = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Dirección'
    )

    city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Ciudad'
    )

    state = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Departamento/Estado'
    )

    country = models.CharField(
        max_length=100,
        default='BO',
        verbose_name='País',
        help_text='Código ISO del país (BO para Bolivia)'
    )

    postal_code = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Código postal'
    )

    # Geolocation
    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        blank=True,
        null=True,
        verbose_name='Latitud'
    )

    longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        blank=True,
        null=True,
        verbose_name='Longitud'
    )

    # Localization preferences
    language = models.CharField(
        max_length=10,
        default='es',
        verbose_name='Idioma',
        help_text='Código de idioma (es, en, etc.)'
    )

    timezone = models.CharField(
        max_length=50,
        default='America/La_Paz',
        verbose_name='Zona horaria'
    )

    class Meta:
        db_table = 'users_userprofile'
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['document_number']),
        ]

    def __str__(self):
        return f"Perfil de {self.user.email}"
