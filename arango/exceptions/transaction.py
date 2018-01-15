from arango.exceptions import ArangoError


class TransactionError(ArangoError):
    """Failed to execute a transaction."""
