"""Tests for ArangoDB Databases."""

import unittest
from arango import Arango


class DatabaseManagementTest(unittest.TestCase):

    def setUp(self):
        self.arango = Arango()

    def test_database_add_and_remove(self):
        dbs = self.arango.databases["all"]

        # Add a new test database
        db_num = 0
        while "db_{}".format(db_num) in dbs:
            db_num += 1
        db_name = "db_{}".format(db_num)
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
        self.assertTrue(isinstance(db.id, str))
        self.assertTrue(isinstance(db.path, str))
        self.assertEqual(db.is_system, True)


if __name__ == "__main__":
    unittest.main()
