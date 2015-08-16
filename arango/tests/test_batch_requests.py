"""Tests for ArangoDB batch requests."""

import unittest
from arango import Arango
from arango.tests.utils import (
    get_next_db_name,
    get_next_col_name,
    get_next_graph_name,
)


class BatchRequestTest(unittest.TestCase):
    """Tests for ArangoDB batch requests."""

    def setUp(self):
        self.arango = Arango()
        self.db_name = get_next_db_name(self.arango)
        self.db = self.arango.create_database(self.db_name)
        self.col_name = get_next_col_name(self.db)
        self.col = self.db.create_collection(self.col_name)

        # Create the vertex collection
        self.vertex_col_name = get_next_col_name(self.db)
        self.vertex_col = self.db.create_collection(self.vertex_col_name)
        # Create the edge collection
        self.edge_col_name = get_next_col_name(self.db)
        self.edge_col = self.db.create_collection(
            self.edge_col_name, is_edge=True
        )
        # Create the graph
        self.graph_name = get_next_graph_name(self.db)
        self.graph = self.db.create_graph(
            name=self.graph_name,
            edge_definitions=[{
                "collection": self.edge_col_name,
                "from": [self.vertex_col_name],
                "to": [self.vertex_col_name]
            }],
        )

        # Test database cleaup
        self.addCleanup(self.arango.delete_database,
                        name=self.db_name, safe_delete=True)

    def test_batch_document_create(self):
        self.db.execute_batch([
            (self.col.create_document, [{"_key": "doc01", "value": 1}], {}),
            (self.col.create_document, [{"_key": "doc02", "value": 2}], {}),
            (self.col.create_document, [{"_key": "doc03", "value": 3}], {}),
        ])
        self.assertEqual(len(self.col), 3)
        self.assertEqual(self.col.document("doc01")["value"], 1)
        self.assertEqual(self.col.document("doc02")["value"], 2)
        self.assertEqual(self.col.document("doc03")["value"], 3)

    def test_batch_document_replace(self):
        self.col.bulk_import([
            {"_key": "doc01", "value": 1},
            {"_key": "doc02", "value": 1},
            {"_key": "doc03", "value": 1}
        ])
        self.db.execute_batch([
            (self.col.replace_document, ["doc01", {"value": 2}], {}),
            (self.col.replace_document, ["doc02", {"value": 2}], {}),
            (self.col.replace_document, ["doc03", {"value": 2}], {}),
        ])
        self.assertEqual(self.col.document("doc01")["value"], 2)
        self.assertEqual(self.col.document("doc02")["value"], 2)
        self.assertEqual(self.col.document("doc03")["value"], 2)

    def test_batch_document_update(self):
        self.col.bulk_import([
            {"_key": "doc01", "value": 1},
            {"_key": "doc02", "value": 1},
            {"_key": "doc03", "value": 1}
        ])
        self.db.execute_batch([
            (
                self.col.update_document,
                ["doc01", {"value": 2}],
                {"wait_for_sync": True}
            ),
            (
                self.col.update_document,
                ["doc02", {"value": 2}],
                {"wait_for_sync": True}
            ),
            (
                self.col.update_document,
                ["doc03", {"value": 2}],
                {"wait_for_sync": True}
            ),
        ])
        self.assertEqual(self.col.document("doc01")["value"], 2)
        self.assertEqual(self.col.document("doc02")["value"], 2)
        self.assertEqual(self.col.document("doc03")["value"], 2)

    def test_batch_document_Delete(self):
        self.col.bulk_import([
            {"_key": "doc01", "value": 1},
            {"_key": "doc02", "value": 1},
            {"_key": "doc03", "value": 1}
        ])
        self.db.execute_batch([
            (self.col.delete_document, ["doc01"], {}),
            (self.col.delete_document, ["doc02"], {}),
            (self.col.delete_document, ["doc03"], {}),
        ])
        self.assertEqual(len(self.col), 0)

    def test_batch_document_mixed(self):
        self.col.bulk_import([
            {"_key": "doc01", "value": 0},
            {"_key": "doc02", "value": 0},
            {"_key": "doc03", "value": 0}
        ])
        self.db.execute_batch([
            (
                self.col.create_document,
                [{"_key": "doc04", "value": 1}],
                {"wait_for_sync": True}
            ),
            (
                self.col.update_document,
                ["doc01", {"value": 2}],
                {"wait_for_sync": True}
            ),
            (
                self.col.replace_document,
                ["doc02", {"new_value": 3}],
                {"wait_for_sync": True}
            ),
            (
                self.col.delete_document,
                ["doc03"],
                {"wait_for_sync": True}
            ),
            (
                self.col.create_document,
                [{"_key": "doc05", "value": 5}],
                {"wait_for_sync": True}
            ),
        ])
        self.assertEqual(len(self.col), 4)
        self.assertEqual(self.col.document("doc01")["value"], 2)
        self.assertEqual(self.col.document("doc02")["new_value"], 3)
        self.assertNotIn("doc03", self.col)
        self.assertEqual(self.col.document("doc04")["value"], 1)
        self.assertEqual(self.col.document("doc05")["value"], 5)

    def test_batch_vertex_create(self):
        self.db.execute_batch([
            (
                self.graph.create_vertex,
                [self.vertex_col_name, {"_key": "v01", "value": 1}],
                {"wait_for_sync": True}
            ),
            (
                self.graph.create_vertex,
                [self.vertex_col_name, {"_key": "v02", "value": 2}],
                {"wait_for_sync": True}
            ),
            (
                self.graph.create_vertex,
                [self.vertex_col_name, {"_key": "v03", "value": 3}],
                {"wait_for_sync": True}
            ),
        ])
        self.assertEqual(self.vertex_col.document("v01")["value"], 1)
        self.assertEqual(self.vertex_col.document("v02")["value"], 2)
        self.assertEqual(self.vertex_col.document("v03")["value"], 3)

    def test_batch_vertex_replace(self):
        self.vertex_col.bulk_import([
            {"_key": "v01", "value": 1},
            {"_key": "v02", "value": 1},
            {"_key": "v03", "value": 1}
        ])
        self.db.execute_batch([
            (
                self.graph.replace_vertex,
                [
                    "{}/{}".format(self.vertex_col_name, "v01"),
                    {"new_val": 2}
                ],
                {"wait_for_sync": True}
            ),
            (
                self.graph.replace_vertex,
                [
                    "{}/{}".format(self.vertex_col_name, "v02"),
                    {"new_val": 3}
                ],
                {"wait_for_sync": True}
            ),
            (
                self.graph.replace_vertex,
                [
                    "{}/{}".format(self.vertex_col_name, "v03"),
                    {"new_val": 4}
                ],
                {"wait_for_sync": True}
            ),
        ])
        self.assertEqual(self.vertex_col.document("v01")["new_val"], 2)
        self.assertEqual(self.vertex_col.document("v02")["new_val"], 3)
        self.assertEqual(self.vertex_col.document("v03")["new_val"], 4)

    def test_batch_vertex_update(self):
        self.vertex_col.bulk_import([
            {"_key": "v01", "value": 1},
            {"_key": "v02", "value": 1},
            {"_key": "v03", "value": 1}
        ])
        self.db.execute_batch([
            (
                self.graph.update_vertex,
                ["{}/{}".format(self.vertex_col_name, "v01"), {"value": 2}],
                {"wait_for_sync": True}
            ),
            (
                self.graph.update_vertex,
                ["{}/{}".format(self.vertex_col_name, "v02"), {"value": 3}],
                {"wait_for_sync": True}
            ),
            (
                self.graph.update_vertex,
                ["{}/{}".format(self.vertex_col_name, "v03"), {"value": 4}],
                {"wait_for_sync": True}
            ),
        ])
        self.assertEqual(self.vertex_col.document("v01")["value"], 2)
        self.assertEqual(self.vertex_col.document("v02")["value"], 3)
        self.assertEqual(self.vertex_col.document("v03")["value"], 4)

    def test_batch_vertex_Delete(self):
        self.vertex_col.bulk_import([
            {"_key": "v01", "value": 1},
            {"_key": "v02", "value": 1},
            {"_key": "v03", "value": 1}
        ])
        self.db.execute_batch([
            (
                self.graph.delete_vertex,
                ["{}/{}".format(self.vertex_col_name, "v01")],
                {"wait_for_sync": True}
            ),
            (
                self.graph.delete_vertex,
                ["{}/{}".format(self.vertex_col_name, "v02")],
                {"wait_for_sync": True}
            ),
            (
                self.graph.delete_vertex,
                ["{}/{}".format(self.vertex_col_name, "v03")],
                {"wait_for_sync": True}
            ),
        ])
        self.assertEqual(len(self.vertex_col), 0)

    def test_batch_edge_create(self):
        self.vertex_col.bulk_import([
            {"_key": "v01", "value": 1},
            {"_key": "v02", "value": 1},
            {"_key": "v03", "value": 1}
        ])
        self.db.execute_batch([
            (
                self.graph.create_edge,
                [self.edge_col_name],
                {
                    "data": {
                        "_key": "e01",
                        "_from": "{}/{}".format(self.vertex_col_name, "v01"),
                        "_to": "{}/{}".format(self.vertex_col_name, "v02"),
                        "value": 4
                    }
                }
            ),
            (
                self.graph.create_edge,
                [self.edge_col_name],
                {
                    "data": {
                        "_key": "e02",
                        "_from": "{}/{}".format(self.vertex_col_name, "v02"),
                        "_to": "{}/{}".format(self.vertex_col_name, "v03"),
                        "value": 5
                    }
                }
            ),
        ])
        self.assertEqual(self.edge_col.document("e01")["value"], 4)
        self.assertEqual(self.edge_col.document("e02")["value"], 5)

    def test_batch_edge_replace(self):
        self.vertex_col.bulk_import([
            {"_key": "v01", "value": 1},
            {"_key": "v02", "value": 1},
            {"_key": "v03", "value": 1}
        ])
        self.db.execute_batch([
            (
                self.graph.create_edge,
                [self.edge_col_name],
                {
                    "data": {
                        "_key": "e01",
                        "_from": "{}/{}".format(self.vertex_col_name, "v01"),
                        "_to": "{}/{}".format(self.vertex_col_name, "v02"),
                        "value": 4
                    }
                }
            ),
            (
                self.graph.create_edge,
                [self.edge_col_name],
                {
                    "data": {
                        "_key": "e02",
                        "_from": "{}/{}".format(self.vertex_col_name, "v02"),
                        "_to": "{}/{}".format(self.vertex_col_name, "v03"),
                        "value": 5
                    }
                }
            ),
        ])
        self.db.execute_batch([
            (
                self.graph.replace_edge,
                ["{}/{}".format(self.edge_col_name, "e01")],
                {"data": {"new_val": 1}}
            ),
            (
                self.graph.replace_edge,
                ["{}/{}".format(self.edge_col_name, "e02")],
                {"data": {"new_val": 2}}
            ),
        ])
        self.assertEqual(self.edge_col.document("e01")["new_val"], 1)
        self.assertEqual(self.edge_col.document("e02")["new_val"], 2)

    def test_batch_edge_update(self):
        self.vertex_col.bulk_import([
            {"_key": "v01", "value": 1},
            {"_key": "v02", "value": 1},
            {"_key": "v03", "value": 1}
        ])
        self.db.execute_batch([
            (
                self.graph.create_edge,
                [self.edge_col_name],
                {
                    "data": {
                        "_key": "e01",
                        "_from": "{}/{}".format(self.vertex_col_name, "v01"),
                        "_to": "{}/{}".format(self.vertex_col_name, "v02"),
                        "value": 4
                    }
                }
            ),
            (
                self.graph.create_edge,
                [self.edge_col_name],
                {
                    "data": {
                        "_key": "e02",
                        "_from": "{}/{}".format(self.vertex_col_name, "v02"),
                        "_to": "{}/{}".format(self.vertex_col_name, "v03"),
                        "value": 5
                    }
                }
            ),
        ])
        self.db.execute_batch([
            (
                self.graph.replace_edge,
                ["{}/{}".format(self.edge_col_name, "e01")],
                {"data": {"value": 1}}
            ),
            (
                self.graph.replace_edge,
                ["{}/{}".format(self.edge_col_name, "e02")],
                {"data": {"value": 2}}
            ),
        ])
        self.assertEqual(self.edge_col.document("e01")["value"], 1)
        self.assertEqual(self.edge_col.document("e02")["value"], 2)

    def test_batch_edge_Delete(self):
        self.vertex_col.bulk_import([
            {"_key": "v01", "value": 1},
            {"_key": "v02", "value": 1},
            {"_key": "v03", "value": 1}
        ])
        self.db.execute_batch([
            (
                self.graph.create_edge,
                [self.edge_col_name],
                {
                    "data": {
                        "_key": "e01",
                        "_from": "{}/{}".format(self.vertex_col_name, "v01"),
                        "_to": "{}/{}".format(self.vertex_col_name, "v02"),
                        "value": 4
                    }
                }
            ),
            (
                self.graph.create_edge,
                [self.edge_col_name],
                {
                    "data": {
                        "_key": "e02",
                        "_from": "{}/{}".format(self.vertex_col_name, "v02"),
                        "_to": "{}/{}".format(self.vertex_col_name, "v03"),
                        "value": 5
                    }
                }
            ),
        ])
        self.assertEqual(len(self.edge_col), 2)
        self.db.execute_batch([
            (
                self.graph.delete_edge,
                ["{}/{}".format(self.edge_col_name, "e01")],
                {}
            ),
            (
                self.graph.delete_edge,
                ["{}/{}".format(self.edge_col_name, "e02")],
                {}
            ),
        ])
        self.assertEqual(len(self.edge_col), 0)


if __name__ == "__main__":
    unittest.main()
