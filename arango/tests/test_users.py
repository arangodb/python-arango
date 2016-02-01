"""Tests for ArangoDB users."""

import unittest

from arango import Arango
from arango.tests.utils import (
    generate_user_name
)
from arango.exceptions import (
    UserNotFoundError,
    UserCreateError,
    UserUpdateError,
    UserReplaceError,
    UserDeleteError
)


class UserManagementTest(unittest.TestCase):

    def setUp(self):
        self.arango = Arango()
        self.username = generate_user_name(self.arango)

        # Test user cleanup
        self.addCleanup(self.arango.delete_user,
                        username=self.username, safe_delete=True)

    def test_get_user(self):
        self.assertEqual(
            self.arango.create_user(self.username, "password"),
            {"active": True, "change_password": False, "extra": {}}
        )
        self.assertEqual(
            self.arango.user(self.username),
            {"active": True, "change_password": False, "extra": {}}
        )
        # Retrieving a non-existing user should fail
        self.assertRaises(
            UserNotFoundError,
            self.arango.user,
            username=generate_user_name(self.arango)
        )

    def test_create_user(self):
        self.assertEqual(
            self.arango.create_user(
                username=self.username,
                password="password",
                change_password=True,
                extra={"key": "val"}
            ),
            {
                "active": True,
                "change_password": True,
                "extra": {"key": "val"}
            }
        )
        self.assertIn(self.username, self.arango.list_users())
        self.assertEqual(
            self.arango.user(username=self.username),
            {
                "active": True,
                "change_password": True,
                "extra": {"key": "val"}
            }
        )
        # Creating duplicate user should fail
        self.assertRaises(
            UserCreateError,
            self.arango.create_user,
            username=self.username,
            password="password"
        )

    def test_update_user(self):
        self.assertEqual(
            self.arango.create_user(self.username, "password"),
            {"active": True, "change_password": False, "extra": {}}
        )
        self.assertEqual(
            self.arango.update_user(
                username=self.username,
                password="new_password",
                change_password=True,
                extra={"key": "val"}
            ),
            {
                "active": True,
                "change_password": True,
                "extra": {"key": "val"}
            }
        )
        self.assertEqual(
            self.arango.user(username=self.username),
            {
                "active": True,
                "change_password": True,
                "extra": {"key": "val"}
            }
        )
        # Updating a non-existing user should fail
        self.assertRaises(
            UserUpdateError,
            self.arango.update_user,
            username=generate_user_name(self.arango),
            password="password"
        )

    def test_replace_user(self):
        self.arango.create_user(
            username=self.username,
            password="password",
            change_password=True,
            extra={"key": "val"}
        ),
        self.assertEqual(
            self.arango.replace_user(
                username=self.username,
                password="new_password",
            ),
            {
                "active": True,
                "change_password": False,
                "extra": {}
            }
        )
        self.assertEqual(
            self.arango.user(username=self.username),
            {
                "active": True,
                "change_password": False,
                "extra": {}
            }
        )

        # Updating non-existing user should fail
        self.assertRaises(
            UserReplaceError,
            self.arango.replace_user,
            username=generate_user_name(self.arango),
            password="password"
        )

    def test_delete_user(self):
        self.assertEqual(
            self.arango.create_user(self.username, "password"),
            {"active": True, "change_password": False, "extra": {}}
        )
        self.assertIn(self.username, self.arango.list_users())
        self.arango.delete_user(self.username)
        self.assertNotIn(self.username, self.arango.list_users())

        # Deleting non-existing user should fail
        self.assertRaises(
            UserDeleteError,
            self.arango.delete_user,
            username=generate_user_name(self.arango)
        )


if __name__ == "__main__":
    unittest.main()
