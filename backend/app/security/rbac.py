"""Role-based access control (RBAC) for datasource permissions."""
import logging
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)


class Role(str, Enum):
    """User roles in the system."""

    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"


class Permission(str, Enum):
    """Permission types."""

    READ_ALL_DATASOURCES = "read:all_datasources"
    READ_OWN_DATASOURCES = "read:own_datasources"
    EXECUTE_QUERIES = "execute:queries"
    MANAGE_DATASOURCES = "manage:datasources"
    MANAGE_USERS = "manage:users"


# Role-to-permissions mapping
ROLE_PERMISSIONS: dict[Role, set[Permission]] = {
    Role.ADMIN: {
        Permission.READ_ALL_DATASOURCES,
        Permission.EXECUTE_QUERIES,
        Permission.MANAGE_DATASOURCES,
        Permission.MANAGE_USERS,
    },
    Role.ANALYST: {
        Permission.READ_ALL_DATASOURCES,
        Permission.EXECUTE_QUERIES,
    },
    Role.VIEWER: {
        Permission.READ_ALL_DATASOURCES,
    },
}


def get_permissions(role: Role) -> set[Permission]:
    """
    Get all permissions for a given role.
    
    Args:
        role: The user's role
    
    Returns:
        Set of permissions for that role
    """
    return ROLE_PERMISSIONS.get(role, set())


def has_permission(role: Role, permission: Permission) -> bool:
    """
    Check if a role has a specific permission.
    
    Args:
        role: The user's role
        permission: The permission to check
    
    Returns:
        True if the role has the permission, False otherwise
    """
    permissions = get_permissions(role)
    has_it = permission in permissions
    logger.info(f"Permission check: {role} + {permission} = {has_it}")
    return has_it


def require_permission(role: Role, permission: Permission) -> None:
    """
    Assert that a role has the required permission.
    
    Args:
        role: The user's role
        permission: The required permission
    
    Raises:
        PermissionError: If the role does not have the permission
    """
    if not has_permission(role, permission):
        raise PermissionError(
            f"Role '{role}' does not have permission '{permission}'"
        )


# Datasource-level access control
class DatasourceACL:
    """Access control list for datasource access."""

    def __init__(self, datasource_id: str, owner_id: str):
        self.datasource_id = datasource_id
        self.owner_id = owner_id
        self.allowed_roles: set[Role] = {Role.ADMIN, Role.ANALYST}
        self.allowed_users: set[str] = {owner_id}

    def can_read(self, user_id: str, role: Role) -> bool:
        """
        Check if a user can read this datasource.
        
        Args:
            user_id: The user's ID
            role: The user's role
        
        Returns:
            True if the user can access the datasource
        """
        # Admins can always read
        if role == Role.ADMIN:
            return True
        
        # Check explicit permissions
        if user_id in self.allowed_users:
            return True
        
        # Check role-based permissions
        if role in self.allowed_roles:
            return True
        
        return False

    def add_user(self, user_id: str) -> None:
        """Grant access to a specific user."""
        self.allowed_users.add(user_id)

    def add_role(self, role: Role) -> None:
        """Grant access to users with a specific role."""
        self.allowed_roles.add(role)

    def remove_user(self, user_id: str) -> None:
        """Revoke access from a specific user."""
        self.allowed_users.discard(user_id)

    def remove_role(self, role: Role) -> None:
        """Revoke access from users with a specific role."""
        self.allowed_roles.discard(role)
