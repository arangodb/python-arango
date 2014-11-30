"""Tests for ArangoDB Databases."""

import unittest
from arango import Arango
from arango.tests.utils import (
    get_next_db_name
)

class DatabaseManagementTest(unittest.TestCase):

    def setUp(self):
        self.arango = Arango()

    def tearDown(self):
        self.arango = None

    def test_database_add_and_remove(self):
        db_name = get_next_db_name(self.arango)
        self.arango.add_database(db_name)
        self.assertIn(db_name, self.arango.databases["all"])

        # Check the properties of the new database
        self.assertEqual(self.arango.db(db_name).name, db_name)
        self.assertEqual(self.arango.db(db_name).is_system, False)

        # Remove the test database
        self.arango.remove_database(db_name)
        self.assertNotIn(db_name, self.arango.databases["all"])

    def test_database_properties(self):
        db = self.arango.database("_system")
        self.assertEqual(db.name, "_system")
        self.assertTrue(isinstance(db.properties, dict))
        self.assertTrue(isinstance(db.id, basestring))
        self.assertTrue(isinstance(db.path, basestring))
        self.assertEqual(db.is_system, True)


if __name__ == "__main__":
    unittest.main()
