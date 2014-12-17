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
            [
                {
                    "fields": ["_key"],
                    "type": "primary",
                    "unique": True
                }
            ]
        )

    def test_add_hash_index(self):
        self.col.add_hash_index(["attr1", "attr2"], unique=True)
        self.assertEquals(
            self.col.indexes.values(),
            [
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
            ]
        )

    def test_add_cap_constraint(self):
        self.col.add_cap_constraint(size=10, byte_size=40000)
        self.assertEquals(
            self.col.indexes.values(),
            [
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
            ]
        )

    def test_skiplist_index(self):
        self.col.add_skiplist_index(["attr1", "attr2"], unique=True)
        self.assertEquals(
            self.col.indexes.values(),
            [
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
            ]
        )

if __name__ == "__main__":
    unittest.main()