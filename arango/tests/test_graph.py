"""Tests for managing ArangoDB collections."""

import unittest

from arango import Arango
from arango.exceptions import *
from arango.tests.test_utils import (
    get_next_graph_name,
    get_next_col_name,
    get_next_db_name
)

class GraphManagementTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.arango = Arango()
        cls.db_name = get_next_db_name(cls.arango)
        cls.db = cls.arango.add_database(cls.db_name)

    @classmethod
    def tearDownClass(cls):
        cls.arango.remove_database(cls.db_name)

    def test_add_graph(self):
        graph_name = get_next_graph_name(self.db)
        self.db.add_graph(graph_name)
        self.assertIn(graph_name, self.db.graphs)

    def test_remove_graph(self):
        # Add a new collection
        graph_name = get_next_graph_name(self.db)
        self.db.add_graph(graph_name)
        self.assertIn(graph_name, self.db.graphs)
        # Remove the collection and ensure that it's gone
        self.db.remove_graph(graph_name)
        self.assertNotIn(graph_name, self.db.graphs)

    def test_add_graph_with_defined_cols(self):
        # Create the orphan collection
        orphan_col_name = get_next_col_name(self.db)
        self.db.add_collection(orphan_col_name)
        # Create the vertex collection
        vertex_col_name = get_next_col_name(self.db)
        self.db.add_collection(vertex_col_name)
        # Create the edge collection
        edge_col_name = get_next_col_name(self.db)
        self.db.add_collection(edge_col_name, is_edge=True)
        # Create the graph
        graph_name = get_next_graph_name(self.db)
        graph = self.db.add_graph(
            name=graph_name,
            edge_definitions=[{
                "collection" : edge_col_name,
                "from" : [vertex_col_name],
                "to": [vertex_col_name]
            }],
            orphan_collections=[orphan_col_name]
        )
        self.assertIn(graph_name, self.db.graphs)
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

    def test_add_and_remove_vertex_collection(self):
        # Create the vertex collection
        vertex_col_name = get_next_col_name(self.db)
        self.db.add_collection(vertex_col_name)
        # Create the graph
        graph_name = get_next_graph_name(self.db)
        graph = self.db.add_graph(graph_name)
        self.assertIn(graph_name, self.db.graphs)
        self.assertEqual(graph.vertex_collections, [])
        # Add the vertex collection to the graph
        graph.add_vertex_collection(vertex_col_name)
        self.assertEqual(
            graph.vertex_collections,
            [vertex_col_name]
        )
        # Remove the vertex collection (completely)
        graph.remove_vertex_collection(
            col_name=vertex_col_name,
            drop_collection=True
        )
        self.assertEqual(graph.vertex_collections,[])
        self.assertNotIn(vertex_col_name, self.db.collections["all"])

    def test_add_and_remove_edge_definition(self):
        # Create the edge and vertex collections
        vertex_col_name = get_next_col_name(self.db)
        self.db.add_collection(vertex_col_name)
        edge_col_name = get_next_col_name(self.db)
        self.db.add_collection(edge_col_name, is_edge=True)
        # Create the graph
        graph_name = get_next_graph_name(self.db)
        graph = self.db.add_graph(graph_name)
        # Add the edge definition to the graph
        edge_definition = {
            "collection" : edge_col_name,
            "from" : [vertex_col_name],
            "to": [vertex_col_name]
        }
        graph.add_edge_definition(edge_definition)
        self.assertEqual(
            graph.edge_definitions,
            [edge_definition]
        )
        graph.remove_edge_definition(
            edge_col_name,
            drop_collection=True
        )
        self.assertEqual(graph.edge_definitions, [])
        self.assertNotIn(edge_col_name, self.db.collections["all"])

    def test_replace_edge_definition(self):
        # Create edge and vertex collection set 1
        vertex_col_name = get_next_col_name(self.db)
        self.db.add_collection(vertex_col_name)
        edge_col_name = get_next_col_name(self.db)
        self.db.add_collection(edge_col_name, is_edge=True)

        # Create edge and vertex collection set 2
        vertex_col_name_2 = get_next_col_name(self.db)
        self.db.add_collection(vertex_col_name_2)
        edge_col_name_2 = get_next_col_name(self.db)
        self.db.add_collection(edge_col_name_2, is_edge=True)

        # Create the graph
        graph_name = get_next_graph_name(self.db)
        graph = self.db.add_graph(graph_name)

        # Add the edge definition to the graph
        edge_definition = {
            "collection" : edge_col_name,
            "from" : [vertex_col_name],
            "to": [vertex_col_name]
        }
        graph.add_edge_definition(edge_definition)
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
            edge_definition_2
        )
        self.assertEqual(
            graph.edge_definitions,
            [edge_definition_2]
        )


if __name__ == "__main__":
    unittest.main()
