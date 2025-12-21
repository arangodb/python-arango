import time
from collections import deque
from uuid import uuid4

import jwt
import pytest

from arango.cursor import Cursor
from arango.exceptions import AsyncExecuteError, TransactionInitError


def generate_db_name():
    """Generate and return a random database name.

    :return: Random database name.
    :rtype: str
    """
    return f"test_database_{uuid4().hex}"


def generate_col_name():
    """Generate and return a random collection name.

    :return: Random collection name.
    :rtype: str
    """
    return f"test_collection_{uuid4().hex}"


def generate_graph_name():
    """Generate and return a random graph name.

    :return: Random graph name.
    :rtype: str
    """
    return f"test_graph_{uuid4().hex}"


def generate_doc_key():
    """Generate and return a random document key.

    :return: Random document key.
    :rtype: str
    """
    return f"test_document_{uuid4().hex}"


def generate_task_name():
    """Generate and return a random task name.

    :return: Random task name.
    :rtype: str
    """
    return f"test_task_{uuid4().hex}"


def generate_task_id():
    """Generate and return a random task ID.

    :return: Random task ID
    :rtype: str
    """
    return f"test_task_id_{uuid4().hex}"


def generate_username():
    """Generate and return a random username.

    :return: Random username.
    :rtype: str
    """
    return f"test_user_{uuid4().hex}"


def generate_view_name():
    """Generate and return a random view name.

    :return: Random view name.
    :rtype: str
    """
    return f"test_view_{uuid4().hex}"


def generate_analyzer_name():
    """Generate and return a random analyzer name.

    :return: Random analyzer name.
    :rtype: str
    """
    return f"test_analyzer_{uuid4().hex}"


def generate_string():
    """Generate and return a random unique string.

    :return: Random unique string.
    :rtype: str
    """
    return uuid4().hex


def generate_service_mount():
    """Generate and return a random service name.

    :return: Random service name.
    :rtype: str
    """
    return f"/test_{uuid4().hex}"


def generate_token_name():
    """Generate and return a random token name.

    :return: Random token name.
    :rtype: str
    """
    return f"test_token_{uuid4().hex}"


def generate_jwt(secret, exp=3600):
    """Generate and return a JWT.

    :param secret: JWT secret
    :type secret: str
    :param exp: Time to expire in seconds.
    :type exp: int
    :return: JWT
    :rtype: str
    """
    now = int(time.time())
    return jwt.encode(
        payload={
            "iat": now,
            "exp": now + exp,
            "iss": "arangodb",
            "server_id": "client",
        },
        key=secret,
    )


def clean_doc(obj):
    """Return the document(s) with all extra system keys stripped.

    :param obj: document(s)
    :type obj: list | dict | arango.cursor.Cursor
    :return: Document(s) with the system keys stripped
    :rtype: list | dict
    """
    if isinstance(obj, (Cursor, list, deque)):
        docs = [clean_doc(d) for d in obj]
        return sorted(docs, key=lambda doc: doc["_key"])

    if isinstance(obj, dict):
        return {
            field: value
            for field, value in obj.items()
            if field in {"_key", "_from", "_to"} or not field.startswith("_")
        }


def empty_collection(collection):
    """Empty all the documents in the collection.

    :param collection: Collection name
    :type collection: arango.collection.StandardCollection |
        arango.collection.VertexCollection | arango.collection.EdgeCollection
    """
    for doc_id in collection.ids():
        collection.delete(doc_id, sync=True)


def extract(key, items):
    """Return the sorted values from dicts using the given key.

    :param key: Dictionary key
    :type key: str
    :param items: Items to filter.
    :type items: [dict]
    :return: Set of values.
    :rtype: [str]
    """
    return sorted(item[key] for item in items)


def assert_raises(*exc):
    """Assert that the given exception is raised.

    :param exc: Expected exception(s).
    :type: exc
    """
    return pytest.raises(exc + (AsyncExecuteError, TransactionInitError))
