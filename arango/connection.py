from __future__ import absolute_import, unicode_literals

from arango.http import DefaultHTTPClient

__all__ = ['Connection']


class Connection(object):
    """HTTP connection to specific ArangoDB database.

    :param url: ArangoDB base URL.
    :type url: str | unicode
    :param db: Database name.
    :type db: str | unicode
    :param username: Username.
    :type username: str | unicode
    :param password: Password.
    :type password: str | unicode
    :param http_client: User-defined HTTP client.
    :type http_client: arango.http.HTTPClient
    """

    def __init__(self, url, db, username, password, http_client):
        self._url_prefix = '{}/_db/{}'.format(url, db)
        self._db_name = db
        self._username = username
        self._auth = (username, password)
        self._http_client = http_client or DefaultHTTPClient()

    @property
    def url_prefix(self):
        """Return the ArangoDB URL prefix (base URL + database name).

        :returns: ArangoDB URL prefix.
        :rtype: str | unicode
        """
        return self._url_prefix

    @property
    def username(self):
        """Return the username.

        :returns: Username.
        :rtype: str | unicode
        """
        return self._username

    @property
    def db_name(self):
        """Return the database name.

        :returns: Database name.
        :rtype: str | unicode
        """
        return self._db_name

    def send_request(self, request):
        """Send an HTTP request to ArangoDB server.

        :param request: HTTP request.
        :type request: arango.request.Request
        :return: HTTP response.
        :rtype: arango.response.Response
        """
        return self._http_client.send_request(
            method=request.method,
            url=self._url_prefix + request.endpoint,
            params=request.params,
            data=request.data,
            headers=request.headers,
            auth=self._auth,
        )
