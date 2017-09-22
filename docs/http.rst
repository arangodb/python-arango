.. _http-client-page:

Using Your Own HTTP Clients
---------------------------

**Python-arango** allows you to use your own custom HTTP clients. Your client
must inherit from :class:`arango.http_clients.base.BaseHTTPClient`, and all of
its abstract methods must be implemented/overridden.

The overridden methods must conform to their original method signatures and
return instances of :class:`arango.response.Response`.

Let's go through a quick example. Let's say you want to use an HTTP client with
built-in retries and SSL certificate verification disabled. You may want to
define your ``MyCustomHTTPClient`` class as follows:

.. code-block:: python

    from __future__ import absolute_import, unicode_literals

    from requests.packages.urllib3.util import Retry
    from requests.adapters import HTTPAdapter
    from requests import Session, exceptions

    from arango.response import Response
    from arango.http_clients.base import BaseHTTPClient


    class MyCustomHTTPClient(BaseHTTPClient):

        def __init__(self, max_retries=5):
            self._session = Session()
            self._session.mount('https://', HTTPAdapter(
                max_retries=Retry(total=max_retries, status_forcelist=[500])
            ))
            self._check_cert = False

        def head(self, url, params=None, headers=None, auth=None):
            res = self._session.head(
                url=url,
                params=params,
                headers=headers,
                auth=auth,
                verify=self._check_cert
            )
            return Response(
                url=url,
                method="head",
                headers=res.headers,
                http_code=res.status_code,
                http_text=res.reason,
                body=res.text
            )

        def get(self, url, params=None, headers=None, auth=None):
            res = self._session.get(
                url=url,
                params=params,
                headers=headers,
                auth=auth,
                verify=self._check_cert
            )
            return Response(
                url=url,
                method="get",
                headers=res.headers,
                http_code=res.status_code,
                http_text=res.reason,
                body=res.text
            )

        def put(self, url, data, params=None, headers=None, auth=None):
            res = self._session.put(
                url=url,
                data=data,
                params=params,
                headers=headers,
                auth=auth,
                verify=self._check_cert
            )
            return Response(
                url=url,
                method="put",
                headers=res.headers,
                http_code=res.status_code,
                http_text=res.reason,
                body=res.text
            )

        def post(self, url, data, params=None, headers=None, auth=None):
            res = self._session.post(
                url=url,
                data=data,
                params=params,
                headers=headers,
                auth=auth,
                verify=self._check_cert
            )
            return Response(
                url=url,
                method="post",
                headers=res.headers,
                http_code=res.status_code,
                http_text=res.reason,
                body=res.text
            )

        def patch(self, url, data, params=None, headers=None, auth=None):
            res = self._session.patch(
                url=url,
                data=data,
                params=params,
                headers=headers,
                auth=auth,
                verify=self._check_cert
            )
            return Response(
                url=url,
                method="patch",
                headers=res.headers,
                http_code=res.status_code,
                http_text=res.reason,
                body=res.text
            )

        def delete(self, url, data=None, params=None, headers=None, auth=None):
            res = self._session.delete(
                url=url,
                data=data,
                params=params,
                headers=headers,
                auth=auth,
                verify=self._check_cert
            )
            return Response(
                url=url,
                method="delete",
                headers=res.headers,
                http_code=res.status_code,
                http_text=res.reason,
                body=res.text
            )


Then you would inject your HTTP client as shown below:

.. code-block:: python

    from my_module import MyCustomHTTPClient

    from arango import ArangoClient

    client = ArangoClient(
        username='root',
        password='',
        http_client=MyCustomHTTPClient(max_retries=10),
        use_session=True,  # This flag (used in the default client) is now ignored
        check_cert=True    # This flag (used in the default client) is now ignored
    )

Refer to the default HTTP client used by **python-arango** itself for another example
`here <https://github.com/joowani/python-arango/blob/master/arango/http_clients/default.py>`__.