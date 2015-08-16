"""Tests for ArangoDB AQL functions."""

import unittest

from arango import Arango
from arango.exceptions import (
    AQLFunctionCreateError,
)
from arango.tests.utils import (
    get_next_db_name
)


class AQLFunctionManagementTest(unittest.TestCase):
    """Tests for ArangoDB AQL functions."""

    def setUp(self):
        self.arango = Arango()
        self.db_name = get_next_db_name(self.arango)
        self.db = self.arango.create_database(self.db_name)

        # Test database cleaup
        self.addCleanup(self.arango.delete_database,
                        name=self.db_name, safe_delete=True)

    def test_create_valid_aql_function(self):
        self.db.create_aql_function(
            "myfunctions::temperature::celsiustofahrenheit",
            "function (celsius) { return celsius * 1.8 + 32; }"
        )
        self.assertEqual(
            self.db.aql_functions,
            {
                "myfunctions::temperature::celsiustofahrenheit": (
                    "function (celsius) { return celsius * 1.8 + 32; }"
                )
            }
        )

    def test_create_invalid_aql_function(self):
        self.assertRaises(
            AQLFunctionCreateError,
            self.db.create_aql_function,
            "myfunctions::temperature::celsiustofahrenheit",
            "function (celsius) { invalid syntax }"
        )

    def test_delete_aql_function(self):
        self.db.create_aql_function(
            "myfunctions::temperature::celsiustofahrenheit",
            "function (celsius) { return celsius * 1.8 + 32; }"
        )
        self.db.delete_aql_function(
            "myfunctions::temperature::celsiustofahrenheit",
        )
        self.assertEqual(self.db.aql_functions, {})

    # TODO create functions within function
    def test_delete_aql_functions_by_group(self):
        self.db.create_aql_function(
            "myfunctions::temperature::celsiustofahrenheit",
            "function (celsius) { return celsius * 1.8 + 32; }"
        )
        self.db.delete_aql_function(
            "myfunctions::temperature::celsiustofahrenheit",
            group=True
        )
        self.assertEqual(self.db.aql_functions, {})


if __name__ == "__main__":
    unittest.main()
