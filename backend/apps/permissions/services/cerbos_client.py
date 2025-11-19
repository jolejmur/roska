"""
Cerbos client service
Migrated from FastAPI app/cerbos/client.py
"""
from cerbos.sdk.client import CerbosClient
from cerbos.sdk.model import Principal, Resource
from django.conf import settings
from typing import Dict, Any, List, TYPE_CHECKING

if TYPE_CHECKING:
    from apps.users.models import User


class CerbosService:
    """
    Service for interacting with Cerbos.
    Migrated from FastAPI CerbosService.
    """

    def __init__(self):
        """Initialize Cerbos client"""
        self.client = CerbosClient(
            host=settings.CERBOS_GRPC_ADDRESS,
            tls_verify=False  # In development, use certificates in production
        )

    def check_user_permission(
        self,
        user: "User",
        resource_type: str,
        resource_id: str,
        action: str,
        resource_attr: Dict[str, Any] = None
    ) -> bool:
        """
        Check permissions using a User object directly.
        Compatible with FastAPI implementation.

        Args:
            user: User object from Django
            resource_type: Resource type (e.g., 'user')
            resource_id: Resource ID
            action: Action to verify (e.g., 'read', 'update', 'delete')
            resource_attr: Additional resource attributes

        Returns:
            bool: True if has permission, False otherwise
        """
        principal = Principal(
            id=str(user.id),
            roles=set(),  # Don't use roles, only is_superuser
            attr={
                "is_superuser": user.is_superuser,
                "email": user.email
            }
        )

        resource = Resource(
            id=str(resource_id),
            kind=resource_type,
            attr=resource_attr or {}
        )

        try:
            result = self.client.is_allowed(
                action=action,
                principal=principal,
                resource=resource
            )
            return result
        except Exception as e:
            print(f"⚠️ Cerbos Error: {e}")
            print(f"🔄 Fallback: Using is_superuser={user.is_superuser} for {action} on {resource_type}")
            # FALLBACK: Si Cerbos falla, usar is_superuser para desarrollo
            # En producción, esto debería ser más restrictivo
            return user.is_superuser

    def get_user_permissions_for_resource(
        self,
        user: "User",
        resource_type: str,
        resource_id: str = "generic",
        resource_attr: Dict[str, Any] = None
    ) -> Dict[str, bool]:
        """
        Get all CRUD permissions for a user on a resource.
        Compatible with FastAPI implementation.

        Args:
            user: User object from Django
            resource_type: Resource type (e.g., 'user')
            resource_id: Resource ID (default: 'generic')
            resource_attr: Additional resource attributes

        Returns:
            Dict with permissions: {"create": bool, "read": bool, "update": bool, "delete": bool, "list": bool}
        """
        actions = ["create", "read", "update", "delete", "list"]
        permissions = {}

        for action in actions:
            permissions[action] = self.check_user_permission(
                user=user,
                resource_type=resource_type,
                resource_id=resource_id,
                action=action,
                resource_attr=resource_attr
            )

        return permissions

    def check_permission(
        self,
        user_id: str,
        roles: List[str],
        resource_type: str,
        resource_id: str,
        action: str,
        attributes: Dict[str, Any] = None
    ) -> bool:
        """
        Check if a user has permission to perform an action on a resource.
        Compatible with FastAPI implementation.

        Args:
            user_id: User ID
            roles: List of user roles
            resource_type: Resource type (e.g., 'radiador')
            resource_id: Resource ID
            action: Action to verify (e.g., 'read', 'create', 'update', 'delete')
            attributes: Additional resource attributes

        Returns:
            bool: True if has permission, False otherwise
        """
        principal = Principal(
            id=user_id,
            roles=set(roles),
            attr={}
        )

        resource = Resource(
            id=resource_id,
            kind=resource_type,
            attr=attributes or {}
        )

        try:
            result = self.client.is_allowed(
                action=action,
                principal=principal,
                resource=resource
            )
            return result
        except Exception as e:
            print(f"Error verifying permissions with Cerbos: {e}")
            return False

    def check_multiple_permissions(
        self,
        user_id: str,
        roles: List[str],
        resource_type: str,
        resource_id: str,
        actions: List[str],
        attributes: Dict[str, Any] = None
    ) -> Dict[str, bool]:
        """
        Check multiple permissions at once.
        Compatible with FastAPI implementation.

        Returns:
            Dict[str, bool]: Dictionary with actions and whether they are allowed
        """
        principal = Principal(
            id=user_id,
            roles=set(roles),
            attr={}
        )

        resource = Resource(
            id=resource_id,
            kind=resource_type,
            attr=attributes or {}
        )

        try:
            results = {}
            for action in actions:
                results[action] = self.client.is_allowed(
                    action=action,
                    principal=principal,
                    resource=resource
                )
            return results
        except Exception as e:
            print(f"Error verifying multiple permissions with Cerbos: {e}")
            return {action: False for action in actions}


# Global service instance
cerbos_service = CerbosService()
