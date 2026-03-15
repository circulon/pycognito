import unittest

import boto3
import moto

from src.pycognito import Cognito, is_cognito_attr_list

# ---------------------------------------------------------------------------
# Shared pool setup used by all three test cases in this module
# ---------------------------------------------------------------------------


def _create_pool_and_client(cognito_idp_client, pool_name="pycognito-test-pool"):
    user_pool = cognito_idp_client.create_user_pool(
        PoolName=pool_name,
        AliasAttributes=["email"],
        UsernameAttributes=["email"],
    )
    return user_pool["UserPool"]["Id"]


TOKEN_VALIDITY_PARAMS = {
    "RefreshTokenValidity": 1,
    "AccessTokenValidity": 1,
    "IdTokenValidity": 1,
    "TokenValidityUnits": {
        "AccessToken": "hour",
        "IdToken": "hour",
        "RefreshToken": "days",
    },
}


# ---------------------------------------------------------------------------
# User pool client CRUD
# ---------------------------------------------------------------------------


@moto.mock_aws
class CognitoUserPoolClientTestCase(unittest.TestCase):
    client_name = "test-client"

    def setUp(self) -> None:
        self.cognito_idp = boto3.client("cognito-idp", region_name="us-east-1")
        self.user_pool_id = _create_pool_and_client(self.cognito_idp)
        self.params = TOKEN_VALIDITY_PARAMS.copy()

    def test_create_user_pool_client(self):
        cognito = Cognito(user_pool_id=self.user_pool_id, client_id=None)
        response = cognito.create_user_pool_client(
            client_name=self.client_name, **self.params
        )
        self.assertEqual(response["ClientName"], self.client_name)
        self.assertEqual(response["AccessTokenValidity"], 1)

    def test_describe_user_pool_client(self):
        params = self.params.copy()
        params.update({"UserPoolId": self.user_pool_id, "ClientName": self.client_name})
        response = self.cognito_idp.create_user_pool_client(**params)

        client_id = response["UserPoolClient"]["ClientId"]
        cognito = Cognito(user_pool_id=self.user_pool_id, client_id=client_id)
        response = cognito.describe_user_pool_client(
            pool_id=self.user_pool_id, client_id=client_id
        )
        self.assertEqual(response["UserPoolId"], self.user_pool_id)
        self.assertEqual(response["ClientId"], client_id)
        self.assertEqual(response["ClientName"], self.client_name)


# ---------------------------------------------------------------------------
# Pagination
# ---------------------------------------------------------------------------


@moto.mock_aws
class PaginationTestCase(unittest.TestCase):
    invalid_user_pool_id = "us-east-1_123456789"

    def setUp(self) -> None:
        cognito_idp_client = boto3.client("cognito-idp", region_name="us-east-1")
        self.user_pool_id = _create_pool_and_client(cognito_idp_client)

        for i in range(2):
            cognito_idp_client.admin_create_user(
                UserPoolId=self.user_pool_id,
                Username=f"user{i}@test.com",
                TemporaryPassword="Testing123!",
                MessageAction="SUPPRESS",
            )
            cognito_idp_client.create_group(
                GroupName=f"group-{i}", UserPoolId=self.user_pool_id
            )
            cognito_idp_client.create_user_pool_client(
                UserPoolId=self.user_pool_id,
                ClientName=f"test-client-{i}",
                **TOKEN_VALIDITY_PARAMS,
            )

    def test_user_pagination(self):
        cognito = Cognito(user_pool_id=self.user_pool_id)

        user_one = cognito.get_users(pool_id=self.user_pool_id, page_limit=1)
        self.assertEqual(len(user_one), 1)

        page_token = cognito.get_users_pagination_token()
        self.assertIsNotNone(page_token)

        user_two = cognito.get_users(page_limit=1, page_token=page_token)
        self.assertEqual(len(user_two), 1)

        self.assertIsNone(cognito.get_users_pagination_token())

        all_users = cognito.get_users()
        self.assertEqual(len(all_users), 2)

        # Pool ID override still works
        cognito.user_pool_id = self.invalid_user_pool_id
        self.assertEqual(len(cognito.get_users(pool_id=self.user_pool_id)), 2)

    def test_group_pagination(self):
        cognito = Cognito(user_pool_id=self.user_pool_id)

        group_one = cognito.get_groups(pool_id=self.user_pool_id, page_limit=1)
        self.assertEqual(len(group_one), 1)

        page_token = cognito.get_groups_pagination_token()
        self.assertIsNotNone(page_token)

        group_two = cognito.get_groups(page_limit=1, page_token=page_token)
        self.assertEqual(len(group_two), 1)

        self.assertIsNone(cognito.get_groups_pagination_token())

        all_groups = cognito.get_groups()
        self.assertEqual(len(all_groups), 2)

        cognito.user_pool_id = self.invalid_user_pool_id
        self.assertEqual(len(cognito.get_groups(pool_id=self.user_pool_id)), 2)

    def test_client_pagination(self):
        cognito = Cognito(user_pool_id=self.user_pool_id)

        client_one = cognito.list_user_pool_clients(
            pool_id=self.user_pool_id, page_limit=1
        )
        self.assertEqual(len(client_one), 1)

        page_token = cognito.get_clients_pagination_token()
        self.assertIsNotNone(page_token)

        client_two = cognito.list_user_pool_clients(page_limit=1, page_token=page_token)
        self.assertEqual(len(client_two), 1)

        self.assertIsNone(cognito.get_clients_pagination_token())

        all_clients = cognito.list_user_pool_clients()
        self.assertEqual(len(all_clients), 2)

        cognito.user_pool_id = self.invalid_user_pool_id
        self.assertEqual(
            len(cognito.list_user_pool_clients(pool_id=self.user_pool_id)), 2
        )


