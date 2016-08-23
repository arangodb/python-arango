from __future__ import absolute_import, unicode_literals

from random import randint


def generate_db_name(client, exclude=None):
    """Generate and return the next available database name.

    :param client: ArangoDB client
    :type client: arango.ArangoClient
    :param exclude: set of names to exclude
    :type exclude: set
    :returns: the next available database name
    :rtype: str
    """
    num = randint(100000, 999999)
    existing = set(client.databases())
    if exclude is not None:
        existing |= set(exclude)
    while 'test_database_{num:06d}'.format(num=num) in existing:
        num = randint(100000, 999999)
    return 'test_database_{num:06d}'.format(num=num)


def generate_col_name(database, exclude=None):
    """Generate and return the next available collection name.

    :param database: ArangoDB database
    :type database: arango.database.ArangoDatabase
    :param exclude: set of names to exclude
    :type exclude: set
    :returns: the next available collection name
    :rtype: str
    """
    num = randint(100000, 999999)
    existing = set(col['name'] for col in database.collections())
    if exclude is not None:
        existing |= set(exclude)
    while 'test_collection_{num:06d}'.format(num=num) in existing:
        num = randint(100000, 999999)
    return 'test_collection_{num:06d}'.format(num=num)


def generate_graph_name(database, exclude=None):
    """Generate and return the next available collection name.

    :param database: ArangoDB database
    :type database: arango.database.ArangoDatabase
    :param exclude: set of names to exclude
    :type exclude: set
    :returns: the next available graph name
    :rtype: str
    """
    num = randint(100000, 999999)
    existing = set(g['name'] for g in database.graphs())
    if exclude is not None:
        existing |= set(exclude)
    while 'test_graph_{num:06d}'.format(num=num) in existing:
        num = randint(100000, 999999)
    return 'test_graph_{num:06d}'.format(num=num)


def generate_task_name(database, exclude=None):
    """Generate and return the next available task name.

    :param database: ArangoDB database
    :type database: arango.database.ArangoDatabase
    :param exclude: set of names to exclude
    :type exclude: set
    :returns: the next available task name
    :rtype: str
    """
    num = randint(100000, 999999)
    existing = set(task['name'] for task in database.tasks())
    if exclude is not None:
        existing |= set(exclude)
    while 'test_task_{num:06d}'.format(num=num) in existing:
        num = randint(100000, 999999)
    return 'test_task_{num:06d}'.format(num=num)


def generate_task_id(database, exclude=None):
    """Generate and return the next available task ID.

    :param database: ArangoDB database
    :type database: arango.database.ArangoDatabase
    :param exclude: set of names to exclude
    :type exclude: set
    :returns: the next available task ID
    :rtype: str
    """
    num = randint(100000, 999999)
    existing = set(task['id'] for task in database.tasks())
    if exclude is not None:
        existing |= set(exclude)
    while 'test_task_id_{num:06d}'.format(num=num) in existing:
        num = randint(100000, 999999)
    return 'test_task_id_{num:06d}'.format(num=num)


def generate_user_name(client, exclude=None):
    """Generate and return the next available user name.

    :param client: ArangoDB client
    :type client: arango.ArangoClient
    :param exclude: set of names to exclude
    :type exclude: set
    :returns: the next available database name
    :rtype: str
    """
    num = randint(100000, 999999)
    existing = set(user['username'] for user in client.users())
    if exclude is not None:
        existing |= set(exclude)
    while 'test_user_{num:06d}'.format(num=num) in existing:
        num = randint(100000, 999999)
    return 'test_user_{num:06d}'.format(num=num)


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
