"""Tests for managing ArangoDB documents."""

import unittest

from arango import Arango
from arango.exceptions import *
from arango.tests.utils import (
    get_next_col_name,
    get_next_db_name,
    strip_system_keys,
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
        self.col.add_geo_index(["coord"])
        self.col.add_skiplist_index(["value"])
        self.col.add_fulltext_index(["text"])

    def tearDown(self):
        self.arango.remove_collection(self.col_name)

    def test_add_document(self):
        self.assertEqual(len(self.col), 0)
        self.col.add_document({"_key": "test_doc"})
        self.assertEqual(len(self.col), 1)
        self.assertIn("test_doc", self.col)

    def test_remove_document(self):
        rev = self.col.add_document({"_key": "test_doc"})["_rev"]
        self.assertEqual(len(self.col), 1)
        self.assertRaises(
            DocumentRemoveError,
            self.col.remove_document,
            "test_doc",
            rev="wrong_revision"
        )
        self.col.remove_document("test_doc", rev=rev)
        self.assertEqual(len(self.col), 0)
        self.assertNotIn("test_doc", self.col)

    def test_replace_document(self):
        rev = self.col.add_document({
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
        rev = self.col.add_document({
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
        self.col.add_document({"_key": "test_doc_01"})
        self.col.add_document({"_key": "test_doc_02"})
        self.col.add_document({"_key": "test_doc_03"})
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
            CollectionBulkImportError,
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

    def test_first(self):
        self.assertEqual(strip_system_keys(self.col.first(1)), [])
        self.col.bulk_import([
            {"name": "test_doc_01"},
            {"name": "test_doc_02"},
            {"name": "test_doc_03"}
        ])
        self.assertEqual(len(self.col), 3)
        self.assertEqual(
            strip_system_keys(self.col.first(1)),
            [{"name": "test_doc_01"}]
        )
        self.assertEqual(
            strip_system_keys(self.col.first(2)),
            [{"name": "test_doc_01"}, {"name": "test_doc_02"}]
        )

    def test_last(self):
        self.assertEqual(strip_system_keys(self.col.last(1)), [])
        self.col.bulk_import([
            {"name": "test_doc_01"},
            {"name": "test_doc_02"},
            {"name": "test_doc_03"}
        ])
        self.assertEqual(len(self.col), 3)
        self.assertEqual(
            strip_system_keys(self.col.last(1)),
            [{"name": "test_doc_03"}]
        )
        self.assertEqual(
            sorted(strip_system_keys(self.col.last(2))),
            sorted([{"name": "test_doc_03"}, {"name": "test_doc_02"}])
        )

    def test_all(self):
        self.assertEqual(list(self.col.all()), [])
        self.col.bulk_import([
            {"name": "test_doc_01"},
            {"name": "test_doc_02"},
            {"name": "test_doc_03"}
        ])
        self.assertEqual(len(self.col), 3)
        self.assertEqual(
            sorted(strip_system_keys(self.col.all())),
            sorted([
                {"name": "test_doc_01"},
                {"name": "test_doc_02"},
                {"name": "test_doc_03"}
            ])
        )

    def test_any(self):
        self.assertEqual(strip_system_keys(self.col.all()), [])
        self.col.bulk_import([
            {"name": "test_doc_01"},
            {"name": "test_doc_02"},
            {"name": "test_doc_03"}
        ])
        self.assertIn(
            strip_system_keys(self.col.any()),
            [
                {"name": "test_doc_01"},
                {"name": "test_doc_02"},
                {"name": "test_doc_03"}
            ]
        )

    def test_get_first_example(self):
        self.assertEqual(
            self.col.get_first_example({"value": 1}), None
        )
        self.col.bulk_import([
            {"name": "test_doc_01", "value": 1},
            {"name": "test_doc_02", "value": 1},
            {"name": "test_doc_03", "value": 3}
        ])
        self.assertIn(
            strip_system_keys(self.col.get_first_example({"value": 1})),
            [
                {"name": "test_doc_01", "value" :1},
                {"name": "test_doc_02", "value" :1}
            ]
        )

    def test_get_by_example(self):
        self.col.bulk_import([
            {"name": "test_doc_01", "value": 1},
            {"name": "test_doc_02", "value": 1},
            {"name": "test_doc_03", "value": 3}
        ])
        self.assertEqual(
            sorted(strip_system_keys(self.col.get_by_example({"value": 1}))),
            sorted([
                {"name": "test_doc_01", "value" :1},
                {"name": "test_doc_02", "value": 1},
            ])
        )
        self.assertEqual(
            strip_system_keys(self.col.get_by_example({"value": 2})), []
        )
        self.assertTrue(
            len(list(self.col.get_by_example({"value": 1}, limit=1))), 1
        )

    def test_update_by_example(self):
        self.col.bulk_import([
            {"name": "test_doc_01", "value": 1},
            {"name": "test_doc_02", "value": 1},
            {"name": "test_doc_03", "value": 3}
        ])
        self.col.update_by_example({"value": 1}, {"value": 2})
        self.assertEqual(
            sorted(strip_system_keys(self.col.all())),
            sorted([
                {"name": "test_doc_01", "value": 2},
                {"name": "test_doc_02", "value": 2},
                {"name": "test_doc_03", "value": 3}
            ])
        )

    def test_replace_by_example(self):
        self.col.bulk_import([
            {"name": "test_doc_01", "value": 1},
            {"name": "test_doc_02", "value": 1},
            {"name": "test_doc_03", "value": 3}
        ])
        self.col.replace_by_example({"value": 1}, {"foo": "bar"})
        self.assertEqual(
            sorted(strip_system_keys(self.col.all())),
            sorted([
                {"foo": "bar"},
                {"foo": "bar"},
                {"name": "test_doc_03", "value": 3}
            ])
        )

    def test_remove_by_example(self):
        self.col.bulk_import([
            {"name": "test_doc_01", "value": 1},
            {"name": "test_doc_02", "value": 1},
            {"name": "test_doc_03", "value": 3}
        ])
        self.col.remove_by_example({"value": 1})
        self.col.remove_by_example({"value": 2})
        self.assertEqual(
            strip_system_keys(self.col.all()),
            [{"name": "test_doc_03", "value": 3}]
        )

    def test_range(self):
        self.col.bulk_import([
            {"name": "test_doc_01", "value": 1},
            {"name": "test_doc_02", "value": 2},
            {"name": "test_doc_03", "value": 3},
            {"name": "test_doc_04", "value": 4},
            {"name": "test_doc_05", "value": 5}
        ])
        self.assertEqual(
            strip_system_keys(
                self.col.range(
                    attribute="value",
                    left=2,
                    right=5,
                    closed=True,
                    skip=1,
                    limit=2
                )
            ),
            [
                {"name": "test_doc_03", "value": 3},
                {"name": "test_doc_04", "value": 4},
            ]
        )

    def test_near(self):
        self.col.bulk_import([
             {"name": "test_doc_01", "coord": [1,1]},
             {"name": "test_doc_02", "coord": [1,4]},
             {"name": "test_doc_03", "coord": [4,1]},
             {"name": "test_doc_03", "coord": [4,4]},
        ])
        self.assertEqual(
            strip_system_keys(
                self.col.near(
                    latitude=1,
                    longitude=1,
                    limit=1,
                )
            ),
            [
                {"name": "test_doc_01", "coord": [1,1]}
            ]
        )

    # TODO enable when the endpoint is fixed
    #def test_within(self):
        #self.col.bulk_import([
            #{"name": "test_doc_01", "coord": [1,1]},
            #{"name": "test_doc_02", "coord": [1,4]},
            #{"name": "test_doc_03", "coord": [4,1]},
            #{"name": "test_doc_03", "coord": [4,4]},
        #])
        #self.assertEqual(
            #strip_system_keys(
                #self.col.within(
                    #latitude=0,
                    #longitude=0,
                    #radius=3.5,
                #)
            #),
            #[
                #{"name": "test_doc_01", "coord": [1,1]},
                #{"name": "test_doc_02", "coord": [1,4]},
                #{"name": "test_doc_03", "coord": [4,1]},
            #]
        #)

    def test_fulltext(self):
        self.col.bulk_import([
             {"name": "test_doc_01", "text": "Hello World!"},
             {"name": "test_doc_02", "text": "foo"},
             {"name": "test_doc_03", "text": "bar"},
             {"name": "test_doc_03", "text": "baz"},
        ])
        self.assertEqual(
            strip_system_keys(self.col.fulltext("text", "foo,|bar")),
            [
                {"name": "test_doc_02", "text": "foo"},
                {"name": "test_doc_03", "text": "bar"},
            ]
        )


if __name__ == "__main__":
    unittest.main()
