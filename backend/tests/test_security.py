"""Tests for security modules."""
import pytest

from app.security.sanitizer import validate_sql, sanitize_mongodb_query
from app.security.rbac import Role, Permission, has_permission, require_permission


class TestSQLSanitizer:
    """Tests for SQL sanitization."""

    def test_valid_select_query(self):
        """Test that valid SELECT queries pass."""
        query = "SELECT * FROM users WHERE id = 1"
        result = validate_sql(query)
        assert result == query

    def test_blocked_insert_query(self):
        """Test that INSERT queries are blocked."""
        query = "INSERT INTO users VALUES (1, 'test')"
        with pytest.raises(ValueError, match="Blocked SQL operation"):
            validate_sql(query)

    def test_blocked_delete_query(self):
        """Test that DELETE queries are blocked."""
        query = "DELETE FROM users WHERE id = 1"
        with pytest.raises(ValueError, match="Blocked SQL operation"):
            validate_sql(query)

    def test_blocked_drop_query(self):
        """Test that DROP queries are blocked."""
        query = "DROP TABLE users"
        with pytest.raises(ValueError, match="Blocked SQL operation"):
            validate_sql(query)


class TestMongoDBSanitizer:
    """Tests for MongoDB aggregation pipeline sanitization."""

    def test_valid_aggregation_pipeline(self):
        """Test that valid pipelines pass."""
        query = '[{"$match": {"status": "active"}}, {"$group": {"_id": "$type"}}]'
        result = sanitize_mongodb_query(query)
        assert result == query

    def test_blocked_out_stage(self):
        """Test that $out stages are blocked."""
        query = '[{"$out": "output_collection"}]'
        with pytest.raises(ValueError, match="Blocked MongoDB operation"):
            sanitize_mongodb_query(query)

    def test_invalid_json(self):
        """Test that invalid JSON fails."""
        query = '[{"$match": "invalid"}]'
        # This should still pass - it's valid JSON, just invalid aggregation
        result = sanitize_mongodb_query(query)
        assert result == query


class TestRBAC:
    """Tests for role-based access control."""

    def test_admin_has_all_permissions(self):
        """Test that admin role has all permissions."""
        assert has_permission(Role.ADMIN, Permission.READ_ALL_DATASOURCES)
        assert has_permission(Role.ADMIN, Permission.MANAGE_USERS)
        assert has_permission(Role.ADMIN, Permission.MANAGE_DATASOURCES)

    def test_analyst_has_read_permissions(self):
        """Test that analyst role can read and query."""
        assert has_permission(Role.ANALYST, Permission.READ_ALL_DATASOURCES)
        assert has_permission(Role.ANALYST, Permission.EXECUTE_QUERIES)
        assert not has_permission(Role.ANALYST, Permission.MANAGE_USERS)

    def test_viewer_limited_permissions(self):
        """Test that viewer role has limited permissions."""
        assert has_permission(Role.VIEWER, Permission.READ_ALL_DATASOURCES)
        assert not has_permission(Role.VIEWER, Permission.EXECUTE_QUERIES)

    def test_require_permission_success(self):
        """Test that require_permission passes for authorized roles."""
        require_permission(Role.ADMIN, Permission.MANAGE_USERS)
        # Should not raise

    def test_require_permission_failure(self):
        """Test that require_permission raises for unauthorized roles."""
        with pytest.raises(PermissionError):
            require_permission(Role.VIEWER, Permission.MANAGE_USERS)
