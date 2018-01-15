from arango.cursors import Cursor


class ExportCursor(Cursor):  # pragma: no cover
    """ArangoDB cursor for export queries only.

    .. note::
        This class is designed to be instantiated internally only.
    """

    def __init__(self, connection, init_data):
        super(ExportCursor, self).__init__(connection, init_data)
        super(ExportCursor, self)._set_cursor_type('export')
