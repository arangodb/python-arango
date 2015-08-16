"""Tests for ArangoDB users."""

import unittest

from arango import Arango
from arango.utils import is_string
from arango.tests.utils import (
    get_next_db_name
)


class UserManagementTest(unittest.TestCase):

    def setUp(self):
        self.arango = Arango()

    def test_create_user(self):
        pass

    def test_update_user(self):
        pass

    def test_replace_user(self):
        pass

    def test_delete_user(self):
        pass


if __name__ == "__main__":
    unittest.main()
