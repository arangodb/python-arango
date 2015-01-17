"""Tests for ArangoDB Transactions."""

import unittest
from arango import Arango
from arango.tests.utils import (
    get_next_db_name,
    get_next_col_name,
)


class BatchRequestTest(unittest.TestCase):

    def setUp(self):
        self.arango = Arango()
        self.db_name = get_next_db_name(self.arango)
        self.db = self.arango.add_database(self.db_name)
        self.col_name01 = get_next_col_name(self.db)
        self.col01 = self.db.add_collection(self.col_name01)
        self.col_name02 = get_next_col_name(self.db)
        self.col02 = self.db.add_collection(self.col_name02)

    def tearDown(self):
        self.arango.remove_database(self.db_name)

    def test_execute_transaction(self):
        action = """
            function () {
                var db = require('internal').db;
                db.%s.save({ _key: 'doc01'});
                db.%s.save({ _key: 'doc02'});
                return 'success!';
            }
        """ % (self.col_name01, self.col_name02)

        res = self.db.execute_transaction(
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
