from rest_framework import serializers
from apps.navigation.models import Function


class FunctionSerializer(serializers.ModelSerializer):
    """
    Serializer for Function model
    Includes nested children for building menu tree
    """
    children = serializers.SerializerMethodField()
    parent_name = serializers.CharField(source='parent.name', read_only=True, allow_null=True)
    category_name = serializers.CharField(source='category.name', read_only=True, allow_null=True)
    category_code = serializers.CharField(source='category.code', read_only=True, allow_null=True)

    class Meta:
        model = Function
        fields = [
            'id',
            'name',
            'code',
            'url',
            'icon',
            'category',
            'category_name',
            'category_code',
            'cerbos_resource',
            'parent',
            'parent_name',
            'order',
            'is_active',
            'is_system',
            'children',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'parent_name', 'category_name', 'category_code']

    def get_children(self, obj):
        """Get children functions recursively"""
        children = obj.children.filter(is_active=True).order_by('order', 'name')
        # Prevent infinite recursion by limiting depth
        if hasattr(self, '_depth'):
            if self._depth >= 3:
                return []
        else:
            self._depth = 0

        self._depth += 1
        serializer = FunctionSerializer(children, many=True, context=self.context)
        self._depth -= 1
        return serializer.data


class FunctionListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing functions without nested children
    """
    parent_name = serializers.CharField(source='parent.name', read_only=True, allow_null=True)
    category_name = serializers.CharField(source='category.name', read_only=True, allow_null=True)
    full_path = serializers.CharField(source='get_full_path', read_only=True)

    class Meta:
        model = Function
        fields = [
            'id',
            'name',
            'code',
            'url',
            'icon',
            'category',
            'category_name',
            'cerbos_resource',
            'parent',
            'parent_name',
            'order',
            'is_active',
            'is_system',
            'full_path',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'parent_name', 'category_name', 'full_path']


class FunctionCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating/updating functions.
    Only allows editing: name, order, and category.
    Other fields (code, url, icon, cerbos_resource, parent, is_system) are system-managed.
    """
    class Meta:
        model = Function
        fields = [
            'id',
            'name',
            'code',
            'url',
            'icon',
            'category',
            'cerbos_resource',
            'parent',
            'order',
            'is_active',
            'is_system'
        ]
        read_only_fields = ['id', 'code', 'url', 'icon', 'cerbos_resource', 'parent', 'is_system']

    def validate_parent(self, value):
        """Prevent circular references"""
        if value and self.instance:
            # Check if the new parent is a descendant of this function
            current = value
            while current:
                if current.id == self.instance.id:
                    raise serializers.ValidationError(
                        "No se puede establecer como padre a un descendiente de esta función"
                    )
                current = current.parent
        return value

    def validate_code(self, value):
        """Ensure code is unique"""
        if self.instance and self.instance.code == value:
            return value

        if Function.objects.filter(code=value).exists():
            raise serializers.ValidationError("Ya existe una función con este código")

        return value

    def validate(self, data):
        """Additional validations"""
        # Prevent deactivating system functions
        if self.instance and self.instance.is_system:
            if 'is_active' in data and not data['is_active']:
                raise serializers.ValidationError({
                    'is_active': 'No se puede desactivar una función del sistema'
                })
        return data
