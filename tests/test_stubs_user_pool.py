"""
Tests for not-yet-implemented stubs in user_pool.py.

Implemented stubs (real tests elsewhere):
  - create_group, update_group, delete_group → test_user_pool.py: GroupCRUDTestCase
  - list_users_in_group                      → test_user_pool.py: ListUsersInGroupTestCase
  - describe_user_pool, update_user_pool     → test_user_pool.py: UserPoolConfigTestCase
  - admin_link_provider_for_user (pending — no moto support)
  - admin_disable_provider_for_user (pending — no moto support)
  - device methods (5) (pending — no moto support)
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
# Device management (no moto support)
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
# Federated identity (no moto support)
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


if __name__ == "__main__":
    unittest.main()
