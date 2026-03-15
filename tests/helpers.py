"""
Shared mock helpers used across multiple test modules.
Import from here rather than duplicating in each file.
"""

from src.pycognito import TokenVerificationException


def mock_authenticate_user(_, client=None, client_metadata=None):
    return {
        "AuthenticationResult": {
            "TokenType": "admin",
            "IdToken": "dummy_token",
            "AccessToken": "dummy_token",
            "RefreshToken": "dummy_token",
        }
    }


def mock_get_params(_):
    return {"USERNAME": "bob", "SRP_A": "srp"}


def mock_verify_tokens(self, token, id_name, token_use):
    if "wrong" in token:
        raise TokenVerificationException
    setattr(self, id_name, token)
