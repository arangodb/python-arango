"""Tests for managing ArangoDB indexes."""

import unittest

from arango import Arango
from arango.exceptions import (
    IndexCreateError,
)
from arango.tests.utils import (
    generate_col_name,
    generate_db_name
)


class IndexManagementTest(unittest.TestCase):
    """Tests for managing ArangoDB indexes."""

    def setUp(self):
        self.arango = Arango()
        self.db_name = generate_db_name(self.arango)
        self.db = self.arango.create_database(self.db_name)
        self.col_name = generate_col_name(self.db)
        self.col = self.db.create_collection(self.col_name)

        # Test database cleanup
        self.addCleanup(self.arango.delete_database,
                        name=self.db_name, safe_delete=True)

    def test_list_indexes(self):
        self.assertIn(
            {
                "selectivity_estimate": 1,
                "sparse": False,
                "type": "primary",
                "fields": ["_key"],
                "unique": True
            },
            self.col.indexes.values()
        )

    def test_create_hash_index(self):
        self.col.create_hash_index(["attr1", "attr2"], unique=True)
        self.assertIn(
            {
                "selectivity_estimate": 1,
                "sparse": False,
                "type": "hash",
                "fields": ["attr1", "attr2"],
                "unique": True
            },
            self.col.indexes.values()
        )

    def test_create_cap_constraint(self):
        self.col.create_cap_constraint(size=10, byte_size=40000)
        self.assertIn(
            {
                "type": "cap",
                "size": 10,
                "byte_size": 40000,
                "unique": False
            },
            self.col.indexes.values()
        )

    def test_create_skiplist_index(self):
        self.col.create_skiplist_index(["attr1", "attr2"], unique=True)
        self.assertIn(
            {
                "sparse": False,
                "type": "skiplist",
                "fields": ["attr1", "attr2"],
                "unique": True
            },
            self.col.indexes.values()
        )

    def test_create_geo_index_with_one_attr(self):
        self.col.create_geo_index(
            fields=["attr1"],
            geo_json=False,
        )
        self.assertIn(
            {
                "sparse": True,
                "type": "geo1",
                "fields": ["attr1"],
                "unique": False,
                "geo_json": False,
                "ignore_null": True,
                "constraint": False
            },
            self.col.indexes.values()
        )

    def test_create_geo_index_with_two_attrs(self):
        self.col.create_geo_index(
            fields=["attr1", "attr2"],
            geo_json=False,
        )
        self.assertIn(
            {
                "sparse": True,
                "type": "geo2",
                "fields": ["attr1", "attr2"],
                "unique": False,
                "ignore_null": True,
                "constraint": False
            },
            self.col.indexes.values()
        )

    def test_create_geo_index_with_more_than_two_attrs(self):
        self.assertRaises(
            IndexCreateError,
            self.col.create_geo_index,
            fields=["attr1", "attr2", "attr3"]
        )

    def test_create_fulltext_index(self):
        self.assertRaises(
            IndexCreateError,
            self.col.create_fulltext_index,
            fields=["attr1", "attr2"]
        )
        self.col.create_fulltext_index(
            fields=["attr1"],
            min_length=10,
        )
        self.assertIn(
            {
                "sparse": True,
                "type": "fulltext",
                "fields": ["attr1"],
                "min_length": 10,
                "unique": False,
            },
            self.col.indexes.values()
        )

    def test_delete_index(self):
        old_indexes = set(self.col.indexes)
        self.col.create_hash_index(["attr1", "attr2"], unique=True)
        self.col.create_skiplist_index(["attr1", "attr2"], unique=True)
        self.col.create_fulltext_index(
            fields=["attr1"],
            min_length=10,
        )
        new_indexes = set(self.col.indexes)
        self.assertNotEqual(old_indexes, new_indexes)

        for index_id in new_indexes - old_indexes:
            self.col.delete_index(index_id)

        self.assertEqual(old_indexes, set(self.col.indexes))


if __name__ == "__main__":
    unittest.main()
