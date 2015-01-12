"""Tests for ArangoDB Batch Requests."""

import unittest
from arango import Arango
from arango.tests.utils import (
    get_next_db_name,
    get_next_col_name
)

class BatchRequestTest(unittest.TestCase):

    def setUp(self):
        self.arango = Arango()
        self.db_name = get_next_db_name(self.arango)
        self.db = self.arango.add_database(self.db_name)
        self.col_name = get_next_col_name(self.db)
        self.col = self.db.add_collection(self.col_name)

    def tearDown(self):
        self.arango.remove_database(self.db_name)

    def test_batch_document_add(self):
        res = self.db.execute_batch([
            (self.col.add_document, [{"value": 1}], {}),
            (self.col.add_document, [{"value": 2}], {}),
            (self.col.add_document, [{"value": 3}], {}),
        ])

    def test_batch_document_replace(self):
        res = self.db.execute_batch([
            (self.col.add_document, [{"_key": "doc01", "value": 1}], {}),
            (self.col.add_document, [{"_key": "doc02", "value": 1}], {}),
            (self.col.add_document, [{"_key": "doc03", "value": 1}], {}),
        ])
        self.assertEqual(len(self.col), 3)
        res = self.db.execute_batch([
            (self.col.replace_document, ["doc01", {"value": 2}], {}),
            (self.col.replace_document, ["doc02", {"value": 2}], {}),
            (self.col.replace_document, ["doc03", {"value": 2}], {}),
        ])
        self.assertEqual(self.col.get_document("doc01")["value"], 2)
        self.assertEqual(self.col.get_document("doc02")["value"], 2)
        self.assertEqual(self.col.get_document("doc03")["value"], 2)

    def test_batch_document_update(self):
        res = self.db.execute_batch([
            (self.col.add_document, [{"_key": "doc01", "value": 1}], {}),
            (self.col.add_document, [{"_key": "doc02", "value": 1}], {}),
            (self.col.add_document, [{"_key": "doc03", "value": 1}], {}),
        ])
        self.assertEqual(len(self.col), 3)
        res = self.db.execute_batch([
            (self.col.update_document, ["doc01", {"value": 2}], {}),
            (self.col.update_document, ["doc02", {"value": 2}], {}),
            (self.col.update_document, ["doc03", {"value": 2}], {}),
        ])
        self.assertEqual(self.col.get_document("doc01")["value"], 2)
        self.assertEqual(self.col.get_document("doc02")["value"], 2)
        self.assertEqual(self.col.get_document("doc03")["value"], 2)

    def test_batch_document_remove(self):
        res = self.db.execute_batch([
            (self.col.add_document, [{"_key": "doc01", "value": 1}], {}),
            (self.col.add_document, [{"_key": "doc02", "value": 1}], {}),
            (self.col.add_document, [{"_key": "doc03", "value": 1}], {}),
        ])
        self.assertEqual(len(self.col), 3)
        res = self.db.execute_batch([
            (self.col.remove_document, ["doc01"], {}),
            (self.col.remove_document, ["doc02"], {}),
            (self.col.remove_document, ["doc03"], {}),
        ])
        self.assertEqual(len(self.col), 0)

    def test_batch_vertex_add(self):
        pass

    def test_batch_vertex_replace(self):
        pass

    def test_batch_vertex_update(self):
        pass

    def test_batch_vertex_remove(self):
        pass

    def test_batch_edge_add(self):
        pass

    def test_batch_edge_replace(self):
        pass

    def test_batch_edge_update(self):
        pass

    def test_batch_edge_remove(self):
        pass

if __name__ == "__main__":
    unittest.main()