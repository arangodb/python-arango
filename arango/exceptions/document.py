from arango.exceptions import ArangoError


class DocumentError(ArangoError):
    """Base class for errors in Document queries"""


class DocumentCountError(DocumentError):
    """Failed to retrieve the count of the documents in the collections."""


class DocumentInError(DocumentError):
    """Failed to check whether a collection contains a document."""


class DocumentGetError(DocumentError):
    """Failed to retrieve the document."""


class DocumentInsertError(DocumentError):
    """Failed to insert the document."""


class DocumentReplaceError(DocumentError):
    """Failed to replace the document."""


class DocumentUpdateError(DocumentError):
    """Failed to update the document."""


class DocumentDeleteError(DocumentError):
    """Failed to delete the document."""


class DocumentRevisionError(DocumentError):
    """The expected and actual document revisions do not match."""
