"""Tests for ArangoDB queries."""

import unittest

from arango import Arango
from arango.exceptions import *
from arango.tests.test_utils import (
    get_next_col_name,
    get_next_db_name
)

class ArangoDBQueryTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.arango = Arango()
        cls.db_name = get_next_db_name(cls.arango)
        cls.db = cls.arango.add_database(cls.db_name)

    @classmethod
    def tearDownClass(cls):
        cls.arango.remove_database(cls.db_name)

    def test_explain_query(self):
        pass

    def test_validate_query(self):
        pass

    def test_execute_query(self):
        pass


if __name__ == "__main__":
    unittest.main()

