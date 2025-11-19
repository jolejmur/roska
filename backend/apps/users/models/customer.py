"""
Customer model - inherits from User
Los clientes son usuarios con acceso de consulta al sistema
"""
from django.db import models
from apps.core.models import TimeStampedModel
from .user import User


class Customer(User):
    """
    Customer model that inherits from User.

    Uses multi-table inheritance (OneToOne relationship with User).
    Customers will have read-only access to the system.

    Additional fields specific to customers:
    - customer_code: unique customer identifier
    - tax_id: RUC/NIT for invoicing
    - company_name: company name (for legal entities)
    - contact_person: contact person name
    - credit_limit: credit limit for the customer
    - payment_terms: payment terms in days (e.g., 30, 60, 90)
    - discount_percentage: default discount percentage
    - notes: internal notes about the customer
    """

    class CustomerType(models.TextChoices):
        INDIVIDUAL = 'INDIVIDUAL', 'Persona Natural'
        BUSINESS = 'BUSINESS', 'Empresa'

    customer_code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Código de Cliente',
        help_text='Código único del cliente en el sistema',
        db_index=True
    )

    customer_type = models.CharField(
        max_length=20,
        choices=CustomerType.choices,
        default=CustomerType.INDIVIDUAL,
        verbose_name='Tipo de Cliente',
        help_text='Persona natural o empresa'
    )

    # Tax information
    tax_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='RUC/NIT',
        help_text='Número de identificación tributaria',
        db_index=True
    )

    # Company information (for business customers)
    company_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Razón Social',
        help_text='Nombre de la empresa (para personas jurídicas)'
    )

    contact_person = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Persona de Contacto',
        help_text='Nombre de la persona de contacto en la empresa'
    )

    # Financial information
    credit_limit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        verbose_name='Límite de Crédito',
        help_text='Límite de crédito en la moneda local'
    )

    payment_terms = models.IntegerField(
        default=30,
        verbose_name='Términos de Pago',
        help_text='Días de crédito para pagos (ej: 30, 60, 90)'
    )

    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        verbose_name='Descuento (%)',
        help_text='Porcentaje de descuento por defecto'
    )

    # Additional information
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Notas',
        help_text='Notas internas sobre el cliente'
    )

    # Status
    is_active_customer = models.BooleanField(
        default=True,
        verbose_name='Cliente Activo',
        help_text='Indica si el cliente está activo para operaciones comerciales'
    )

    class Meta:
        db_table = 'users_customer'
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer_code']),
            models.Index(fields=['tax_id']),
            models.Index(fields=['is_active_customer']),
            models.Index(fields=['company_name']),
        ]

    def __str__(self):
        if self.company_name:
            return f"{self.customer_code} - {self.company_name}"
        return f"{self.customer_code} - {self.get_full_name()}"

    def save(self, *args, **kwargs):
        """
        Override save to:
        1. Set user_type to CUSTOMER automatically
        2. Generate customer_code if not provided
        3. Set is_staff to False (customers should not have staff access)
        """
        # Ensure user_type is CUSTOMER
        self.user_type = User.UserType.CUSTOMER

        # Customers should not have staff access by default
        if not self.pk:  # Only on creation
            self.is_staff = False

        # Generate customer_code if not provided
        if not self.customer_code:
            # Get the last customer code
            last_customer = Customer.objects.all().order_by('-id').first()
            if last_customer and last_customer.customer_code.startswith('CLI'):
                try:
                    last_number = int(last_customer.customer_code[3:])
                    new_number = last_number + 1
                except (ValueError, IndexError):
                    new_number = 1
            else:
                new_number = 1

            self.customer_code = f"CLI{new_number:06d}"

        super().save(*args, **kwargs)

    @property
    def display_name(self):
        """Returns the display name for the customer"""
        if self.customer_type == self.CustomerType.BUSINESS and self.company_name:
            return self.company_name
        return self.get_full_name()

    @property
    def has_credit_available(self):
        """Check if customer has credit available"""
        # This can be extended to check against actual outstanding balance
        return self.credit_limit > 0
