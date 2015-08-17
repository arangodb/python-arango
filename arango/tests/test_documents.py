"""Tests for ArangoDB Document Management."""

import unittest

from arango import Arango
from arango.exceptions import (
    DocumentDeleteError,
    DocumentReplaceError,
    DocumentUpdateError,
    DocumentsImportError,
)
from arango.tests.utils import (
    get_next_col_name,
    get_next_db_name,
)


class DocumentManagementTest(unittest.TestCase):
    """Tests for ArangoDB document management."""

    def setUp(self):
        self.arango = Arango()
        self.db_name = get_next_db_name(self.arango)
        self.db = self.arango.create_database(self.db_name)
        self.col_name = get_next_col_name(self.db)
        self.col = self.db.create_collection(self.col_name)

        # Test database cleaup
        self.addCleanup(self.arango.delete_database,
                        name=self.db_name, safe_delete=True)

    def test_create_document(self):
        self.assertEqual(len(self.col), 0)
        self.col.create_document({"_key": "test_doc"})
        self.assertEqual(len(self.col), 1)
        self.assertIn("test_doc", self.col)

    def test_delete_document(self):
        rev = self.col.create_document({"_key": "test_doc"})["_rev"]
        self.assertEqual(len(self.col), 1)
        self.assertRaises(
            DocumentDeleteError,
            self.col.delete_document,
            "test_doc",
            rev="wrong_revision"
        )
        self.col.delete_document("test_doc", rev=rev)
        self.assertEqual(len(self.col), 0)
        self.assertNotIn("test_doc", self.col)

    def test_replace_document(self):
        rev = self.col.create_document({
            "_key": "test_doc",
            "value": 1,
            "value2": 2,
        })["_rev"]
        self.assertRaises(
            DocumentReplaceError,
            self.col.replace_document,
            "test_doc",
            {"_rev": "wrong_revision", "value": 2},
        )
        self.col.replace_document(
            "test_doc",
            {"_rev": rev, "value": 2}
        )
        self.assertEqual(self.col["test_doc"]["value"], 2)
        self.assertNotIn("value2", self.col["test_doc"])

    def test_update_document(self):
        rev = self.col.create_document({
            "_key": "test_doc",
            "value": 1,
            "value2": 2,
        })["_rev"]
        self.assertRaises(
            DocumentUpdateError,
            self.col.update_document,
            "test_doc",
            {"_rev": "wrong_revision", "value": 2},
        )
        self.col.update_document(
            "test_doc",
            {"_rev": rev, "new_value": 2}
        )
        self.assertEqual(self.col["test_doc"]["value"], 1)
        self.assertEqual(self.col["test_doc"]["new_value"], 2)

    def test_truncate(self):
        self.col.create_document({"_key": "test_doc_01"})
        self.col.create_document({"_key": "test_doc_02"})
        self.col.create_document({"_key": "test_doc_03"})
        self.assertEqual(len(self.col), 3)
        self.col.truncate()
        self.assertEqual(len(self.col), 0)

    def test_import_documents(self):
        documents = [
            {"_key": "test_doc_01"},
            {"_key": "test_doc_02"},
            {"_key": 1}  # invalid key
        ]
        # This should succeed partially
        res = self.col.import_documents(documents, complete=False)
        self.assertEqual(len(self.col), 2)
        self.assertIn("test_doc_01", self.col)
        self.assertIn("test_doc_01", self.col)
        self.assertEqual(res["errors"], 1)
        self.assertEqual(res["created"], 2)
        # This should fail because of the last document
        self.col.truncate()
        self.assertRaises(
            DocumentsImportError,
            self.col.import_documents,
            documents,
            complete=True
        )
        self.assertEqual(len(self.col), 0)
        # This should succeed completely since all documents are valid
        self.col.truncate()
        res = self.col.import_documents(documents[:2], complete=True)
        self.assertEqual(len(self.col), 2)
        self.assertEqual(res["errors"], 0)
        self.assertEqual(res["created"], 2)

    def test_export_documents(self):
        pass


if __name__ == "__main__":
    unittest.main()
