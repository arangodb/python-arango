"""Tests for ArangoDB Transactions."""

import unittest
from arango import Arango
from arango.tests.utils import (
    get_next_db_name,
    get_next_col_name,
    get_next_graph_name,
)

class BatchRequestTest(unittest.TestCase):

    def setUp(self):
        self.arango = Arango()
        self.col_name01 = get_next_col_name(self.arango)
        self.col01 = self.arango.add_collection(self.col_name01)
        self.col_name02 = get_next_col_name(self.arango)
        self.col02 = self.arango.add_collection(self.col_name02)

    def tearDown(self):
        self.arango.remove_collection(self.col_name01)
        self.arango.remove_collection(self.col_name02)

    def test_execute_transaction(self):
        action = """
            function () {
                var db = require('internal').db;
                db.%s.save({ _key: 'doc01'});
                db.%s.save({ _key: 'doc02'});
                return 'success!';
            }
        """ % (self.col_name01, self.col_name02)

        res = self.arango.execute_transaction(
            action=action,
            read_collections=[self.col_name01, self.col_name02],
            write_collections=[self.col_name01, self.col_name02],
            wait_for_sync=True,
            lock_timeout=10000
        )
        self.assertEqual(res, "success!")
        self.assertIn("doc01", self.col01)
        self.assertIn("doc02", self.col02)


if __name__ == "__main__":
    unittest.main()
