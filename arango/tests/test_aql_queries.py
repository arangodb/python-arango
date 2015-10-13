"""Tests for ArangoDB AQL queries."""

import unittest

from arango import Arango
from arango.exceptions import (
    AQLQueryValidateError,
)
from arango.tests.utils import (
    generate_col_name,
    generate_db_name
)


class ArangoDBQueryTest(unittest.TestCase):
    """Tests for ArangoDB AQL queries."""

    def setUp(self):
        self.arango = Arango()
        self.db_name = generate_db_name(self.arango)
        self.db = self.arango.create_database(self.db_name)
        self.col_name = generate_col_name(self.db)
        self.db.create_collection(self.col_name)

        # Test database cleanup
        self.addCleanup(self.arango.delete_database,
                        name=self.db_name, safe_delete=True)

    def test_explain_query(self):
        self.assertRaises(
            AQLQueryValidateError,
            self.db.validate_query,
            "THIS IS AN INVALID QUERY"
        )
        plans = self.db.explain_query(
            "FOR d IN {} RETURN d".format(self.col_name),
            all_plans=True,
            optimizer_rules=["-all", "+use-index-range"]
        )
        for plan in plans:
            self.assertGreaterEqual(
                set(plan),
                {
                    "collections",
                    "estimated_cost",
                    "estimated_nr_items",
                    "nodes",
                    "rules",
                    "variables"
                }
            )

    def test_validate_query(self):
        self.assertRaises(
            AQLQueryValidateError,
            self.db.validate_query,
            "THIS IS AN INVALID QUERY"
        )
        self.assertEqual(
            None,
            self.db.validate_query(
                "FOR d IN {} RETURN d".format(self.col_name)
            ),
        )

    def test_execute_query(self):
        collection = self.db.collection(self.col_name)
        collection.import_documents([
            {"_key": "doc01"},
            {"_key": "doc02"},
            {"_key": "doc03"},
        ])
        res = self.db.execute_query(
            "FOR d IN {} RETURN d".format(self.col_name),
            count=True,
            batch_size=1,
            ttl=10,
            optimizer_rules=["+all"]
        )
        self.assertEqual(
            sorted([doc["_key"] for doc in list(res)]),
            ["doc01", "doc02", "doc03"]
        )

    def test_execute_query_2(self):
        collection = self.db.collection(self.col_name)
        collection.import_documents([
            {"_key": "doc01", "value": 1},
            {"_key": "doc02", "value": 2},
            {"_key": "doc03", "value": 3},
        ])
        res = self.db.execute_query(
            "FOR d IN {} FILTER d.value == @value RETURN d".format(
                self.col_name
            ),
            bind_vars={
                "value": 1
            }
        )
        self.assertEqual(
            sorted([doc["_key"] for doc in list(res)]),
            ["doc01"]
        )


if __name__ == "__main__":
    unittest.main()
