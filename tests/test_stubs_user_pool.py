"""
Tests for not-yet-implemented stubs in user_pool.py:
  - Device management
  - Group CRUD
  - Federated identity
  - User pool management

Replace each assertRaises block with real assertions as each stub is
implemented.
"""

import unittest

from src.pycognito import Cognito


class _Base(unittest.TestCase):
    POOL_ID = "us-east-1_123456789"
    CLIENT_ID = "testclientid"
    USERNAME = "testuser"
    DEVICE_KEY = "us-east-1_device_abc123"

    def _cognito(self):
        return Cognito(
            user_pool_id=self.POOL_ID,
            client_id=self.CLIENT_ID,
            username=self.USERNAME,
        )


# ---------------------------------------------------------------------------
# Device management
# ---------------------------------------------------------------------------


class DeviceManagementStubsTestCase(_Base):
    def test_list_devices_not_implemented(self):
        with self.assertRaises(NotImplementedError) as ctx:
            self._cognito().list_devices()
        self.assertIn("list_devices", str(ctx.exception))

    def test_list_devices_accepts_pagination_params(self):
        """Placeholder: once implemented, verify limit and pagination_token are forwarded."""
        with self.assertRaises(NotImplementedError):
            self._cognito().list_devices(limit=10, pagination_token="tok")

    def test_admin_list_devices_not_implemented(self):
        with self.assertRaises(NotImplementedError) as ctx:
            self._cognito().admin_list_devices()
        self.assertIn("admin_list_devices", str(ctx.exception))

    def test_admin_list_devices_accepts_username(self):
        """Placeholder: once implemented, verify username is forwarded."""
        with self.assertRaises(NotImplementedError):
            self._cognito().admin_list_devices(username="someone")

    def test_get_device_not_implemented(self):
        with self.assertRaises(NotImplementedError) as ctx:
            self._cognito().get_device(self.DEVICE_KEY)
        self.assertIn("get_device", str(ctx.exception))

    def test_admin_get_device_not_implemented(self):
        with self.assertRaises(NotImplementedError) as ctx:
            self._cognito().admin_get_device(self.DEVICE_KEY)
        self.assertIn("admin_get_device", str(ctx.exception))

    def test_admin_get_device_accepts_username(self):
        """Placeholder: once implemented, verify username overrides self.username."""
        with self.assertRaises(NotImplementedError):
            self._cognito().admin_get_device(self.DEVICE_KEY, username="otheruser")

    def test_admin_forget_device_not_implemented(self):
        with self.assertRaises(NotImplementedError) as ctx:
            self._cognito().admin_forget_device(self.DEVICE_KEY)
        self.assertIn("admin_forget_device", str(ctx.exception))

    def test_admin_forget_device_accepts_username(self):
        """Placeholder: once implemented, verify username overrides self.username."""
        with self.assertRaises(NotImplementedError):
            self._cognito().admin_forget_device(self.DEVICE_KEY, username="otheruser")


# ---------------------------------------------------------------------------
# Group CRUD
# ---------------------------------------------------------------------------


class GroupCRUDStubsTestCase(_Base):
    def test_create_group_not_implemented(self):
        with self.assertRaises(NotImplementedError) as ctx:
            self._cognito().create_group("my-group")
        self.assertIn("create_group", str(ctx.exception))

    def test_create_group_accepts_optional_params(self):
        """Placeholder: once implemented, verify description/role_arn/precedence are forwarded."""
        with self.assertRaises(NotImplementedError):
            self._cognito().create_group(
                "my-group",
                description="desc",
                role_arn="arn:aws:iam::123:role/MyRole",
                precedence=10,
            )

    def test_update_group_not_implemented(self):
        with self.assertRaises(NotImplementedError) as ctx:
            self._cognito().update_group("my-group")
        self.assertIn("update_group", str(ctx.exception))

    def test_update_group_accepts_optional_params(self):
        """Placeholder: once implemented, verify partial updates are supported."""
        with self.assertRaises(NotImplementedError):
            self._cognito().update_group("my-group", description="new desc")

    def test_delete_group_not_implemented(self):
        with self.assertRaises(NotImplementedError) as ctx:
            self._cognito().delete_group("my-group")
        self.assertIn("delete_group", str(ctx.exception))

    def test_list_users_in_group_not_implemented(self):
        with self.assertRaises(NotImplementedError) as ctx:
            self._cognito().list_users_in_group("my-group")
        self.assertIn("list_users_in_group", str(ctx.exception))

    def test_list_users_in_group_accepts_pagination_params(self):
        """Placeholder: once implemented, verify page_limit and page_token are forwarded."""
        with self.assertRaises(NotImplementedError):
            self._cognito().list_users_in_group(
                "my-group", page_limit=5, page_token="tok"
            )


# ---------------------------------------------------------------------------
# Federated identity
# ---------------------------------------------------------------------------


class FederatedIdentityStubsTestCase(_Base):
    def test_admin_link_provider_for_user_not_implemented(self):
        with self.assertRaises(NotImplementedError) as ctx:
            self._cognito().admin_link_provider_for_user(
                destination_username=self.USERNAME,
                provider_name="Google",
                provider_attribute_name="Cognito_Subject",
                provider_attribute_value="google-sub-123",
            )
        self.assertIn("admin_link_provider_for_user", str(ctx.exception))

    def test_admin_disable_provider_for_user_not_implemented(self):
        with self.assertRaises(NotImplementedError) as ctx:
            self._cognito().admin_disable_provider_for_user(
                provider_name="Google",
                provider_attribute_value="google-sub-123",
            )
        self.assertIn("admin_disable_provider_for_user", str(ctx.exception))


# ---------------------------------------------------------------------------
# User pool management
# ---------------------------------------------------------------------------


class UserPoolManagementStubsTestCase(_Base):
    def test_describe_user_pool_not_implemented(self):
        with self.assertRaises(NotImplementedError) as ctx:
            self._cognito().describe_user_pool()
        self.assertIn("describe_user_pool", str(ctx.exception))

    def test_describe_user_pool_accepts_explicit_pool_id(self):
        """Placeholder: once implemented, verify an explicit pool_id is accepted."""
        with self.assertRaises(NotImplementedError):
            self._cognito().describe_user_pool(pool_id="us-east-1_other")

    def test_update_user_pool_not_implemented(self):
        with self.assertRaises(NotImplementedError) as ctx:
            self._cognito().update_user_pool()
        self.assertIn("update_user_pool", str(ctx.exception))

    def test_update_user_pool_passes_kwargs(self):
        """Placeholder: once implemented, verify kwargs reach UpdateUserPool."""
        with self.assertRaises(NotImplementedError):
            self._cognito().update_user_pool(
                Policies={"PasswordPolicy": {"MinimumLength": 12}}
            )


if __name__ == "__main__":
    unittest.main()
