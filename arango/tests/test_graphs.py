"""Tests for managing ArangoDB graphs."""

import unittest

from arango import Arango
from arango.tests.utils import (
    generate_graph_name,
    generate_col_name,
    generate_db_name
)


class GraphManagementTest(unittest.TestCase):
    """Tests for managing ArangoDB graphs."""

    def setUp(self):
        self.arango = Arango()
        self.db_name = generate_db_name(self.arango)
        self.db = self.arango.create_database(self.db_name)

        # Test database cleanup
        self.addCleanup(self.arango.delete_database,
                        name=self.db_name, safe_delete=True)

    def test_create_graph(self):
        graph_name = generate_graph_name(self.db)
        self.db.create_graph(graph_name)
        self.assertIn(graph_name, self.db.list_graphs())

    def test_delete_graph(self):
        # Create a new collection
        graph_name = generate_graph_name(self.db)
        self.db.create_graph(graph_name)
        self.assertIn(graph_name, self.db.list_graphs())
        # Delete the collection and ensure that it's gone
        self.db.delete_graph(graph_name)
        self.assertNotIn(graph_name, self.db.list_graphs())

    def test_create_graph_with_defined_cols(self):
        # Create the orphan collection
        orphan_col_name = generate_col_name(self.db)
        self.db.create_collection(orphan_col_name)
        # Create the vertex collection
        vertex_col_name = generate_col_name(self.db)
        self.db.create_collection(vertex_col_name)
        # Create the edge collection
        edge_col_name = generate_col_name(self.db)
        self.db.create_collection(edge_col_name, is_edge=True)
        # Create the graph
        graph_name = generate_graph_name(self.db)
        graph = self.db.create_graph(
            name=graph_name,
            edge_definitions=[{
                "collection": edge_col_name,
                "from": [vertex_col_name],
                "to": [vertex_col_name]
            }],
            orphan_collections=[orphan_col_name]
        )
        self.assertIn(graph_name, self.db.list_graphs())
        self.assertEqual(
            graph.orphan_collections,
            [orphan_col_name]
        )
        self.assertEqual(
            graph.edge_definitions,
            [{
                "collection": edge_col_name,
                "from": [vertex_col_name],
                "to": [vertex_col_name]
            }]
        )
        self.assertEqual(
            sorted(graph.vertex_collections),
            sorted([orphan_col_name, vertex_col_name])
        )
        properties = graph.properties
        del properties["_rev"]
        del properties["_id"]
        self.assertEqual(
            properties,
            {
                "name": graph_name,
                "edge_definitions": [
                    {
                        "collection": edge_col_name,
                        "from": [vertex_col_name],
                        "to": [vertex_col_name]
                    }
                ],
                "orphan_collections": [orphan_col_name]
            }
        )

    def test_create_and_delete_vertex_collection(self):
        # Create the vertex collection
        vertex_col_name = generate_col_name(self.db)
        self.db.create_collection(vertex_col_name)
        # Create the graph
        graph_name = generate_graph_name(self.db)
        graph = self.db.create_graph(graph_name)
        self.assertIn(graph_name, self.db.list_graphs())
        self.assertEqual(graph.vertex_collections, [])
        # Create the vertex collection to the graph
        graph.create_vertex_collection(vertex_col_name)
        self.assertEqual(
            graph.vertex_collections,
            [vertex_col_name]
        )
        # Delete the vertex collection (completely)
        graph.delete_vertex_collection(
            vertex_col_name,
            drop_collection=True
        )
        self.assertEqual(graph.vertex_collections, [])
        self.assertNotIn(vertex_col_name, self.db.list_collections["all"])

    def test_create_and_delete_edge_definition(self):
        # Create the edge and vertex collections
        vertex_col_name = generate_col_name(self.db)
        self.db.create_collection(vertex_col_name)
        edge_col_name = generate_col_name(self.db)
        self.db.create_collection(edge_col_name, is_edge=True)
        # Create the graph
        graph_name = generate_graph_name(self.db)
        graph = self.db.create_graph(graph_name)
        # Create the edge definition to the graph
        edge_definition = {
            "collection": edge_col_name,
            "from": [vertex_col_name],
            "to": [vertex_col_name]
        }
        graph.create_edge_definition(
            edge_col_name,
            [vertex_col_name],
            [vertex_col_name]
        )
        self.assertEqual(
            graph.edge_definitions,
            [edge_definition]
        )
        graph.delete_edge_definition(
            edge_col_name,
            drop_collection=True
        )
        self.assertEqual(graph.edge_definitions, [])
        self.assertNotIn(edge_col_name, self.db.list_collections["all"])

    def test_replace_edge_definition(self):
        # Create edge and vertex collection set 1
        vertex_col_name = generate_col_name(self.db)
        self.db.create_collection(vertex_col_name)
        edge_col_name = generate_col_name(self.db)
        self.db.create_collection(edge_col_name, is_edge=True)

        # Create edge and vertex collection set 2
        vertex_col_name_2 = generate_col_name(self.db)
        self.db.create_collection(vertex_col_name_2)
        edge_col_name_2 = generate_col_name(self.db)
        self.db.create_collection(edge_col_name_2, is_edge=True)

        # Create the graph
        graph_name = generate_graph_name(self.db)
        graph = self.db.create_graph(graph_name)

        # Create the edge definition to the graph
        edge_definition = {
            "collection": edge_col_name,
            "from": [vertex_col_name],
            "to": [vertex_col_name]
        }
        graph.create_edge_definition(
            edge_col_name,
            [vertex_col_name],
            [vertex_col_name]
        )
        self.assertEqual(
            graph.edge_definitions,
            [edge_definition]
        )

        # Replace the edge definition 1 with 2
        edge_definition_2 = {
            "collection": edge_col_name,
            "from": [vertex_col_name_2],
            "to": [vertex_col_name_2]
        }
        graph.replace_edge_definition(
            edge_col_name,
            [vertex_col_name_2],
            [vertex_col_name_2]
        )
        self.assertEqual(
            graph.edge_definitions,
            [edge_definition_2]
        )


if __name__ == "__main__":
    unittest.main()
