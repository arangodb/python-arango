from arango.exceptions import ArangoError


class CollectionError(ArangoError):
    """Base class for errors in Collection queries"""


class CollectionListError(CollectionError):
    """Failed to retrieve the list of collections."""


class CollectionPropertiesError(CollectionError):
    """Failed to retrieve the collection properties."""


class CollectionConfigureError(CollectionError):
    """Failed to configure the collection properties."""


class CollectionStatisticsError(CollectionError):
    """Failed to retrieve the collection statistics."""


class CollectionRevisionError(CollectionError):
    """Failed to retrieve the collection revision."""


class CollectionChecksumError(CollectionError):
    """Failed to retrieve the collection checksum."""


class CollectionCreateError(CollectionError):
    """Failed to create the collection."""


class CollectionDeleteError(CollectionError):
    """Failed to delete the collection"""


class CollectionRenameError(CollectionError):
    """Failed to rename the collection."""


class CollectionTruncateError(CollectionError):
    """Failed to truncate the collection."""


class CollectionLoadError(CollectionError):
    """Failed to load the collection into memory."""


class CollectionUnloadError(CollectionError):
    """Failed to unload the collection from memory."""


class CollectionRotateJournalError(CollectionError):
    """Failed to rotate the journal of the collection."""


class CollectionBadStatusError(CollectionError):
    """Unknown status was returned from the collection."""
