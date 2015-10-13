"""Tests for ArangoDB transactions."""

import unittest
from arango import Arango
from arango.tests.utils import (
    generate_db_name,
    generate_col_name,
)


class BatchRequestTest(unittest.TestCase):
    """Tests for ArangoDB transactions."""

    def setUp(self):
        self.arango = Arango()
        self.db_name = generate_db_name(self.arango)
        self.db = self.arango.create_database(self.db_name)
        self.col_name01 = generate_col_name(self.db)
        self.col01 = self.db.create_collection(self.col_name01)
        self.col_name02 = generate_col_name(self.db)
        self.col02 = self.db.create_collection(self.col_name02)

        # Test database cleanup
        self.addCleanup(self.arango.delete_database,
                        name=self.db_name, safe_delete=True)

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

    def test_execute_transaction_with_params(self):
        action = """
            function (params) {
                var db = require('internal').db;
                db.%s.save({ _key: 'doc11', val: params.val1 });
                db.%s.save({ _key: 'doc12', val: params.val2 });
                return 'success!';
            }
        """ % (self.col_name01, self.col_name02)

        params = {"val1": 1, "val2": 2}

        res = self.db.execute_transaction(
            action=action,
            read_collections=[self.col_name01, self.col_name02],
            write_collections=[self.col_name01, self.col_name02],
            params=params,
            wait_for_sync=True,
            lock_timeout=10000
        )

        self.assertEqual(res, "success!")
        self.assertIn("doc11", self.col01)
        self.assertIn("doc12", self.col02)
        self.assertEqual(self.col01["doc11"]["val"], params["val1"])
        self.assertEqual(self.col02["doc12"]["val"], params["val2"])


if __name__ == "__main__":
    unittest.main()
