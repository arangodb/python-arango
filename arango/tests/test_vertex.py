"""Tests for managing ArangoDB vertices."""

import unittest

from arango import Arango
from arango.tests.utils import (
    get_next_graph_name,
    get_next_col_name,
    get_next_db_name
)


class VertexManagementTest(unittest.TestCase):

    def setUp(self):
        self.arango = Arango()
        self.db_name = get_next_db_name(self.arango)
        self.db = self.arango.add_database(self.db_name)
        self.col_name = get_next_col_name(self.db)
        self.col = self.db.add_collection(self.col_name)
        # Create the vertex collection
        self.vertex_col_name = get_next_col_name(self.db)
        self.vertex_col = self.db.add_collection(self.vertex_col_name)
        # Create the edge collection
        self.edge_col_name = get_next_col_name(self.db)
        self.edge_col = self.db.add_collection(
            self.edge_col_name, is_edge=True
        )
        # Create the graph
        self.graph_name = get_next_graph_name(self.db)
        self.graph = self.db.add_graph(
            name=self.graph_name,
            edge_definitions=[{
                "collection": self.edge_col_name,
                "from": [self.vertex_col_name],
                "to": [self.vertex_col_name]
            }],
        )

    def tearDown(self):
        self.arango.remove_database(self.db_name)

    def test_add_vertex(self):
        self.graph.add_vertex(
            self.vertex_col_name,
            data={"_key": "vertex01", "value": 10}
        )
        self.assertEqual(self.vertex_col.count, 1)
        self.assertEqual(
            self.graph.get_vertex(
                "{}/{}".format(self.vertex_col_name, "vertex01")
            )["value"],
            10
        )

    def test_update_vertex(self):
        self.graph.add_vertex(
            self.vertex_col_name,
            data={"_key": "vertex01", "value": 10}
        )
        self.graph.update_vertex(
            "{}/{}".format(self.vertex_col_name, "vertex01"),
            data={"value": 20, "new_value": 30}
        )
        self.assertEqual(
            self.graph.get_vertex(
                "{}/{}".format(self.vertex_col_name, "vertex01")
            )["value"],
            20
        )
        self.assertEqual(
            self.graph.get_vertex(
                "{}/{}".format(self.vertex_col_name, "vertex01")
            )["new_value"],
            30
        )

    def test_replace_vertex(self):
        self.graph.add_vertex(
            self.vertex_col_name,
            data={"_key": "vertex01", "value": 10}
        )
        self.graph.replace_vertex(
            "{}/{}".format(self.vertex_col_name, "vertex01"),
            data={"new_value": 30}
        )
        self.assertNotIn(
            "value",
            self.graph.get_vertex(
                "{}/{}".format(self.vertex_col_name, "vertex01")
            )
        )
        self.assertEqual(
            self.graph.get_vertex(
                "{}/{}".format(self.vertex_col_name, "vertex01")
            )["new_value"],
            30
        )

    def test_remove_vertex(self):
        self.graph.add_vertex(
            self.vertex_col_name,
            data={"_key": "vertex01", "value": 10}
        )
        self.graph.remove_vertex(
            "{}/{}".format(self.vertex_col_name, "vertex01")
        )
        self.assertNotIn("vertex01", self.vertex_col)
        self.assertEqual(len(self.vertex_col), 0)


if __name__ == "__main__":
    unittest.main()
