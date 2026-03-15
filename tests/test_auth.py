import base64
import json
from os import environ
import unittest
from unittest.mock import patch

from botocore.exceptions import ParamValidationError
from botocore.stub import Stubber
import pendulum

from src.pycognito import Cognito, TokenVerificationException
from src.pycognito.aws_srp import AWSSRP

from .helpers import mock_authenticate_user, mock_get_params, mock_verify_tokens


class CognitoAuthTestCase(unittest.TestCase):
    def setUp(self):
        if environ.get("USE_CLIENT_SECRET") == "True":
            self.app_id = environ.get("COGNITO_APP_WITH_SECRET_ID", "app")
            self.client_secret = environ.get("COGNITO_CLIENT_SECRET")
        else:
            self.app_id = environ.get("COGNITO_APP_ID", "app")
            self.client_secret = None
        self.cognito_user_pool_id = environ.get(
            "COGNITO_USER_POOL_ID", "us-east-1_123456789"
        )
        self.username = environ.get("COGNITO_TEST_USERNAME", "bob")
        self.password = environ.get("COGNITO_TEST_PASSWORD", "bobpassword")
        self.user = Cognito(
            self.cognito_user_pool_id,
            self.app_id,
            username=self.username,
            client_secret=self.client_secret,
        )

    @patch("src.pycognito.aws_srp.AWSSRP.authenticate_user", mock_authenticate_user)
    @patch("src.pycognito.Cognito.verify_token", mock_verify_tokens)
    def test_authenticate(self):
        self.user.authenticate(self.password)
        self.assertNotEqual(self.user.access_token, None)
        self.assertNotEqual(self.user.id_token, None)
        self.assertNotEqual(self.user.refresh_token, None)

    @patch("src.pycognito.aws_srp.AWSSRP.authenticate_user", mock_authenticate_user)
    @patch("src.pycognito.Cognito.verify_token", mock_verify_tokens)
    def test_verify_token(self):
        self.user.authenticate(self.password)
        bad_access_token = "{}wrong".format(self.user.access_token)
        with self.assertRaises(TokenVerificationException):
            self.user.verify_token(bad_access_token, "access_token", "access")

    @patch("src.pycognito.Cognito", autospec=True)
    def test_register(self, cognito_user):
        user = cognito_user(
            self.cognito_user_pool_id, self.app_id, username=self.username
        )
        base_attr = dict(
            given_name="Brian",
            family_name="Jones",
            name="Brian Jones",
            email="bjones39@capless.io",
            phone_number="+19194894555",
            gender="Male",
            preferred_username="billyocean",
        )
        user.set_base_attributes(**base_attr)
        user.register("sampleuser", "sample4#Password")

    @patch("src.pycognito.aws_srp.AWSSRP.authenticate_user", mock_authenticate_user)
    @patch("src.pycognito.Cognito.verify_token", mock_verify_tokens)
    @patch("src.pycognito.Cognito._add_secret_hash", return_value=None)
    def test_renew_tokens(self, _):
        stub = Stubber(self.user.client)
        stub.add_response(
            method="initiate_auth",
            service_response={
                "AuthenticationResult": {
                    "TokenType": "admin",
                    "IdToken": "dummy_token",
                    "AccessToken": "dummy_token",
                    "RefreshToken": "dummy_token",
                },
                "ResponseMetadata": {"HTTPStatusCode": 200},
            },
            expected_params={
                "ClientId": self.app_id,
                "AuthFlow": "REFRESH_TOKEN_AUTH",
                "AuthParameters": {"REFRESH_TOKEN": "dummy_token"},
            },
        )
        with stub:
            self.user.authenticate(self.password)
            self.user.renew_access_token()
            stub.assert_no_pending_responses()

    @patch("src.pycognito.Cognito", autospec=True)
    def test_update_profile(self, cognito_user):
        user = cognito_user(
            self.cognito_user_pool_id, self.app_id, username=self.username
        )
        user.authenticate(self.password)
        user.update_profile({"given_name": "Jenkins"})

    def test_admin_get_user(self):
        stub = Stubber(self.user.client)
        stub.add_response(
            method="admin_get_user",
            service_response={
                "Enabled": True,
                "UserStatus": "CONFIRMED",
                "Username": self.username,
                "UserAttributes": [],
            },
            expected_params={
                "UserPoolId": self.cognito_user_pool_id,
                "Username": self.username,
            },
        )
        with stub:
            u = self.user.admin_get_user()
            self.assertEqual(u.username, self.username)
            stub.assert_no_pending_responses()

    def test_check_token(self):
        # JWT with exp set to January 1st, 3000 — should not be expired.
        self.user.access_token = (
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG"
            "9lIiwiaWF0IjoxNTE2MjM5MDIyLCJleHAiOjMyNTAzNjgwMDAwfQ.C-1gPxrhUsiWeCvMvaZuuQYarkDNAc"
            "pEGJPIqu_SrKQ"
        )
        try:
            valid = self.user.check_token()
        except OverflowError:
            self.skipTest("This test requires 64-bit time_t")
        else:
            self.assertFalse(valid)

    def test_check_token_uses_utc(self):
        """
        Regression: check_token must compare against UTC, not local time.
        Patch pendulum.now directly so the boundary is evaluated correctly
        regardless of the system timezone.
        """

        def _b64(data):
            return (
                base64.urlsafe_b64encode(json.dumps(data).encode())
                .rstrip(b"=")
                .decode()
            )

        exp_ts = int(pendulum.datetime(2024, 6, 1, 12, 0, 0, tz="UTC").timestamp())
        token = (
            f"{_b64({'alg': 'HS256', 'typ': 'JWT'})}"
            f".{_b64({'exp': exp_ts, 'sub': 'test'})}"
            f".fakesig"
        )
        self.user.access_token = token

        # One second before expiry → not expired
        one_before = pendulum.datetime(2024, 6, 1, 11, 59, 59, tz="UTC")
        with patch("pendulum.now", return_value=one_before):
            self.assertFalse(self.user.check_token(renew=False))

        # One second after expiry → expired
        one_after = pendulum.datetime(2024, 6, 1, 12, 0, 1, tz="UTC")
        with patch("pendulum.now", return_value=one_after):
            self.assertTrue(self.user.check_token(renew=False))

    @patch("src.pycognito.Cognito", autospec=True)
    def test_validate_verification(self, cognito_user):
        u = cognito_user(self.cognito_user_pool_id, self.app_id, username=self.username)
        u.validate_verification("4321")

    @patch("src.pycognito.Cognito", autospec=True)
    def test_confirm_forgot_password(self, cognito_user):
        u = cognito_user(self.cognito_user_pool_id, self.app_id, username=self.username)
        u.confirm_forgot_password("4553", "samplepassword")
        with self.assertRaises(TypeError):
            u.confirm_forgot_password(self.password)

    @patch("src.pycognito.aws_srp.AWSSRP.authenticate_user", mock_authenticate_user)
    @patch("src.pycognito.Cognito.verify_token", mock_verify_tokens)
    @patch("src.pycognito.Cognito.check_token", return_value=True)
    def test_change_password(self, _):
        self.user.authenticate(self.password)
        stub = Stubber(self.user.client)
        stub.add_response(
            method="change_password",
            service_response={"ResponseMetadata": {"HTTPStatusCode": 200}},
            expected_params={
                "PreviousPassword": self.password,
                "ProposedPassword": "crazypassword$45DOG",
                "AccessToken": self.user.access_token,
            },
        )
        with stub:
            self.user.change_password(self.password, "crazypassword$45DOG")
            stub.assert_no_pending_responses()

        with self.assertRaises(ParamValidationError):
            self.user.change_password(self.password, None)

    def test_set_attributes(self):
        user = Cognito(self.cognito_user_pool_id, self.app_id)
        user._set_attributes(
            {"ResponseMetadata": {"HTTPStatusCode": 200}}, {"somerandom": "attribute"}
        )
        self.assertEqual(user.somerandom, "attribute")

    @patch("src.pycognito.Cognito.verify_token", mock_verify_tokens)
    def test_admin_authenticate(self):
        """
        admin_authenticate must use ALLOW_ADMIN_USER_PASSWORD_AUTH (not the
        deprecated ADMIN_NO_SRP_AUTH) after the section-2 fix.
        """
        stub = Stubber(self.user.client)
        stub.add_response(
            method="admin_initiate_auth",
            service_response={
                "AuthenticationResult": {
                    "TokenType": "admin",
                    "IdToken": "dummy_token",
                    "AccessToken": "dummy_token",
                    "RefreshToken": "dummy_token",
                }
            },
            expected_params={
                "UserPoolId": self.cognito_user_pool_id,
                "ClientId": self.app_id,
                # Fixed in section 2: was ADMIN_NO_SRP_AUTH
                "AuthFlow": "ALLOW_ADMIN_USER_PASSWORD_AUTH",
                "AuthParameters": {
                    "USERNAME": self.username,
                    "PASSWORD": self.password,
                },
            },
        )
        with stub:
            self.user.admin_authenticate(self.password)
            self.assertNotEqual(self.user.access_token, None)
            self.assertNotEqual(self.user.id_token, None)
            self.assertNotEqual(self.user.refresh_token, None)
            stub.assert_no_pending_responses()