# ---------------------------------------------------------------------------
# Admin profile updates
# ---------------------------------------------------------------------------


@moto.mock_aws
class AdminUpdateProfileTestCase(unittest.TestCase):
    username = "user@test.com"
    password = "Testing123!"

    def setUp(self) -> None:
        cognito_idp_client = boto3.client("cognito-idp", region_name="us-east-1")
        self.user_pool_id = _create_pool_and_client(cognito_idp_client)

        cognito_idp_client.admin_create_user(
            UserPoolId=self.user_pool_id,
            Username=self.username,
            TemporaryPassword=self.password,
            MessageAction="SUPPRESS",
        )
        cognito_idp_client.admin_set_user_password(
            UserPoolId=self.user_pool_id,
            Username=self.username,
            Password=self.password,
            Permanent=True,
        )
        client_app = cognito_idp_client.create_user_pool_client(
            UserPoolId=self.user_pool_id,
            ClientName="test-client",
            **TOKEN_VALIDITY_PARAMS,
        )
        self.client_id = client_app["UserPoolClient"]["ClientId"]

    def test_cognito_attr_list(self):
        self.assertFalse(
            is_cognito_attr_list(
                [{"Name": "given_name", "Value": "John", "Bad_Key": "Test"}]
            )
        )
        self.assertFalse(
            is_cognito_attr_list(
                [{"Name": "given_name", "Value": "John"}, {"Bad_Key": "Test"}]
            )
        )
        self.assertTrue(
            is_cognito_attr_list(
                [
                    {"Name": "given_name", "Value": "John"},
                    {"Name": "middle_name", "Value": "Smith"},
                ]
            )
        )

    def test_user_admin_update_profile(self):
        cognito = Cognito(
            user_pool_id=self.user_pool_id,
            username=self.username,
            client_id=self.client_id,
        )
        cognito.authenticate(self.password)

        cognito.admin_update_profile(attrs={"given_name": "John"})
        self.assertEqual(cognito.get_user().given_name, "John")

        cognito.admin_update_profile(
            attrs={"gn": "Steve"}, attr_map={"given_name": "gn"}
        )
        self.assertEqual(cognito.get_user().given_name, "Steve")

        cognito.admin_update_profile(
            attrs=[{"Name": "given_name", "Value": "Bob"}], username=self.username
        )
        self.assertEqual(cognito.get_user().given_name, "Bob")

        # is_cognito_attr_list returns False on bad input, so dict_to_cognito is
        # called and raises AttributeError on the list.
        with self.assertRaises(AttributeError) as ctx:
            cognito.admin_update_profile(
                attrs=[{"Name": "given_name", "Value": "John", "Bad_Key": "Test"}],
                username=self.username,
            )
        self.assertEqual(str(ctx.exception), "'list' object has no attribute 'items'")


if __name__ == "__main__":
    unittest.main()
