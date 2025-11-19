"""
Category serializers for navigation
"""
from rest_framework import serializers
from apps.navigation.models import Category


class CategorySerializer(serializers.ModelSerializer):
    """
    Complete Category serializer for read operations
    """
    active_functions_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'code',
            'description',
            'icon',
            'color',
            'order',
            'is_active',
            'is_system',
            'active_functions_count',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'active_functions_count']

    def get_active_functions_count(self, obj):
        """Get number of active functions in this category"""
        return obj.get_active_functions_count()


class CategoryListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing categories
    """
    active_functions_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'code',
            'icon',
            'color',
            'order',
            'is_active',
            'is_system',
            'active_functions_count'
        ]
        read_only_fields = ['id', 'active_functions_count']

    def get_active_functions_count(self, obj):
        """Get number of active functions in this category"""
        return obj.get_active_functions_count()


class CategoryCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating/updating categories
    """
    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'code',
            'description',
            'icon',
            'color',
            'order',
            'is_active'
        ]
        read_only_fields = ['id']

    def validate_code(self, value):
        """Ensure code is unique"""
        # Si estamos actualizando y el código no cambió, permitirlo
        if self.instance and self.instance.code == value:
            return value

        # Verificar si el código ya existe
        if Category.objects.filter(code=value).exists():
            raise serializers.ValidationError("Ya existe una categoría con este código")

        return value

    def validate(self, data):
        """Additional validations"""
        # Prevent disabling system categories
        if self.instance and self.instance.is_system:
            # Solo prevenir desactivación, permitir otros cambios
            if 'is_active' in data and not data['is_active']:
                raise serializers.ValidationError({
                    'is_active': 'No se puede desactivar una categoría del sistema'
                })

            # Prevenir cambio de código en categorías del sistema
            if 'code' in data and data['code'] != self.instance.code:
                raise serializers.ValidationError({
                    'code': 'No se puede cambiar el código de una categoría del sistema'
                })

        return data
