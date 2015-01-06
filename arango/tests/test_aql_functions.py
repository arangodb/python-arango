"""Tests for managing ArangoDB indexes."""

import unittest

from arango import Arango
from arango.exceptions import *
from arango.tests.utils import (
    get_next_col_name,
    get_next_db_name
)

class AQLFunctionManagementTest(unittest.TestCase):


    def setUp(self):
        self.arango = Arango()
        self.db_name = get_next_db_name(self.arango)
        self.db = self.arango.add_database(self.db_name)

    def tearDown(self):
        self.arango.remove_database(self.db_name)

    def test_add_valid_aql_function(self):
        self.db.add_aql_function(
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

    def test_add_invalid_aql_function(self):
        self.assertRaises(
            ArangoAQLFunctionAddError,
            self.db.add_aql_function,
            "myfunctions::temperature::celsiustofahrenheit",
            "function (celsius) { invalid syntax }"
        )

    def test_remove_aql_function(self):
        self.db.add_aql_function(
            "myfunctions::temperature::celsiustofahrenheit",
            "function (celsius) { return celsius * 1.8 + 32; }"
        )
        self.db.remove_aql_function(
            "myfunctions::temperature::celsiustofahrenheit",
        )
        self.assertEqual(self.db.aql_functions, {})

    # TODO create functions within function
    def test_remove_aql_functions_by_group(self):
        self.db.add_aql_function(
            "myfunctions::temperature::celsiustofahrenheit",
            "function (celsius) { return celsius * 1.8 + 32; }"
        )
        self.db.remove_aql_function(
            "myfunctions::temperature::celsiustofahrenheit",
            group=True
        )
        self.assertEqual(self.db.aql_functions, {})


if __name__ == "__main__":
    unittest.main()