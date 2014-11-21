"""ArangoDB Document."""


class ArangoDocumentMixin(object):
    """ArangoDB document mix-in class for ArangoCollection"""


    def add(self, document, overwrite=True):
        """Add a document to this collection."""

    def remove(self, document):
        """Delete the document from this collection."""

    def add_batch(self, documents):
        """Add the documents in one batch request."""

    def remove_batch(self, documents):
        """Remove the documents in one batch request."""