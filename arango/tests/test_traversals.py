"""Tests for ArangoDB graph traversals."""

import unittest

from arango import Arango
from arango.tests.utils import (
    generate_graph_name,
    generate_col_name,
    generate_db_name
)


# TODO add more tests
class EdgeManagementTest(unittest.TestCase):
    """Tests for ArangoDB graph traversals."""

    def setUp(self):
        # Create the test database
        self.arango = Arango()
        self.db_name = generate_db_name(self.arango)
        self.db = self.arango.create_database(self.db_name)
        # Create the test vertex "from" collection
        self.from_col_name = generate_col_name(self.db)
        self.from_col = self.db.create_collection(self.from_col_name)
        # Create the test vertex "to" collection
        self.to_col_name = generate_col_name(self.db)
        self.to_col = self.db.create_collection(self.to_col_name)
        # Create the test edge collection
        self.edge_col_name = generate_col_name(self.db)
        self.edge_col = self.db.create_collection(
            self.edge_col_name, is_edge=True
        )
        # Create the test graph
        self.graph_name = generate_graph_name(self.db)
        self.graph = self.db.create_graph(
            name=self.graph_name,
            edge_definitions=[{
                "collection": self.edge_col_name,
                "from": [self.from_col_name],
                "to": [self.to_col_name]
            }],
        )
        # Create a few test "from" vertices
        self.graph.create_vertex(
            self.from_col_name,
            data={"_key": "from01", "value": 1}
        )
        self.graph.create_vertex(
            self.from_col_name,
            data={"_key": "from02", "value": 2}
        )
        # Create a few test "to" vertices
        self.graph.create_vertex(
            self.to_col_name,
            data={"_key": "to01", "value": 1}
        )
        self.graph.create_vertex(
            self.to_col_name,
            data={"_key": "to02", "value": 2}
        )
        self.graph.create_vertex(
            self.to_col_name,
            data={"_key": "to03", "value": 3}
        )

        # Create a few test edges
        self.graph.create_edge(
            self.edge_col_name,
            {
                "_from": "{}/{}".format(self.from_col_name, "from01"),
                "_to": "{}/{}".format(self.to_col_name, "to01"),
            }
        )
        self.graph.create_edge(
            self.edge_col_name,
            {
                "_from": "{}/{}".format(self.from_col_name, "from02"),
                "_to": "{}/{}".format(self.to_col_name, "to02"),
            }
        )
        self.graph.create_edge(
            self.edge_col_name,
            {
                "_from": "{}/{}".format(self.from_col_name, "from02"),
                "_to": "{}/{}".format(self.to_col_name, "to03"),
            }

        )
        # Test database cleanup
        self.addCleanup(self.arango.delete_database,
                        name=self.db_name, safe_delete=True)

    def test_basic_traversal(self):
        visited = self.graph.execute_traversal(
            "{}/{}".format(self.from_col_name, "from01"),
            direction="outbound"
        )["visited"]
        self.assertEqual(len(visited["paths"]), 2)
        self.assertEqual(
            [vertex["_id"] for vertex in visited["vertices"]],
            [
                "{}/{}".format(self.from_col_name, "from01"),
                "{}/{}".format(self.to_col_name, "to01"),
            ]
        )

if __name__ == "__main__":
    unittest.main()
