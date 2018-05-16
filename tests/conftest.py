from __future__ import absolute_import, unicode_literals, division

import pytest

from arango import ArangoClient
from arango.database import StandardDatabase
from tests.helpers import (
    generate_db_name,
    generate_col_name,
    generate_string,
    generate_username,
    generate_graph_name,
)
from tests.executors import (
    TestAsyncExecutor,
    TestBatchExecutor,
    TestTransactionExecutor
)

print('Setting up test ArangoDB client ...')
_client = ArangoClient()
_sys_db = _client.db('_system', 'root', 'passwd')

print('Setting up test databases ...')
_db_name = generate_db_name()
_username = generate_username()
_password = generate_string()
_db_users = [{
    'username': _username,
    'password': _password,
    'active': True
}]
_sys_db.create_database(_db_name, _db_users)
_db = _client.db(_db_name, _username, _password)
_bad_db_name = generate_db_name()
_bad_db = _client.db(_bad_db_name, '', '')

print('Setting up test collections ...')
_col_name = generate_col_name()
_col = _db.create_collection(_col_name)
_skiplist_index = _col.add_skiplist_index(['val'])
_fulltext_index = _col.add_fulltext_index(['text'])
_geo_index = _col.add_geo_index(['loc'])
_bad_col = _bad_db.collection(_col_name)
_lecol_name = generate_col_name()
_lecol = _db.create_collection(_lecol_name, edge=True)

print('Setting up test graphs ...')
_graph_name = generate_graph_name()
_graph = _db.create_graph(_graph_name)
_bad_graph = _bad_db.graph(_graph_name)

print('Setting up test "_from" vertex collections ...')
_fvcol_name = generate_col_name()
_fvcol = _graph.create_vertex_collection(_fvcol_name)
_bad_fvcol = _bad_graph.vertex_collection(_fvcol_name)

print('Setting up test "_to" vertex collections ...')
_tvcol_name = generate_col_name()
_tvcol = _graph.create_vertex_collection(_tvcol_name)
_bad_tvcol = _bad_graph.vertex_collection(_tvcol_name)

print('Setting up test edge collection and definition ...')
_ecol_name = generate_col_name()
_ecol = _graph.create_edge_definition(
    edge_collection=_ecol_name,
    from_vertex_collections=[_fvcol_name],
    to_vertex_collections=[_tvcol_name]
)
_bad_ecol = _bad_graph.edge_collection(_ecol_name)

print('Setting up test documents ...')
_docs = [
    {'_key': '1', 'val': 1, 'text': 'foo', 'loc': [1, 1]},
    {'_key': '2', 'val': 2, 'text': 'foo', 'loc': [2, 2]},
    {'_key': '3', 'val': 3, 'text': 'foo', 'loc': [3, 3]},
    {'_key': '4', 'val': 4, 'text': 'bar', 'loc': [4, 4]},
    {'_key': '5', 'val': 5, 'text': 'bar', 'loc': [5, 5]},
    {'_key': '6', 'val': 6, 'text': 'bar', 'loc': [5, 5]},
]

print('Setting up test "_from" vertex documents ...')
_fvdocs = [
    {'_key': '1', 'val': 1},
    {'_key': '2', 'val': 2},
    {'_key': '3', 'val': 3},
]

print('Setting up test "_to" vertex documents ...')
_tvdocs = [
    {'_key': '4', 'val': 4},
    {'_key': '5', 'val': 5},
    {'_key': '6', 'val': 6},
]

print('Setting up test edge documents ...')
_edocs = [
    {
        '_key': '1',
        '_from': '{}/1'.format(_fvcol_name),
        '_to': '{}/4'.format(_tvcol_name)
    },
    {
        '_key': '2',
        '_from': '{}/1'.format(_fvcol_name),
        '_to': '{}/5'.format(_tvcol_name)
    },
    {
        '_key': '3',
        '_from': '{}/6'.format(_fvcol_name),
        '_to': '{}/2'.format(_tvcol_name)
    },
    {
        '_key': '4',
        '_from': '{}/8'.format(_fvcol_name),
        '_to': '{}/7'.format(_tvcol_name)
    },
]


@pytest.fixture(autouse=False)
def client():
    return _client


@pytest.fixture(autouse=False)
def url():
    return _client.base_url


@pytest.fixture(autouse=False)
def username():
    return _username


@pytest.fixture(autouse=False)
def password():
    return _password


