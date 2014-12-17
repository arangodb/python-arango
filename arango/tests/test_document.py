"""Tests for managing ArangoDB documents."""

import unittest

from arango import Arango
from arango.exceptions import *
from arango.tests.test_utils import (
    get_next_col_name,
    get_next_db_name
)


class DocumentManagementTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.arango = Arango()
        cls.db_name = get_next_db_name(cls.arango)
        cls.db = cls.arango.add_database(cls.db_name)

    @classmethod
    def tearDownClass(cls):
        cls.arango.remove_database(cls.db_name)

    def setUp(self):
        self.col_name = get_next_col_name(self.arango)
        self.col = self.arango.add_collection(self.col_name)

    def tearDown(self):
        self.arango.remove_collection(self.col_name)

    def test_add_document(self):
        self.assertEqual(len(self.col), 0)
        self.col.add({"_key": "test_doc"})
        self.assertEqual(len(self.col), 1)
        self.assertIn("test_doc", self.col)

    def test_remove_document(self):
        rev = self.col.add({"_key": "test_doc"})["_rev"]
        self.assertEqual(len(self.col), 1)
        self.assertRaises(
            ArangoDocumentRemoveError,
            self.col.remove,
            "test_doc",
            rev="wrong_revision"
        )
        self.col.remove("test_doc", rev=rev)
        self.assertEqual(len(self.col), 0)
        self.assertNotIn("test_doc", self.col)

    def test_replace_document(self):
        rev = self.col.add({
            "_key": "test_doc",
            "value": 1,
            "value2": 2,
        })["_rev"]
        self.assertRaises(
            ArangoDocumentReplaceError,
            self.col.replace,
            "test_doc",
            {"value": 2},
            rev="wrong_revision"
        )
        self.col.replace("test_doc", {"value": 2}, rev=rev)
        self.assertEqual(self.col["test_doc"]["value"], 2)
        self.assertNotIn("value2", self.col["test_doc"])

    def test_update_document(self):
        rev = self.col.add({
            "_key": "test_doc",
            "value": 1,
            "value2": 2,
        })["_rev"]
        self.assertRaises(
            ArangoDocumentUpdateError,
            self.col.update,
            "test_doc",
            {"value": 2},
            "wrong_revision"
        )
        self.col.update("test_doc", {"value": 2}, rev=rev)
        self.assertEqual(self.col["test_doc"]["value"], 2)
        self.assertEqual(self.col["test_doc"]["value2"], 2)

    def test_truncate(self):
        self.col.add({"_key": "test_doc_01"})
        self.col.add({"_key": "test_doc_02"})
        self.col.add({"_key": "test_doc_03"})
        self.assertEqual(len(self.col), 3)
        self.col.truncate()
        self.assertEqual(len(self.col), 0)

    def test_bulk_import(self):
        documents = [
            {"_key": "test_doc_01"},
            {"_key": "test_doc_02"},
            {"_key": 1}  # invalid key
        ]
        # This should succeed partially
        res = self.col.bulk_import(documents, complete=False)
        self.assertEqual(len(self.col), 2)
        self.assertIn("test_doc_01", self.col)
        self.assertIn("test_doc_01", self.col)
        self.assertEqual(res["errors"], 1)
        self.assertEqual(res["created"], 2)
        # This should fail because of the last document
        self.col.truncate()
        self.assertRaises(
            ArangoCollectionBulkImportError,
            self.col.bulk_import,
            documents,
            complete=True
        )
        self.assertEqual(len(self.col), 0)
        # This should succeed completely since all documents are valid
        self.col.truncate()
        res = self.col.bulk_import(documents[:2], complete=True)
        self.assertEqual(len(self.col), 2)
        self.assertEqual(res["errors"], 0)
        self.assertEqual(res["created"], 2)


if __name__ == "__main__":
    unittest.main()