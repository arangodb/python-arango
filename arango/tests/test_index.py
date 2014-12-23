"""Tests for managing ArangoDB indexes."""

import unittest

from arango import Arango
from arango.exceptions import *
from arango.tests.test_utils import (
    get_next_col_name,
    get_next_db_name
)


class IndexManagementTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.arango = Arango()
        cls.db_name = get_next_db_name(cls.arango)
        cls.db = cls.arango.add_database(cls.db_name)

    @classmethod
    def tearDownClass(cls):
        cls.arango.remove_database(cls.db_name)

    def setUp(self):
        self.col_name = get_next_col_name(self.arango)
        self.col = self.arango.add_collection(self.col_name)

    def tearDown(self):
        self.arango.remove_collection(self.col_name)

    def test_list_indexes(self):
        self.assertEquals(
            sorted(self.col.indexes.values()),
            sorted([
                {
                    "fields": ["_key"],
                    "type": "primary",
                    "unique": True
                }
            ])
        )

    def test_add_hash_index(self):
        self.col.add_hash_index(["attr1", "attr2"], unique=True)
        self.assertEquals(
            sorted(self.col.indexes.values()),
            sorted([
                {
                    "type": "primary",
                    "fields": ["_key"],
                    "unique": True
                },
                {
                    "type": "hash",
                    "fields": ["attr1", "attr2"],
                    "unique": True
                }
            ])
        )

    def test_add_cap_constraint(self):
        self.col.add_cap_constraint(size=10, byte_size=40000)
        self.assertEquals(
            sorted(self.col.indexes.values()),
            sorted([
                {
                    "type": "primary",
                    "fields": ["_key"],
                    "unique": True
                },
                {
                    "type": "cap",
                    "size": 10,
                    "byte_size": 40000,
                    "unique": False
                }
            ])
        )

    def test_add_skiplist_index(self):
        self.col.add_skiplist_index(["attr1", "attr2"], unique=True)
        self.assertEquals(
            sorted(self.col.indexes.values()),
            sorted([
                {
                    "type": "primary",
                    "fields": ["_key"],
                    "unique": True
                },
                {
                    "type": "skiplist",
                    "fields": ["attr1", "attr2"],
                    "unique": True
                }
            ])
        )

    def test_add_geo_index_with_one_attr(self):
        self.col.add_geo_index(
            fields=["attr1"],
            geo_json=False,
            unique=True,
            ignore_null=False
        )
        self.assertEquals(
             sorted(self.col.indexes.values()),
             sorted([
                {
                    "type": "primary",
                    "fields": ["_key"],
                    "unique": True
                },
                {
                    "type": "geo1",
                    "fields": ["attr1"],
                    "unique": True,
                    "geo_json": False,
                    "ignore_null": False,
                    "constraint": True
                }
            ])
        )

    def test_add_geo_index_with_two_attrs(self):
        self.col.add_geo_index(
            fields=["attr1", "attr2"],
            geo_json=False,
            unique=True,
            ignore_null=False
        )
        self.assertEquals(
             sorted(self.col.indexes.values()),
             sorted([
                {
                    "type": "primary",
                    "fields": ["_key"],
                    "unique": True
                },
                {
                    "type": "geo2",
                    "fields": ["attr1", "attr2"],
                    "unique": True,
                    "ignore_null": False,
                    "constraint": True
                }
            ])
        )

    def test_add_geo_index_with_more_than_two_attrs(self):
        self.assertRaises(
            ArangoIndexAddError,
            self.col.add_geo_index,
            fields=["attr1", "attr2", "attr3"]
        )

    def test_add_fulltext_index(self):
        self.assertRaises(
            ArangoIndexAddError,
            self.col.add_fulltext_index,
            fields=["attr1", "attr2"]
        )
        self.col.add_fulltext_index(
            fields=["attr1"],
            min_length=10,
        )
        self.assertEquals(
             sorted(self.col.indexes.values()),
             sorted([
                {
                    "type": "primary",
                    "fields": ["_key"],
                    "unique": True
                },
                {
                    "type": "fulltext",
                    "fields": ["attr1"],
                    "min_length": 10,
                    "unique": False,
                }
            ])
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
