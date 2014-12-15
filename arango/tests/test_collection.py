"""Tests for ArangoDB Collections."""

import unittest
from arango import Arango


class CollectionTest(unittest.TestCase):

    def setUp(self):
        self.arango = Arango()

    def test_collection_basic_add_rename_remove(self):
        # Add a new test collection
        col_num = 0
        while "col_{}".format(col_num) in self.arango.collections:
            col_num += 1
        col_name = "col_{}".format(col_num)
        self.arango.add_collection(col_name)
        self.assertIn(col_name, self.arango.collections)
        col_id = self.arango.collection(col_name).id

        # Rename the test collection
        while "col_{}".format(col_num) in self.arango.collections:
            col_num += 1
        new_col_name = "col_{}".format(col_num)
        self.arango.rename_collection(col_name, new_col_name)
        self.assertNotIn(col_name, self.arango.collections)
        self.assertIn(new_col_name, self.arango.collections)
        self.assertEqual(self.arango.collection(new_col_name).id, col_id)

        # Remove the test collection
        self.arango.remove_collection(new_col_name)
        self.assertNotIn(new_col_name, self.arango.collections)

    def test_collection_properties(self):
        # Add a new test collection
        col_num = 0
        while "col_{}".format(col_num) in self.arango.collections:
            col_num += 1
        col_name = "col_{}".format(col_num)
        self.arango.add_collection(col_name)
        col = self.arango.collection(col_name)

        self.assertEqual(col.status, "new")
        self.assertEqual(col.name, col_name)
        self.assertEqual(col.is_edge, False)
        self.assertEqual(col.is_system, False)
        self.assertEqual(col.is_volatile, False)

        self.assertTrue(isinstance(col.properties, dict))
        self.assertTrue(isinstance(col.id, str))
        self.assertTrue(isinstance(col.key_options, dict))
        self.assertTrue(isinstance(col.journal_size, int))

        self.arango.remove_collection(new_col_name)

    def test_collection_count(self):



def add_test_collection(arango):
    col_num = 0
    while "col_{}".format(col_num) in arango.collections:
        col_num += 1
    return "col_{}".format(col_num)

if __name__ == "__main__":
    unittest.main()

