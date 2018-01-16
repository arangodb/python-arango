from __future__ import absolute_import, unicode_literals

from uuid import uuid4


def arango_version(client):
    """Return the major and minor version of ArangoDB.

    :param client: The ArangoDB client.
    :type client: arango.ArangoClient
    :return: The major and minor version numbers.
    :rtype: (int, int)
    """
    version_nums = client.version().split('.')
    return map(int, version_nums[:2])


def generate_db_name():
    """Generate and return a random database name.

    :returns: A random database name.
    :rtype: str | unicode
    """
    return 'test_database_{}'.format(uuid4().hex)


def generate_col_name():
    """Generate and return a random collection name.

    :returns: A random collection name.
    :rtype: str | unicode
    """
    return 'test_collection_{}'.format(uuid4().hex)


def generate_graph_name():
    """Generate and return a random graph name.

    :returns: A random graph name.
    :rtype: str | unicode
    """
    return 'test_graph_{}'.format(uuid4().hex)


def generate_task_name():
    """Generate and return a random task name.

    :returns: A random task name.
    :rtype: str | unicode
    """
    return 'test_task_{}'.format(uuid4().hex)


def generate_task_id():
    """Generate and return a random task ID.

    :returns: A random task ID
    :rtype: str | unicode
    """
    return 'test_task_id_{}'.format(uuid4().hex)


def generate_user_name():
    """Generate and return a random username.

    :returns: A random username.
    :rtype: str | unicode
    """
    return 'test_user_{}'.format(uuid4().hex)


def clean_keys(obj):
    """Return the document(s) with all the system keys stripped.

    :param obj: document(s)
    :type obj: list |dict | object
    :returns: the document(s) with the system keys stripped
    :rtype: list | dict |object
    """
    if isinstance(obj, dict):
        return {
            k: v for k, v in obj.items()
            if not (k not in {'_key', '_from', '_to'} and k.startswith('_'))
        }
    else:
        return [{
            k: v for k, v in document.items()
            if not (k not in {'_key', '_from', '_to'} and k.startswith('_'))
        } for document in obj]


def ordered(documents):
    """Sort the list of the documents by keys and return the list.

    :param documents: the list of documents to order
    :type documents: [dict]
    :returns: the ordered list of documents
    :rtype: [dict]
    """
    return sorted(documents, key=lambda doc: doc['_key'])
