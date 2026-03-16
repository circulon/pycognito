"""
Tests for not-yet-implemented stubs in auth.py (auth flows) and
tokens.py (token management).

Implemented stubs (real tests elsewhere):
  - admin_renew_access_token  → test_auth.py: AdminRenewAccessTokenTestCase
  - admin_user_global_sign_out → test_auth.py: AdminUserGlobalSignOutTestCase
"""

import unittest

from src.pycognito import Cognito


class _Base(unittest.TestCase):
    POOL_ID = "us-east-1_123456789"
    CLIENT_ID = "testclientid"
    USERNAME = "testuser"

    def _cognito(self):
        return Cognito(
            user_pool_id=self.POOL_ID,
            client_id=self.CLIENT_ID,
            username=self.USERNAME,
        )


# ---------------------------------------------------------------------------
# Auth flows — authenticate_custom_auth, admin_authenticate_with_mfa
# ---------------------------------------------------------------------------


class AuthFlowStubsTestCase(_Base):
    def test_authenticate_custom_auth_not_implemented(self):
        with self.assertRaises(NotImplementedError) as ctx:
            self._cognito().authenticate_custom_auth()
        self.assertIn("authenticate_custom_auth", str(ctx.exception))

    def test_authenticate_custom_auth_passes_metadata(self):
        """Placeholder: once implemented, verify client_metadata is forwarded."""
        with self.assertRaises(NotImplementedError):
            self._cognito().authenticate_custom_auth(client_metadata={"flow": "custom"})

    def test_admin_authenticate_with_mfa_not_implemented(self):
        with self.assertRaises(NotImplementedError) as ctx:
            self._cognito().admin_authenticate_with_mfa("somepassword")
        self.assertIn("admin_authenticate_with_mfa", str(ctx.exception))

    def test_admin_authenticate_with_mfa_stores_tokens(self):
        """Placeholder: once implemented, verify mfa_tokens is populated."""
        with self.assertRaises(NotImplementedError):
            self._cognito().admin_authenticate_with_mfa("somepassword")


# ---------------------------------------------------------------------------
# Token management — revoke_token (no moto support)
# ---------------------------------------------------------------------------


class TokenManagementStubsTestCase(_Base):
    def test_revoke_token_not_implemented(self):
        with self.assertRaises(NotImplementedError) as ctx:
            self._cognito().revoke_token()
        self.assertIn("revoke_token", str(ctx.exception))

    def test_revoke_token_accepts_explicit_token(self):
        """Placeholder: once implemented, verify an explicit token is accepted."""
        with self.assertRaises(NotImplementedError):
            self._cognito().revoke_token(token="some_refresh_token")

    def test_revoke_token_falls_back_to_self_refresh_token(self):
        """Placeholder: once implemented, verify self.refresh_token is used when token=None."""
        c = self._cognito()
        c.refresh_token = "stored_refresh_token"
        with self.assertRaises(NotImplementedError):
            c.revoke_token()


if __name__ == "__main__":
    unittest.main()
