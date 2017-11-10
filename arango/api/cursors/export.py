from arango.api.cursors import BaseCursor


class ExportCursor(BaseCursor):  # pragma: no cover
    """ArangoDB cursor for export queries only.

    .. note::
        This class is designed to be instantiated internally only.
    """

    def __init__(self, connection, init_data):
        super(ExportCursor, self).__init__(connection, init_data,
                                           cursor_type="export")
