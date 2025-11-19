"""
User serializers
"""
from rest_framework import serializers
from apps.users.models import User
from apps.permissions.models import RoleAssignment, Role


class UserSerializer(serializers.ModelSerializer):
    """
    Complete User serializer for read operations.
    Includes all person fields (CI, phone, profile_picture, etc.)
    """
    full_name = serializers.SerializerMethodField()
    profile_picture_url = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'full_name',
            'ci',
            'phone',
            'profile_picture',
            'profile_picture_url',
            'address',
            'city',
            'country',
            'birth_date',
            'user_type',
            'is_active',
            'is_superuser',
            'is_staff',
            'roles',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'full_name', 'profile_picture_url', 'roles']

    def get_full_name(self, obj):
        """Get full name from first_name and last_name"""
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username

    def get_profile_picture_url(self, obj):
        """Get absolute URL for profile picture"""
        if obj.profile_picture:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_picture.url)
            return obj.profile_picture.url
        return None

    def get_roles(self, obj):
        """Get active roles assigned to the user"""
        active_assignments = obj.role_assignments.filter(is_active=True).select_related('role')
        return [
            {
                'id': assignment.role.id,
                'name': assignment.role.name,
                'code': assignment.role.code,
                'assignment_id': assignment.id,
            }
            for assignment in active_assignments
        ]


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating users.
    Only superadmin can create users.
    NOTE: Users are assigned ROLES via RoleAssignment, not user_type.
    """
    password = serializers.CharField(write_only=True, min_length=8)
    role_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text="List of role IDs to assign to the user"
    )

    class Meta:
        model = User
        fields = [
            'email',
            'username',
            'password',
            'first_name',
            'last_name',
            'ci',
            'phone',
            'address',
            'city',
            'country',
            'birth_date',
            'is_active',
            'is_staff',
            'role_ids',
        ]

    def create(self, validated_data):
        """Create user with hashed password and assign roles"""
        role_ids = validated_data.pop('role_ids', [])

        # create_user handles password hashing automatically
        user = User.objects.create_user(**validated_data)

        # Assign roles to the user
        request = self.context.get('request')
        assigned_by = request.user if request else None

        # ALWAYS assign the basic user role automatically
        try:
            basic_role = Role.objects.get(code='basic_user', is_system=True)
            RoleAssignment.objects.create(
                user=user,
                role=basic_role,
                assigned_by=assigned_by,
                is_active=True
            )
        except Role.DoesNotExist:
            pass  # If basic_user role doesn't exist, skip

        # Assign additional roles specified by the admin
        for role_id in role_ids:
            try:
                role = Role.objects.get(id=role_id)
                # Skip if it's the basic_user role (already assigned)
                if role.code == 'basic_user':
                    continue
                RoleAssignment.objects.create(
                    user=user,
                    role=role,
                    assigned_by=assigned_by,
                    is_active=True
                )
            except Role.DoesNotExist:
                pass  # Skip invalid role IDs

        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating users by admin.
    NOTE: Users are assigned ROLES via RoleAssignment, not user_type.
    """
    role_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text="List of role IDs to assign to the user"
    )

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'ci',
            'phone',
            'address',
            'city',
            'country',
            'birth_date',
            'is_active',
            'is_staff',
            'role_ids',
        ]

    def update(self, instance, validated_data):
        """Update user instance and handle role assignments"""
        role_ids = validated_data.pop('role_ids', None)

        # Debug logging
        print(f"\n[DEBUG] Updating user {instance.username}")
        print(f"[DEBUG] Received role_ids: {role_ids}")
        print(f"[DEBUG] Type of role_ids: {type(role_ids)}")

        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update role assignments if role_ids were provided
        if role_ids is not None:
            request = self.context.get('request')
            assigned_by = request.user if request else None

            # Deactivate all current role assignments EXCEPT the basic_user role
            instance.role_assignments.filter(
                is_active=True
            ).exclude(
                role__code='basic_user',
                role__is_system=True
            ).update(is_active=False)

            # Create new role assignments
            for role_id in role_ids:
                try:
                    role = Role.objects.get(id=role_id)
                    # Check if assignment already exists (was deactivated)
                    assignment, created = RoleAssignment.objects.get_or_create(
                        user=instance,
                        role=role,
                        scope_type=None,
                        scope_id=None,
                        defaults={'assigned_by': assigned_by, 'is_active': True}
                    )
                    if not created:
                        # Reactivate existing assignment
                        assignment.is_active = True
                        assignment.assigned_by = assigned_by
                        assignment.save()
                except Role.DoesNotExist:
                    pass  # Skip invalid role IDs

            # ALWAYS ensure the basic_user role is active
            try:
                basic_role = Role.objects.get(code='basic_user', is_system=True)
                assignment, created = RoleAssignment.objects.get_or_create(
                    user=instance,
                    role=basic_role,
                    scope_type=None,
                    scope_id=None,
                    defaults={'assigned_by': assigned_by, 'is_active': True}
                )
                if not created and not assignment.is_active:
                    # Reactivate if it was somehow deactivated
                    assignment.is_active = True
                    assignment.save()
            except Role.DoesNotExist:
                pass  # If basic_user role doesn't exist, skip

        return instance


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for users to update their own profile.
    Allows editing personal information but NOT permissions/roles.
    """
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'ci',
            'phone',
            'profile_picture',
            'address',
            'city',
            'country',
            'birth_date',
        ]

    def validate_ci(self, value):
        """Validate CI is unique"""
        if value:
            # Check if CI already exists for another user
            user = self.instance
            if User.objects.filter(ci=value).exclude(id=user.id).exists():
                raise serializers.ValidationError("Esta cédula de identidad ya está registrada")
        return value

    def update(self, instance, validated_data):
        """Update user profile"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
