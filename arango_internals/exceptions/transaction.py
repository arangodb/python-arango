from arango_internals.exceptions import ArangoError


class TransactionError(ArangoError):
    """Failed to execute a transaction."""
