"""
Tests for not-yet-implemented MFA configuration stubs in mfa.py:
  - admin_set_user_mfa_preference
  - get_user_pool_mfa_config
  - set_user_pool_mfa_config

Replace each assertRaises block with real assertions as each stub is
implemented.
"""

import unittest

from src.pycognito import Cognito


class MFAConfigStubsTestCase(unittest.TestCase):
    POOL_ID = "us-east-1_123456789"
    CLIENT_ID = "testclientid"
    USERNAME = "testuser"

    def _cognito(self):
        return Cognito(
            user_pool_id=self.POOL_ID,
            client_id=self.CLIENT_ID,
            username=self.USERNAME,
        )

    def test_admin_set_user_mfa_preference_not_implemented(self):
        with self.assertRaises(NotImplementedError) as ctx:
            self._cognito().admin_set_user_mfa_preference(
                username=self.USERNAME,
                sms_mfa=False,
                software_token_mfa=True,
                preferred="SOFTWARE_TOKEN",
            )
        self.assertIn("admin_set_user_mfa_preference", str(ctx.exception))

    def test_admin_set_user_mfa_preference_disable_mfa(self):
        """Placeholder: once implemented, verify disabling both MFA types is accepted."""
        with self.assertRaises(NotImplementedError):
            self._cognito().admin_set_user_mfa_preference(
                username=self.USERNAME,
                sms_mfa=False,
                software_token_mfa=False,
            )

    def test_get_user_pool_mfa_config_not_implemented(self):
        with self.assertRaises(NotImplementedError) as ctx:
            self._cognito().get_user_pool_mfa_config()
        self.assertIn("get_user_pool_mfa_config", str(ctx.exception))

    def test_get_user_pool_mfa_config_accepts_explicit_pool_id(self):
        """Placeholder: once implemented, verify an explicit pool_id is accepted."""
        with self.assertRaises(NotImplementedError):
            self._cognito().get_user_pool_mfa_config(pool_id="us-east-1_other")

    def test_set_user_pool_mfa_config_not_implemented(self):
        with self.assertRaises(NotImplementedError) as ctx:
            self._cognito().set_user_pool_mfa_config(
                MfaConfiguration="ON",
                SoftwareTokenMfaConfiguration={"Enabled": True},
            )
        self.assertIn("set_user_pool_mfa_config", str(ctx.exception))

    def test_set_user_pool_mfa_config_accepts_explicit_pool_id(self):
        """Placeholder: once implemented, verify an explicit pool_id is accepted."""
        with self.assertRaises(NotImplementedError):
            self._cognito().set_user_pool_mfa_config(
                pool_id="us-east-1_other",
                MfaConfiguration="OPTIONAL",
            )


if __name__ == "__main__":
    unittest.main()
