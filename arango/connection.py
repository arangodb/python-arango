from __future__ import absolute_import, unicode_literals

from six import string_types

from arango.exceptions import ServerConnectionError
from arango.response import Response

__all__ = ['Connection']


class Connection(object):
    """Connection to specific ArangoDB database.

    :param hosts: Host URL or list of URLs (coordinators in a cluster).
    :type hosts: [str | unicode]
    :param host_resolver: Host resolver (used for clusters).
    :type host_resolver: arango.resolver.HostResolver
    :param sessions: HTTP session objects per host.
    :type sessions: [requests.Session]
    :param db_name: Database name.
    :type db_name: str | unicode
    :param username: Username.
    :type username: str | unicode
    :param password: Password.
    :type password: str | unicode
    :param http_client: User-defined HTTP client.
    :type http_client: arango.http.HTTPClient
    """

    def __init__(self,
                 hosts,
                 host_resolver,
                 sessions,
                 db_name,
                 username,
                 password,
                 http_client,
                 serializer,
                 deserializer):
        self._url_prefixes = ['{}/_db/{}'.format(h, db_name) for h in hosts]
        self._host_resolver = host_resolver
        self._sessions = sessions
        self._db_name = db_name
        self._username = username
        self._auth = (username, password)
        self._http = http_client
        self._serializer = serializer
        self._deserializer = deserializer

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

    def serialize(self, obj):
        """Serialize the object and return the string.

        :param obj: Object to serialize.
        :type obj: str | unicode | bool | int | list | dict
        :return: Serialized string.
        :rtype: str | unicode
        """
        return self._serializer(obj)

    def deserialize(self, string):
        """De-serialize the string and return the object.

        :param string: String to de-serialize.
        :type string: str | unicode
        :return: De-serialized object.
        :rtype: str | unicode | bool | int | list | dict
        """
        try:
            return self._deserializer(string)
        except (ValueError, TypeError):
            return string

    def prep_response(self, response, deserialize=True):
        """Populate the response with details and return it.

        :param deserialize: Deserialize the response body.
        :type deserialize: bool
        :param response: HTTP response.
        :type response: arango.response.Response
        :return: HTTP response.
        :rtype: arango.response.Response
        """
        if deserialize:
            response.body = self.deserialize(response.raw_body)
            if isinstance(response.body, dict):
                response.error_code = response.body.get('errorNum')
                response.error_message = response.body.get('errorMessage')
        else:
            response.body = response.raw_body

        http_ok = 200 <= response.status_code < 300
        response.is_success = http_ok and response.error_code is None
        return response

    def build_error_response(self, parent_response, body):
        """Build and return a bulk error response.

        :param parent_response: Parent response.
        :type parent_response: arango.response.Response
        :param body: Error response body.
        :type body: dict
        :return: Child bulk error response.
        :rtype: arango.response.Response
        """
        response = Response(
            method=parent_response.method,
            url=parent_response.url,
            headers=parent_response.headers,
            status_code=parent_response.status_code,
            status_text=parent_response.status_text,
            raw_body=self.serialize(body),
        )
        response.body = body
        response.error_code = body['errorNum']
        response.error_message = body['errorMessage']
        response.is_success = False
        return response

    def send_request(self, request):
        """Send an HTTP request to ArangoDB server.

        :param request: HTTP request.
        :type request: arango.request.Request
        :return: HTTP response.
        :rtype: arango.response.Response
        """
        if request.data is None or isinstance(request.data, string_types):
            normalized_data = request.data
        else:
            normalized_data = self.serialize(request.data)

        host_index = self._host_resolver.get_host_index()
        response = self._http.send_request(
            session=self._sessions[host_index],
            method=request.method,
            url=self._url_prefixes[host_index] + request.endpoint,
            params=request.params,
            data=normalized_data,
            headers=request.headers,
            auth=self._auth,
        )
        return self.prep_response(response, request.deserialize)

    def ping(self):
        for host_index in range(len(self._sessions)):
            resp = self._http.send_request(
                session=self._sessions[host_index],
                method='get',
                url=self._url_prefixes[host_index] + '/_api/collection',
                auth=self._auth,
            )
            resp = self.prep_response(resp)

            code = resp.status_code
            if code in {401, 403}:
                raise ServerConnectionError('bad username and/or password')
            if not (200 <= code < 300):  # pragma: no cover
                raise ServerConnectionError(
                    resp.error_message or 'bad server response')
            return code
