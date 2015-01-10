"""Tests for ArangoDB Batch Requests."""

import unittest
from arango import Arango
from arango.tests.utils import (
    get_next_db_name,
    get_next_col_name
)

class BatchRequestTest(unittest.TestCase):

    def setUp(self):
        self.arango = Arango()
        self.db_name = get_next_db_name(self.arango)
        self.db = self.arango.add_database(self.db_name)
        self.col_name = get_next_col_name(self.db)
        self.col = self.db.add_collection(self.col_name)

    def tearDown(self):
        self.arango.remove_database(self.db_name)

    def test_batch_add(self):
        res = self.db.execute_batch([
            (self.col.add_document, [{"value": 1}], {}),
            (self.col.add_document, [{"value": 2}], {}),
            (self.col.add_document, [{"value": 3}], {}),
        ])
        print res

    def test_batch_replace(self):
        res = self.db.execute_batch([

        ])
        pass

    def test_batch_update(self):
        pass

    def test_batch_remove(self):
        pass

if __name__ == "__main__":
    unittest.main()