"""Tests for managing ArangoDB edges."""

import unittest

from arango import Arango
from arango.tests.utils import (
    generate_graph_name,
    generate_col_name,
    generate_db_name
)


class EdgeManagementTest(unittest.TestCase):
    """Tests for managing ArangoDB edges."""

    def setUp(self):
        # Create the test database
        self.arango = Arango()
        self.db_name = generate_db_name(self.arango)
        self.db = self.arango.create_database(self.db_name)
        # Create the test vertex collection
        self.vertex_col_name = generate_col_name(self.db)
        self.vertex_col = self.db.create_collection(self.vertex_col_name)
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
                "from": [self.vertex_col_name],
                "to": [self.vertex_col_name]
            }],
        )
        # Create a few test vertices
        self.graph.create_vertex(
            self.vertex_col_name,
            data={
                "_key": "vertex01",
                "value": 1
            }
        )
        self.graph.create_vertex(
            self.vertex_col_name,
            data={
                "_key": "vertex02",
                "value": 1
            }
        )
        self.graph.create_vertex(
            self.vertex_col_name,
            data={
                "_key": "vertex03",
                "value": 1
            }
        )

        # Test database cleanup
        self.addCleanup(self.arango.delete_database,
                        name=self.db_name, safe_delete=True)

    def test_create_edge(self):
        self.graph.create_edge(
            self.edge_col_name,
            data={
                "_key": "edge01",
                "_from": "{}/{}".format(self.vertex_col_name, "vertex01"),
                "_to": "{}/{}".format(self.vertex_col_name, "vertex01"),
                "value": "foobar"
            }
        )
        self.assertEqual(len(self.edge_col), 1)
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
        self.graph.create_edge(
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
        self.graph.create_edge(
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

    def test_delete_edge(self):
        self.graph.create_edge(
            self.edge_col_name,
            data={
                "_key": "edge01",
                "_from": "{}/{}".format(self.vertex_col_name, "vertex01"),
                "_to": "{}/{}".format(self.vertex_col_name, "vertex01"),
                "value": 10
            }
        )
        self.graph.delete_edge("{}/{}".format(self.edge_col_name, "edge01"))
        self.assertNotIn("edge01", self.edge_col)
        self.assertEqual(len(self.edge_col), 0)


if __name__ == "__main__":
    unittest.main()
