from arango.exceptions import ArangoError


class WALError(ArangoError):
    """Base class for errors in WAL queries"""


class WALPropertiesError(WALError):
    """Failed to retrieve the write-ahead log."""


class WALConfigureError(WALError):
    """Failed to configure the write-ahead log."""


class WALTransactionListError(WALError):
    """Failed to retrieve the list of running transactions."""


class WALFlushError(WALError):
    """Failed to flush the write-ahead log."""