@pytest.fixture(autouse=False)
def sys_db():
    return _sys_db


@pytest.fixture(autouse=False)
def col(db):
    collection = db.collection(_col_name)
    collection.truncate()
    return collection


@pytest.fixture(autouse=False)
def lecol(db):
    collection = db.collection(_lecol_name)
    collection.truncate()
    return collection


@pytest.fixture(autouse=False)
def bad_col(bad_db):
    return bad_db.collection(_col_name)


@pytest.fixture(autouse=False)
def graph(db):
    return db.graph(_graph_name)


@pytest.fixture(autouse=False)
def bad_graph(bad_db):
    return bad_db.graph(_graph_name)


@pytest.fixture(autouse=False)
def fvcol():
    _fvcol.truncate()
    return _fvcol


@pytest.fixture(autouse=False)
def bad_fvcol():
    return _bad_fvcol


@pytest.fixture(autouse=False)
def tvcol():
    _tvcol.truncate()
    return _tvcol


@pytest.fixture(autouse=False)
def ecol():
    return _ecol


@pytest.fixture(autouse=False)
def bad_ecol():
    return _bad_ecol


@pytest.fixture(autouse=False)
def docs():
    return [doc.copy() for doc in _docs]


@pytest.fixture(autouse=False)
def fvdocs():
    return [doc.copy() for doc in _fvdocs]


@pytest.fixture(autouse=False)
def tvdocs():
    return [doc.copy() for doc in _tvdocs]


@pytest.fixture(autouse=False)
def edocs():
    return [doc.copy() for doc in _edocs]


@pytest.fixture(autouse=False)
def geo():
    return _geo_index


def pytest_addoption(parser):
    parser.addoption("--complete", action="store_true")


# noinspection PyProtectedMember
def pytest_generate_tests(metafunc):
    test_name = metafunc.module.__name__.split('.test_', 1)[-1]

    dbs = [_db]
    bad_dbs = [_bad_db]

    if metafunc.config.getoption('complete'):

        if test_name in {'collection', 'document', 'graph', 'aql', 'index'}:
            # Add test transaction databases
            tdb = StandardDatabase(_db._conn)
            tdb._executor = TestTransactionExecutor(_db._conn)
            tdb._is_transaction = True
            dbs.append(tdb)

            bad_tdb = StandardDatabase(_bad_db._conn)
            bad_tdb._executor = TestTransactionExecutor(_bad_db._conn)
            bad_dbs.append(bad_tdb)

        if test_name not in {
            'async', 'batch', 'transaction', 'client', 'exception'
        }:
            # Add test async databases
            adb = StandardDatabase(_db._conn)
            adb._executor = TestAsyncExecutor(_db._conn)
            dbs.append(adb)

            bad_adb = StandardDatabase(_bad_db._conn)
            bad_adb._executor = TestAsyncExecutor(_bad_db._conn)
            bad_dbs.append(bad_adb)

            # Add test batch databases
            bdb = StandardDatabase(_db._conn)
            bdb._executor = TestBatchExecutor(_db._conn)
            dbs.append(bdb)

            bad_bdb = StandardDatabase(_bad_db._conn)
            bad_bdb._executor = TestBatchExecutor(_bad_db._conn)
            bad_dbs.append(bad_bdb)

    if 'db' in metafunc.fixturenames and 'bad_db' in metafunc.fixturenames:
        metafunc.parametrize('db,bad_db', zip(dbs, bad_dbs))
    elif 'db' in metafunc.fixturenames:
        metafunc.parametrize('db', dbs)
    elif 'bad_db' in metafunc.fixturenames:
        metafunc.parametrize('bad_db', bad_dbs)


def pytest_unconfigure(*_):  # pragma: no cover
    # Remove all test async jobs.
    _sys_db.clear_async_jobs()

    # Remove all test databases.
    for database in _sys_db.databases():
        if database.startswith('test_database'):
            _sys_db.delete_database(database)

    # Remove all test collections
    for collection in _sys_db.collections():
        if collection['name'].startswith('test_collection'):
            _sys_db.delete_collection(collection)

    # Remove all test tasks
    for task in _sys_db.tasks():
        if task['name'].startswith('test_task'):
            _sys_db.delete_task(task['id'], ignore_missing=True)

    # Remove all test users
    for user in _sys_db.users():
        if user['username'].startswith('test_user'):
            _sys_db.delete_user(user['username'], ignore_missing=True)
