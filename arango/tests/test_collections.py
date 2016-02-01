"""Tests for managing ArangoDB collections."""

import unittest

from arango import Arango
from arango.exceptions import (
    CollectionRotateJournalError,
)
from arango.utils import is_str
from arango.tests.utils import (
    generate_col_name,
    generate_db_name
)


class CollectionManagementTest(unittest.TestCase):
    """Tests for managing ArangoDB collections."""

    def setUp(self):
        self.arango = Arango()
        self.db_name = generate_db_name(self.arango)
        self.db = self.arango.create_database(self.db_name)

        # Test database cleanup
        self.addCleanup(self.arango.delete_database,
                        name=self.db_name, safe_delete=True)

    def test_create_collection(self):
        col_name = generate_col_name(self.db)
        self.db.create_collection(col_name)
        self.assertIn(col_name, self.db.list_collections["all"])

    def test_rename_collection(self):
        # Create a new collection
        col_name = generate_col_name(self.db)
        self.db.create_collection(col_name)
        col_id = self.db.collection(col_name).id
        # Rename the collection
        new_col_name = generate_col_name(self.db)
        self.db.rename_collection(col_name, new_col_name)
        self.assertNotIn(col_name, self.db.list_collections["all"])
        self.assertIn(new_col_name, self.db.list_collections["all"])
        # Ensure it is the same collection by checking the ID
        self.assertEqual(self.db.collection(new_col_name).id, col_id)

    def test_delete_collection(self):
        # Create a new collection
        col_name = generate_col_name(self.db)
        self.db.create_collection(col_name)
        self.assertIn(col_name, self.db.list_collections["all"])
        # Delete the collection and ensure that it's gone
        self.db.delete_collection(col_name)
        self.assertNotIn(col_name, self.db.list_collections)

    def test_collection_create_with_config(self):
        # Create a new collection with custom defined properties
        col_name = generate_col_name(self.db)
        col = self.db.create_collection(
            name=col_name,
            wait_for_sync=True,
            do_compact=False,
            journal_size=7774208,
            is_system=False,
            is_volatile=False,
            key_generator_type="autoincrement",
            allow_user_keys=False,
            key_increment=9,
            key_offset=100,
            is_edge=True,
            number_of_shards=2,
            shard_keys=["test_attr"],
        )
        # Ensure that the new collection's properties are set correctly
        self.assertEqual(col.name, col_name)
        self.assertTrue(col.revision, "0")
        self.assertEqual(col.status, "loaded")
        self.assertEqual(col.journal_size, 7774208)
        self.assertEqual(col.checksum(), 0)
        self.assertEqual(
            col.key_options,
            {
                "allow_user_keys": False,
                "increment": 9,
                "offset": 100,
                "type": "autoincrement"
            }
        )
        self.assertFalse(col.is_system)
        self.assertFalse(col.is_volatile)
        self.assertFalse(col.is_compacted)
        self.assertTrue(col.wait_for_sync)
        self.assertTrue(col.is_edge)
        self.assertTrue(is_str(col.id))
        self.assertTrue(isinstance(col.statistics(), dict))

    def test_collection_setters(self):
        # Create a new collection with predefined properties
        col = self.db.create_collection(
            name=generate_col_name(self.db),
            wait_for_sync=False,
            journal_size=7774208
        )
        self.assertFalse(col.wait_for_sync)
        self.assertEqual(col.journal_size, 7774208)
        # Change the properties of the graph and ensure that it went through
        col.wait_for_sync = True
        col.journal_size = 8884208
        self.assertTrue(col.wait_for_sync)
        self.assertEqual(col.journal_size, 8884208)

    def test_collection_load_unload(self):
        col = self.db.create_collection(generate_col_name(self.db))
        self.assertIn(col.unload(), {"unloaded", "unloading"})
        self.assertIn(col.load(), {"loaded", "loading"})

    def test_collection_rotate_journal(self):
        col = self.db.create_collection(generate_col_name(self.db))
        self.assertRaises(
            CollectionRotateJournalError,
            col.rotate_journal
        )


if __name__ == "__main__":
    unittest.main()
