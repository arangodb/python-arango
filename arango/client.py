"""Request Client for ArangoDB"""

import requests


class ArangoRequestClient(object):

    def __init__(self, host, port):
        self._host = host
        self._port = port
        self._sess = requests.Session()

    def url(self, path, db=None):
        """Return the full request URL.

        :param path: the API path.
        :type path: str.
        :param db: name of the database.
        :type db: str or None.
        :returns: str.
        """
        path=path[1:] if path.startswith("/") else path
        if db is not None:
            return "http://{host}:{port}/_db/{db}/_api/{path}".format(
                host=self._host,
                port=self._port,
                db = db,
                path=path
            )
        else:  # Use the default database if not specified
            return "http://{host}:{port}/_api/{path}".format(
                host=self._host,
                port=self._port,
                path=path
            )

    def get(self, path, db=None, **kwargs):
        """Execute an HTTP GET method."""
        return self._sess.get(self.url(path, db), **kwargs)

    def put(self, path, db=None, **kwargs):
        """Execute an HTTP PUT method."""
        return self._sess.put(self.url(path, db), **kwargs)

    def post(self, path, db=None, **kwargs):
        """Execute an HTTP POST method."""
        return self._sess.post(self.url(path, db), **kwargs)

    def delete(self, path, db=None, **kwargs):
        """Execute an HTTP DELETE method."""
        return self._sess.delete(self.url(path, db), **kwargs)
