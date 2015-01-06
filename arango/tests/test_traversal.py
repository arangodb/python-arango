"""Tests for ArangoDB graph traversals."""

import unittest

from arango import Arango
from arango.tests.utils import (
    get_next_graph_name,
    get_next_col_name,
    get_next_db_name
)

# TODO add more tests
class EdgeManagementTest(unittest.TestCase):

    def setUp(self):
        # Create the test database
        self.arango = Arango()
        self.db_name = get_next_db_name(self.arango)
        self.db = self.arango.add_database(self.db_name)
        # Create the test vertex "from" collection
        self.from_col_name = get_next_col_name(self.db)
        self.from_col = self.db.add_collection(self.from_col_name)
        # Create the test vertex "to" collection
        self.to_col_name = get_next_col_name(self.db)
        self.to_col = self.db.add_collection(self.to_col_name)
        # Create the test edge collection
        self.edge_col_name = get_next_col_name(self.db)
        self.edge_col = self.db.add_collection(
            self.edge_col_name, is_edge=True
        )
        # Create the test graph
        self.graph_name = get_next_graph_name(self.db)
        self.graph = self.db.add_graph(
            name=self.graph_name,
            edge_definitions=[{
                "collection": self.edge_col_name,
                "from": [self.from_col_name],
                "to": [self.to_col_name]
            }],
        )
        # Add a few test "from" vertices
        self.graph.add_vertex(
            self.from_col_name,
            key="from01",
            data={"value": 1}
        )
        self.graph.add_vertex(
            self.from_col_name,
            key="from02",
            data={"value": 2}
        )
        # Add a few test "to" vertices
        self.graph.add_vertex(
            self.to_col_name,
            key="to01",
            data={"value": 1}
        )
        self.graph.add_vertex(
            self.to_col_name,
            key="to02",
            data={"value": 2}
        )
        self.graph.add_vertex(
            self.to_col_name,
            key="to03",
            data={"value": 3}
        )

        # Add a few test edges
        self.graph.add_edge(
            self.edge_col_name,
            "{}/{}".format(self.from_col_name, "from01"),
            "{}/{}".format(self.to_col_name, "to01"),
        )
        self.graph.add_edge(
            self.edge_col_name,
            "{}/{}".format(self.from_col_name, "from02"),
            "{}/{}".format(self.to_col_name, "to02"),
        )
        self.graph.add_edge(
            self.edge_col_name,
            "{}/{}".format(self.from_col_name, "from02"),
            "{}/{}".format(self.to_col_name, "to03"),
        )

    def tearDown(self):
        self.arango.remove_database(self.db_name)

    def test_basic_traversal(self):
        visited = self.graph.execute_traversal(
            self.from_col_name + "/from01",
            direction="outbound"
        )["visited"]
        print visited
        self.assertEqual(len(visited["paths"]), 2)
        self.assertEqual(
            [vertex["_id"] for vertex in visited["vertices"]],
            [
                "{}/from01".format(self.from_col_name),
                "{}/to01".format(self.to_col_name)
            ]
        )

if __name__ == "__main__":
    unittest.main()
