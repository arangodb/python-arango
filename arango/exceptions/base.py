from __future__ import absolute_import, unicode_literals

from six import string_types as string

from arango.responses import BaseResponse


class ArangoError(Exception):
    """Base class for all ArangoDB exceptions.

    :param data: the response object or string
    :type data: arango.response.Response | str | unicode
    """

    def __init__(self, data, message=None):
        if isinstance(data, BaseResponse):
            # Get the ArangoDB error message if provided
            if message is not None:
                error_message = message
            elif data.error_message is not None:
                error_message = data.error_message
            elif data.status_text is not None:
                error_message = data.status_text
            else:  # pragma: no cover
                error_message = "request failed"

            # Get the ArangoDB error number if provided
            self.error_code = data.error_code

            # Build the error message for the exception
            if self.error_code is None:
                error_message = '[HTTP {}] {}'.format(
                    data.status_code,
                    error_message
                )
            else:
                error_message = '[HTTP {}][ERR {}] {}'.format(
                    data.status_code,
                    self.error_code,
                    error_message
                )
            # Generate the error message for the exception
            super(ArangoError, self).__init__(error_message)
            self.message = error_message
            self.http_method = data.method
            self.url = data.url
            self.http_code = data.status_code
            self.http_headers = data.headers
        elif isinstance(data, string):
            super(ArangoError, self).__init__(data)
            self.message = data
            self.error_code = None
            self.url = None
            self.http_method = None
            self.http_code = None
            self.http_headers = None