class AWSSRPTestCase(unittest.TestCase):
    def setUp(self):
        if environ.get("USE_CLIENT_SECRET") == "True":
            self.client_secret = environ.get("COGNITO_CLIENT_SECRET")
            self.app_id = environ.get("COGNITO_APP_WITH_SECRET_ID", "app")
        else:
            self.app_id = environ.get("COGNITO_APP_ID", "app")
            self.client_secret = None
        self.cognito_user_pool_id = environ.get(
            "COGNITO_USER_POOL_ID", "us-east-1_123456789"
        )
        self.username = environ.get("COGNITO_TEST_USERNAME")
        self.password = environ.get("COGNITO_TEST_PASSWORD")
        self.aws = AWSSRP(
            username=self.username,
            password=self.password,
            pool_region="us-east-1",
            pool_id=self.cognito_user_pool_id,
            client_id=self.app_id,
            client_secret=self.client_secret,
        )

    def tearDown(self):
        del self.aws

    @patch("src.pycognito.aws_srp.AWSSRP.get_auth_params", mock_get_params)
    @patch("src.pycognito.aws_srp.AWSSRP.process_challenge", return_value={})
    def test_authenticate_user(self, _):
        stub = Stubber(self.aws.client)
        stub.add_response(
            method="initiate_auth",
            service_response={
                "ChallengeName": "PASSWORD_VERIFIER",
                "ChallengeParameters": {},
            },
            expected_params={
                "AuthFlow": "USER_SRP_AUTH",
                "AuthParameters": mock_get_params(None),
                "ClientId": self.app_id,
            },
        )
        stub.add_response(
            method="respond_to_auth_challenge",
            service_response={
                "AuthenticationResult": {
                    "IdToken": "dummy_token",
                    "AccessToken": "dummy_token",
                    "RefreshToken": "dummy_token",
                }
            },
            expected_params={
                "ClientId": self.app_id,
                "ChallengeName": "PASSWORD_VERIFIER",
                "ChallengeResponses": {},
            },
        )
        with stub:
            tokens = self.aws.authenticate_user()
            self.assertTrue("IdToken" in tokens["AuthenticationResult"])
            self.assertTrue("AccessToken" in tokens["AuthenticationResult"])
            self.assertTrue("RefreshToken" in tokens["AuthenticationResult"])
            stub.assert_no_pending_responses()

    def test_cognito_formatted_timestamp(self):
        """
        get_cognito_formatted_timestamp now accepts pendulum DateTime objects.
        The format must match Cognito's expected pattern:
        'Www Mmm D HH:MM:SS UTC YYYY' — no leading zero on single-digit days.
        """
        cases = [
            (
                pendulum.datetime(2022, 1, 1, 0, 0, 0, tz="UTC"),
                "Sat Jan 1 00:00:00 UTC 2022",
            ),
            (
                pendulum.datetime(2022, 1, 2, 12, 0, 0, tz="UTC"),
                "Sun Jan 2 12:00:00 UTC 2022",
            ),
            (
                pendulum.datetime(2022, 1, 3, 9, 0, 0, tz="UTC"),
                "Mon Jan 3 09:00:00 UTC 2022",
            ),
            (
                pendulum.datetime(2022, 12, 31, 23, 59, 59, tz="UTC"),
                "Sat Dec 31 23:59:59 UTC 2022",
            ),
        ]
        for dt, expected in cases:
            with self.subTest(dt=dt):
                self.assertEqual(self.aws.get_cognito_formatted_timestamp(dt), expected)

    def test_cognito_formatted_timestamp_no_leading_zero(self):
        """
        Cognito requires no leading zero on single-digit day numbers.
        Previously stripped with re.sub; pendulum's D token handles it natively.
        """
        result = self.aws.get_cognito_formatted_timestamp(
            pendulum.datetime(2022, 3, 5, 8, 0, 0, tz="UTC")
        )
        self.assertEqual(result, "Sat Mar 5 08:00:00 UTC 2022")
        self.assertNotIn(" 05 ", result)

    def test_process_challenge_timestamp_is_utc(self):
        """
        process_challenge must embed a UTC timestamp; verify the string
        contains 'UTC' and matches Cognito's format when time is patched.
        """
        frozen_moment = pendulum.datetime(2024, 3, 7, 15, 30, 0, tz="UTC")
        challenge_parameters = {
            "USERNAME": self.username or "testuser",
            "USER_ID_FOR_SRP": self.username or "testuser",
            "SALT": "00" * 16,
            "SRP_B": "00" * 16,
            "SECRET_BLOCK": "",
        }
        # Patch pendulum.now so the embedded TIMESTAMP is deterministic,
        # and mock HKDF/HMAC so we only need to inspect TIMESTAMP.
        with (
            patch("pendulum.now", return_value=frozen_moment),
            patch.object(
                self.aws,
                "get_password_authentication_key",
                return_value=b"\x00" * 16,
            ),
            patch("src.pycognito.aws_srp.base64.standard_b64decode", return_value=b""),
            patch("src.pycognito.aws_srp.hmac.new") as mock_hmac,
        ):
            mock_hmac.return_value.digest.return_value = b"\x00" * 32
            response = self.aws.process_challenge(
                challenge_parameters, {"USERNAME": "testuser"}
            )

        self.assertIn("UTC", response["TIMESTAMP"])
        self.assertEqual(response["TIMESTAMP"], "Thu Mar 7 15:30:00 UTC 2024")


if __name__ == "__main__":
    unittest.main()
