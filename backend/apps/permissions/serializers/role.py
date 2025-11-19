from rest_framework import serializers
from apps.permissions.models import Role, RoleAssignment
from apps.navigation.serializers import FunctionListSerializer


class RoleSerializer(serializers.ModelSerializer):
    """
    Complete serializer for Role with nested functions
    """
    functions = FunctionListSerializer(many=True, read_only=True)
    function_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=__import__('apps.navigation.models', fromlist=['Function']).Function.objects.all(),
        source='functions',
        required=False
    )
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True, allow_null=True)
    users_count = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = [
            'id',
            'name',
            'code',
            'description',
            'cerbos_role',
            'is_active',
            'is_system',
            'level',
            'functions',
            'function_ids',
            'created_by',
            'created_by_name',
            'users_count',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by_name', 'users_count']

    def get_users_count(self, obj):
        """Get count of active users with this role"""
        return obj.role_assignments.filter(is_active=True).count()


class RoleListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing roles
    """
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True, allow_null=True)
    users_count = serializers.SerializerMethodField()
    functions_count = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = [
            'id',
            'name',
            'code',
            'description',
            'cerbos_role',
            'is_active',
            'is_system',
            'level',
            'created_by_name',
            'users_count',
            'functions_count',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_users_count(self, obj):
        """Get count of active users with this role"""
        return obj.role_assignments.filter(is_active=True).count()

    def get_functions_count(self, obj):
        """Get count of functions assigned to this role"""
        return obj.functions.filter(is_active=True).count()


class RoleCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating/updating roles
    """
    function_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=__import__('apps.navigation.models', fromlist=['Function']).Function.objects.all(),
        required=False
    )

    class Meta:
        model = Role
        fields = [
            'id',
            'name',
            'code',
            'description',
            'cerbos_role',
            'is_active',
            'is_system',
            'level',
            'function_ids'
        ]
        read_only_fields = ['id']

    def validate_code(self, value):
        """Ensure code is unique"""
        if self.instance and self.instance.code == value:
            return value

        if Role.objects.filter(code=value).exists():
            raise serializers.ValidationError("Ya existe un rol con este código")

        return value

    def validate_is_system(self, value):
        """Prevent modifying system roles"""
        if self.instance and self.instance.is_system and not value:
            raise serializers.ValidationError(
                "No se puede desmarcar un rol del sistema"
            )
        return value

    def create(self, validated_data):
        """Create role with functions"""
        function_ids = validated_data.pop('function_ids', [])
        role = Role.objects.create(**validated_data)

        if function_ids:
            role.functions.set(function_ids)

        return role

    def update(self, instance, validated_data):
        """Update role with functions"""
        function_ids = validated_data.pop('function_ids', None)

        # Prevent updating system roles
        if instance.is_system:
            raise serializers.ValidationError(
                "No se pueden modificar los roles del sistema"
            )

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if function_ids is not None:
            instance.functions.set(function_ids)

        return instance


class RoleAssignmentSerializer(serializers.ModelSerializer):
    """
    Serializer for RoleAssignment model
    """
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_full_name = serializers.CharField(source='user.full_name', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)
    assigned_by_name = serializers.CharField(source='assigned_by.full_name', read_only=True, allow_null=True)
    is_expired = serializers.BooleanField(read_only=True)

    class Meta:
        model = RoleAssignment
        fields = [
            'id',
            'user',
            'user_email',
            'user_full_name',
            'role',
            'role_name',
            'assigned_at',
            'assigned_by',
            'assigned_by_name',
            'expires_at',
            'scope_type',
            'scope_id',
            'is_active',
            'is_expired',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'assigned_at',
            'created_at',
            'updated_at',
            'user_email',
            'user_full_name',
            'role_name',
            'assigned_by_name',
            'is_expired'
        ]

    def validate(self, attrs):
        """Validate role assignment"""
        user = attrs.get('user')
        role = attrs.get('role')

        # Check if assignment already exists
        if not self.instance:
            existing = RoleAssignment.objects.filter(
                user=user,
                role=role,
                is_active=True
            ).first()

            if existing:
                raise serializers.ValidationError(
                    f"El usuario {user.email} ya tiene asignado el rol {role.name}"
                )

        return attrs
