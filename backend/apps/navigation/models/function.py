from django.db import models


class Function(models.Model):
    """
    Modelo para representar funciones/opciones del menú.
    Cada función tiene una URL, icono, orden y está ligada a un recurso de Cerbos.

    Las funciones se agrupan en categorías y pueden tener jerarquía (parent/children).
    """
    name = models.CharField(
        max_length=100,
        verbose_name='Nombre',
        help_text='Nombre descriptivo de la función (ej: "Listar Usuarios")'
    )
    code = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Código',
        help_text='Código único para identificar la función (ej: "users.list")'
    )
    url = models.CharField(
        max_length=200,
        verbose_name='URL',
        help_text='Ruta de la función en Angular (ej: "/users")',
        blank=True,
        null=True
    )
    icon = models.CharField(
        max_length=100,
        verbose_name='Icono',
        help_text='Clase CSS del icono (ej: "fas fa-users")',
        default='fas fa-circle'
    )

    # Nueva relación con Category
    category = models.ForeignKey(
        'navigation.Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='functions',
        verbose_name='Categoría',
        help_text='Categoría a la que pertenece esta función'
    )

    # Campo para integración con Cerbos
    cerbos_resource = models.CharField(
        max_length=100,
        verbose_name='Recurso Cerbos',
        help_text='Nombre del recurso en Cerbos (ej: "user", "role", "function", "category")',
        blank=True,
        null=True
    )

    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='Función padre',
        help_text='Función padre para crear submenús'
    )
    order = models.IntegerField(
        default=0,
        verbose_name='Orden',
        help_text='Orden de aparición en el menú (menor = primero)'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo',
        help_text='Si la función está activa o no'
    )

    is_system = models.BooleanField(
        default=False,
        verbose_name='Función del sistema',
        help_text='Las funciones del sistema no pueden ser eliminadas'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'navigation_functions'
        verbose_name = 'Función'
        verbose_name_plural = 'Funciones'
        ordering = ['order', 'name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['parent', 'order']),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"

    def get_full_path(self):
        """Retorna el path completo incluyendo padres"""
        if self.parent:
            return f"{self.parent.get_full_path()} > {self.name}"
        return self.name
