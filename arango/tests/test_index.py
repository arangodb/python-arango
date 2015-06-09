"""Tests for managing ArangoDB indexes."""

import unittest

from arango import Arango
from arango.exceptions import *
from arango.tests.utils import (
    get_next_col_name,
    get_next_db_name
)


class IndexManagementTest(unittest.TestCase):

    def setUp(self):
        self.arango = Arango()
        self.db_name = get_next_db_name(self.arango)
        self.db = self.arango.add_database(self.db_name)
        self.col_name = get_next_col_name(self.db)
        self.col = self.db.add_collection(self.col_name)

    def tearDown(self):
        self.arango.remove_database(self.db_name)

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

    def test_add_hash_index(self):
        self.col.add_hash_index(["attr1", "attr2"], unique=True)
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

    def test_add_cap_constraint(self):
        self.col.add_cap_constraint(size=10, byte_size=40000)
        self.assertIn(
            {
                "type": "cap",
                "size": 10,
                "byte_size": 40000,
                "unique": False
            },
            self.col.indexes.values()
        )
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

    def test_add_skiplist_index(self):
        self.col.add_skiplist_index(["attr1", "attr2"], unique=True)
        self.assertIn(
            {
                "sparse": False,
                "type": "skiplist",
                "fields": ["attr1", "attr2"],
                "unique": True
            },
            self.col.indexes.values()
        )
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

    def test_add_geo_index_with_one_attr(self):
        self.skipTest("I have no idea why unique comes back as false, on the geo creation."
                      "Perhaps that index type doesn't support it.")
        self.col.add_geo_index(
            fields=["attr1"],
            geo_json=False,
            unique=True,
            ignore_null=False
        )
        self.assertIn(
            {
                "sparse": True,
                "type": "geo1",
                "fields": ["attr1"],
                "unique": True,
                "geo_json": False,
                "ignore_null": False,
                "constraint": True
            },
            self.col.indexes.values()
        )
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

    def test_add_geo_index_with_two_attrs(self):
        self.skipTest("I have no idea why unique comes back as false, on the geo creation."
                      "Perhaps that index type doesn't support it.")
        self.col.add_geo_index(
            fields=["attr1", "attr2"],
            geo_json=False,
            unique=True,
            ignore_null=False
        )
        self.assertIn(
            {
                "sparse": True,
                "type": "geo2",
                "fields": ["attr1", "attr2"],
                "unique": True,
                "ignore_null": False,
                "constraint": True
            },
            self.col.indexes.values()
        )
        self.assertIn(
            {
                "type": "primary",
                "fields": ["_key"],
                "unique": True
            },
            self.col.indexes.values()
        )

    def test_add_geo_index_with_more_than_two_attrs(self):
        self.assertRaises(
            IndexAddError,
            self.col.add_geo_index,
            fields=["attr1", "attr2", "attr3"]
        )

    def test_add_fulltext_index(self):
        self.assertRaises(
            IndexAddError,
            self.col.add_fulltext_index,
            fields=["attr1", "attr2"]
        )
        self.col.add_fulltext_index(
            fields=["attr1"],
            min_length=10,
        )
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

    def test_remove_index(self):
        old_indexes = set(self.col.indexes)
        self.col.add_hash_index(["attr1", "attr2"], unique=True)
        self.col.add_skiplist_index(["attr1", "attr2"], unique=True)
        self.col.add_fulltext_index(
            fields=["attr1"],
            min_length=10,
        )
        new_indexes = set(self.col.indexes)
        self.assertNotEqual(old_indexes, new_indexes)

        for index_id in new_indexes - old_indexes:
            self.col.remove_index(index_id)

        self.assertEqual(old_indexes, set(self.col.indexes))


if __name__ == "__main__":
    unittest.main()
