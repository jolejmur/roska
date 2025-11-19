"""
Customer serializers
"""
from rest_framework import serializers
from apps.users.models import Customer, User
from apps.permissions.models import RoleAssignment, Role


class CustomerSerializer(serializers.ModelSerializer):
    """
    Complete Customer serializer for read operations.
    Includes all customer-specific fields and inherited user fields.
    """
    full_name = serializers.SerializerMethodField()
    display_name = serializers.SerializerMethodField()
    profile_picture_url = serializers.SerializerMethodField()
    has_credit_available = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = [
            'id',
            'customer_code',
            'customer_type',
            'email',
            'username',
            'first_name',
            'last_name',
            'full_name',
            'display_name',
            'ci',
            'phone',
            'profile_picture',
            'profile_picture_url',
            'address',
            'city',
            'country',
            'birth_date',
            'tax_id',
            'company_name',
            'contact_person',
            'credit_limit',
            'payment_terms',
            'discount_percentage',
            'notes',
            'is_active_customer',
            'is_active',
            'has_credit_available',
            'roles',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'customer_code', 'created_at', 'updated_at',
            'full_name', 'display_name', 'profile_picture_url',
            'has_credit_available', 'roles'
        ]

    def get_full_name(self, obj):
        """Get full name from first_name and last_name"""
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username

    def get_display_name(self, obj):
        """Get display name (company name or full name)"""
        return obj.display_name

    def get_profile_picture_url(self, obj):
        """Get absolute URL for profile picture"""
        if obj.profile_picture:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_picture.url)
            return obj.profile_picture.url
        return None

    def get_has_credit_available(self, obj):
        """Check if customer has credit available"""
        return obj.has_credit_available

    def get_roles(self, obj):
        """Get active roles assigned to the customer"""
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


class CustomerCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating customers.
    Customers are automatically assigned the CUSTOMER user_type and basic read-only access.
    """
    password = serializers.CharField(write_only=True, min_length=8)
    customer_code = serializers.CharField(required=False, read_only=True)

    class Meta:
        model = Customer
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
            'customer_type',
            'customer_code',
            'tax_id',
            'company_name',
            'contact_person',
            'credit_limit',
            'payment_terms',
            'discount_percentage',
            'notes',
            'is_active_customer',
        ]

    def validate_email(self, value):
        """Validate email is unique"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este correo electrónico ya está registrado")
        return value

    def validate_ci(self, value):
        """Validate CI is unique"""
        if value and User.objects.filter(ci=value).exists():
            raise serializers.ValidationError("Esta cédula de identidad ya está registrada")
        return value

    def validate_tax_id(self, value):
        """Validate tax_id is unique"""
        if value and Customer.objects.filter(tax_id=value).exists():
            raise serializers.ValidationError("Este RUC/NIT ya está registrado")
        return value

    def create(self, validated_data):
        """
        Create customer with hashed password.
        Automatically assigns customer role with read-only permissions.
        """
        # Create customer (password will be hashed automatically by User model)
        password = validated_data.pop('password')
        customer = Customer(**validated_data)
        customer.set_password(password)
        customer.save()

        # Assign basic customer role
        request = self.context.get('request')
        assigned_by = request.user if request else None

        # Assign customer role if it exists
        try:
            customer_role = Role.objects.get(code='customer', is_system=True)
            RoleAssignment.objects.create(
                user=customer,
                role=customer_role,
                assigned_by=assigned_by,
                is_active=True
            )
        except Role.DoesNotExist:
            # If customer role doesn't exist, assign basic_user role
            try:
                basic_role = Role.objects.get(code='basic_user', is_system=True)
                RoleAssignment.objects.create(
                    user=customer,
                    role=basic_role,
                    assigned_by=assigned_by,
                    is_active=True
                )
            except Role.DoesNotExist:
                pass

        return customer


class CustomerUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating customers by admin.
    """
    class Meta:
        model = Customer
        fields = [
            'first_name',
            'last_name',
            'ci',
            'phone',
            'address',
            'city',
            'country',
            'birth_date',
            'customer_type',
            'tax_id',
            'company_name',
            'contact_person',
            'credit_limit',
            'payment_terms',
            'discount_percentage',
            'notes',
            'is_active_customer',
            'is_active',
        ]

    def validate_ci(self, value):
        """Validate CI is unique"""
        if value:
            customer = self.instance
            if User.objects.filter(ci=value).exclude(id=customer.id).exists():
                raise serializers.ValidationError("Esta cédula de identidad ya está registrada")
        return value

    def validate_tax_id(self, value):
        """Validate tax_id is unique"""
        if value:
            customer = self.instance
            if Customer.objects.filter(tax_id=value).exclude(id=customer.id).exists():
                raise serializers.ValidationError("Este RUC/NIT ya está registrado")
        return value

    def update(self, instance, validated_data):
        """Update customer instance"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class CustomerProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for customers to update their own profile.
    Allows editing personal information but NOT financial information or permissions.
    """
    class Meta:
        model = Customer
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
            'contact_person',
        ]

    def validate_ci(self, value):
        """Validate CI is unique"""
        if value:
            customer = self.instance
            if User.objects.filter(ci=value).exclude(id=customer.id).exists():
                raise serializers.ValidationError("Esta cédula de identidad ya está registrada")
        return value

    def update(self, instance, validated_data):
        """Update customer profile"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
