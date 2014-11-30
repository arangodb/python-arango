"""Tests for managing ArangoDB edges."""

import unittest

from arango import Arango
from arango.tests.utils import (
    get_next_graph_name,
    get_next_col_name,
    get_next_db_name
)


class EdgeManagementTest(unittest.TestCase):

    def setUp(self):
        # Create the test database
        self.arango = Arango()
        self.db_name = get_next_db_name(self.arango)
        self.db = self.arango.add_database(self.db_name)
        # Create the test vertex collection
        self.vertex_col_name = get_next_col_name(self.db)
        self.vertex_col = self.db.add_collection(self.vertex_col_name)
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
                "from": [self.vertex_col_name],
                "to": [self.vertex_col_name]
            }],
        )
        # Add a few test vertices
        self.graph.add_vertex(
            self.vertex_col_name,
            data={
                "_key": "vertex01",
                "value": 1
            }
        )
        self.graph.add_vertex(
            self.vertex_col_name,
            data={
                "_key": "vertex02",
                "value": 1
            }
        )
        self.graph.add_vertex(
            self.vertex_col_name,
            data={
                "_key": "vertex03",
                "value": 1
            }
        )

    def tearDown(self):
        self.arango.remove_database(self.db_name)

    def test_add_edge(self):
        self.graph.add_edge(
            self.edge_col_name,
            data={
                "_key": "edge01",
                "_from": "{}/{}".format(self.vertex_col_name, "vertex01"),
                "_to": "{}/{}".format(self.vertex_col_name, "vertex01"),
                "value": "foobar"
            }
        )
        self.assertEqual(self.edge_col.count, 1)
        self.assertEqual(
            self.graph.get_edge(
                "{}/{}".format(self.edge_col_name, "edge01")
            )["value"],
            "foobar"
        )
        self.assertEqual(
            self.graph.get_edge(
                "{}/{}".format(self.edge_col_name, "edge01")
            )["_from"],
            "{}/{}".format(self.vertex_col_name, "vertex01")
        )
        self.assertEqual(
            self.graph.get_edge(
                "{}/{}".format(self.edge_col_name, "edge01")
            )["_to"],
            "{}/{}".format(self.vertex_col_name, "vertex01")
        )

    def test_update_edge(self):
        self.graph.add_edge(
            self.edge_col_name,
            data={
                "_key": "edge01",
                "_from": "{}/{}".format(self.vertex_col_name, "vertex01"),
                "_to": "{}/{}".format(self.vertex_col_name, "vertex01"),
                "value": 10
            }
        )
        self.graph.update_edge(
            "{}/{}".format(self.edge_col_name, "edge01"),
            data={"value": 20, "new_value": 30}
        )
        self.assertEqual(
            self.graph.get_edge(
                "{}/{}".format(self.edge_col_name, "edge01"),
            )["value"],
            20
        )
        self.assertEqual(
            self.graph.get_edge(
                "{}/{}".format(self.edge_col_name, "edge01"),
            )["new_value"],
            30
        )

    def test_replace_edge(self):
        self.graph.add_edge(
            self.edge_col_name,
            data={
                "_key": "edge01",
                "_from": "{}/{}".format(self.vertex_col_name, "vertex01"),
                "_to": "{}/{}".format(self.vertex_col_name, "vertex01"),
                "value": 10
            }
        )
        self.graph.replace_edge(
            "{}/{}".format(self.edge_col_name, "edge01"),
            data={"new_value": 20}
        )
        self.assertNotIn(
            "value",
            self.graph.get_edge(
                "{}/{}".format(self.edge_col_name, "edge01")
            )
        )
        self.assertEqual(
            self.graph.get_edge(
                "{}/{}".format(self.edge_col_name, "edge01")
            )["new_value"],
            20
        )

    def test_remove_edge(self):
        self.graph.add_edge(
            self.edge_col_name,
            data={
                "_key": "edge01",
                "_from": "{}/{}".format(self.vertex_col_name, "vertex01"),
                "_to": "{}/{}".format(self.vertex_col_name, "vertex01"),
                "value": 10
            }
        )
        self.graph.remove_edge("{}/{}".format(self.edge_col_name, "edge01"))
        self.assertNotIn("edge01", self.edge_col)
        self.assertEqual(len(self.edge_col), 0)


if __name__ == "__main__":
    unittest.main()
