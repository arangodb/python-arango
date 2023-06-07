from dataclasses import dataclass

import pytest
from packaging import version

from arango import ArangoClient, formatter
from arango.database import StandardDatabase
from arango.typings import Json
from tests.executors import TestAsyncApiExecutor, TestTransactionApiExecutor
from tests.helpers import (
    empty_collection,
    generate_col_name,
    generate_db_name,
    generate_graph_name,
    generate_jwt,
    generate_string,
    generate_username,
)


@dataclass
class GlobalData:
    url: str = None
    client: ArangoClient = None
    username: str = None
    password: str = None
    db_name: str = None
    sys_db: StandardDatabase = None
    tst_db: StandardDatabase = None
    bad_db: StandardDatabase = None
    geo_index: Json = None
    col_name: str = None
    icol_name: str = None
    graph_name: str = None
    ecol_name: str = None
    fvcol_name: str = None
    tvcol_name: str = None
    cluster: bool = None
    complete: bool = None
    replication: bool = None
    enterprise: bool = None
    secret: str = None
    root_password: str = None
    db_version: version = version.parse("0.0.0")


global_data = GlobalData()


def pytest_addoption(parser):
    parser.addoption("--host", action="store", default="127.0.0.1")
    parser.addoption("--port", action="store", default="8529")
    parser.addoption("--passwd", action="store", default="passwd")
    parser.addoption("--complete", action="store_true")
    parser.addoption("--cluster", action="store_true")
    parser.addoption("--replication", action="store_true")
    parser.addoption("--enterprise", action="store_true")
    parser.addoption("--secret", action="store", default="secret")


def pytest_configure(config):
    url = f"http://{config.getoption('host')}:{config.getoption('port')}"
    secret = config.getoption("secret")
    client = ArangoClient(hosts=[url, url, url])
    sys_db = client.db(
        name="_system",
        username="root",
        password=config.getoption("passwd"),
        superuser_token=generate_jwt(secret),
    )
    db_version = sys_db.version()

    # Create a user and non-system database for testing.
    username = generate_username()
    password = generate_string()
    tst_db_name = generate_db_name()
    bad_db_name = generate_db_name()
    sys_db.create_database(
        name=tst_db_name,
        users=[
            {
                "active": True,
                "username": username,
                "password": password,
            }
        ],
    )
    tst_db = client.db(tst_db_name, username, password)
    bad_db = client.db(bad_db_name, username, password)

    # Create a standard collection for testing.
    col_name = generate_col_name()
    tst_col = tst_db.create_collection(col_name, edge=False)

    tst_col.add_skiplist_index(["val"])
    tst_col.add_fulltext_index(["text"])
    geo_index = tst_col.add_geo_index(["loc"])

    # Create a legacy edge collection for testing.
    icol_name = generate_col_name()
    tst_db.create_collection(icol_name, edge=True)

    # Create test vertex & edge collections and graph.
    graph_name = generate_graph_name()
    ecol_name = generate_col_name()
    fvcol_name = generate_col_name()
    tvcol_name = generate_col_name()
    tst_graph = tst_db.create_graph(graph_name)
    tst_graph.create_vertex_collection(fvcol_name)
    tst_graph.create_vertex_collection(tvcol_name)
    tst_graph.create_edge_definition(
        edge_collection=ecol_name,
        from_vertex_collections=[fvcol_name],
        to_vertex_collections=[tvcol_name],
    )

    # Update global config
    global_data.url = url
    global_data.client = client
    global_data.username = username
    global_data.password = password
    global_data.db_name = tst_db_name
    global_data.db_version = version.parse(db_version)
    global_data.sys_db = sys_db
    global_data.tst_db = tst_db
    global_data.bad_db = bad_db
    global_data.geo_index = geo_index
    global_data.col_name = col_name
    global_data.icol_name = icol_name
    global_data.graph_name = graph_name
    global_data.ecol_name = ecol_name
    global_data.fvcol_name = fvcol_name
    global_data.tvcol_name = tvcol_name
    global_data.cluster = config.getoption("cluster")
    global_data.complete = config.getoption("complete")
    global_data.replication = config.getoption("replication")
    global_data.enterprise = config.getoption("enterprise")
    global_data.secret = secret
    global_data.root_password = config.getoption("passwd")


# noinspection PyShadowingNames
def pytest_unconfigure(*_):  # pragma: no cover
    sys_db = global_data.sys_db
    if sys_db is None:
        return

    # Remove all test async jobs.
    sys_db.clear_async_jobs()

    # Remove all test tasks.
    for task in sys_db.tasks():
        task_name = task["name"]
        if task_name.startswith("test_task"):
            sys_db.delete_task(task_name, ignore_missing=True)

    # Remove all test users.
    for user in sys_db.users():
        username = user["username"]
        if username.startswith("test_user"):
            sys_db.delete_user(username, ignore_missing=True)

    # Remove all test databases.
    for db_name in sys_db.databases():
        if db_name.startswith("test_database"):
            sys_db.delete_database(db_name, ignore_missing=True)

    # Remove all test collections.
    for collection in sys_db.collections():
        col_name = collection["name"]
        if col_name.startswith("test_collection"):
            sys_db.delete_collection(col_name, ignore_missing=True)

    # # Remove all backups.
    if global_data.enterprise:
        for backup_id in sys_db.backup.get()["list"].keys():
            sys_db.backup.delete(backup_id)

    global_data.client.close()


# noinspection PyProtectedMember
def pytest_generate_tests(metafunc):
    tst_db = global_data.tst_db
    bad_db = global_data.bad_db

    tst_dbs = [tst_db]
    bad_dbs = [bad_db]

    if global_data.complete:
        test = metafunc.module.__name__.split(".test_", 1)[-1]
        tst_conn = tst_db._conn
        bad_conn = bad_db._conn

        if test in {"aql", "collection", "document", "index"}:
            # Add test transaction databases
            tst_txn_db = StandardDatabase(tst_conn)
            tst_txn_db._executor = TestTransactionApiExecutor(tst_conn)
            tst_dbs.append(tst_txn_db)
            bad_txn_db = StandardDatabase(bad_conn)
            bad_txn_db._executor = TestTransactionApiExecutor(bad_conn)
            bad_dbs.append(bad_txn_db)

            # Add test async databases
            tst_async_db = StandardDatabase(tst_conn)
            tst_async_db._executor = TestAsyncApiExecutor(tst_conn)
            tst_dbs.append(tst_async_db)
            bad_async_db = StandardDatabase(bad_conn)
            bad_async_db._executor = TestAsyncApiExecutor(bad_conn)
            bad_dbs.append(bad_async_db)

            # Skip test batch databases, as they are deprecated.
            """
            tst_batch_db = StandardDatabase(tst_conn)
            tst_batch_db._executor = TestBatchExecutor(tst_conn)
            tst_dbs.append(tst_batch_db)
            bad_batch_bdb = StandardDatabase(bad_conn)
            bad_batch_bdb._executor = TestBatchExecutor(bad_conn)
            bad_dbs.append(bad_batch_bdb)
            """

    if "db" in metafunc.fixturenames and "bad_db" in metafunc.fixturenames:
        metafunc.parametrize("db,bad_db", zip(tst_dbs, bad_dbs))

    elif "db" in metafunc.fixturenames:
        metafunc.parametrize("db", tst_dbs)

    elif "bad_db" in metafunc.fixturenames:
        metafunc.parametrize("bad_db", bad_dbs)


@pytest.fixture(autouse=True)
def mock_formatters(monkeypatch):
    def mock_verify_format(body, result):
        body.pop("error", None)
        body.pop("code", None)
        result.pop("edge", None)

        # Remove all None values
        # Sometimes they are expected to be excluded from the body (see computedValues)
        result = {k: v for k, v in result.items() if v is not None}
        body = {k: v for k, v in body.items() if v is not None}

        if len(body) != len(result):
            before = sorted(body, key=lambda x: x.strip("_"))
            after = sorted(result, key=lambda x: x.strip("_"))
            raise ValueError(f"\nIN: {before}\nOUT: {after}")
        return result

    monkeypatch.setattr(formatter, "verify_format", mock_verify_format)


@pytest.fixture(autouse=False)
def db_version():
    return global_data.db_version


@pytest.fixture(autouse=False)
def url():
    return global_data.url


@pytest.fixture(autouse=False)
def client():
    return global_data.client


@pytest.fixture(autouse=False)
def db_name():
    return global_data.db_name


@pytest.fixture(autouse=False)
def sys_db():
    return global_data.sys_db


@pytest.fixture(autouse=False)
def username():
    return global_data.username


@pytest.fixture(autouse=False)
def password():
    return global_data.password


@pytest.fixture(autouse=False)
def root_password():
    return global_data.root_password


@pytest.fixture(autouse=False)
def conn(db):
    return getattr(db, "_conn")


@pytest.fixture(autouse=False)
def col(db):
    collection = db.collection(global_data.col_name)
    empty_collection(collection)
    return collection


@pytest.fixture(autouse=False)
def bad_col(bad_db):
    return bad_db.collection(global_data.col_name)


@pytest.fixture(autouse=False)
def geo():
    return global_data.geo_index


@pytest.fixture(autouse=False)
def icol(db):
    collection = db.collection(global_data.icol_name)
    empty_collection(collection)
    return collection


@pytest.fixture(autouse=False)
def graph(db):
    return db.graph(global_data.graph_name)


@pytest.fixture(autouse=False)
def bad_graph(bad_db):
    return bad_db.graph(global_data.graph_name)


# noinspection PyShadowingNames
@pytest.fixture(autouse=False)
def fvcol(graph):
    collection = graph.vertex_collection(global_data.fvcol_name)
    empty_collection(collection)
    return collection


# noinspection PyShadowingNames
@pytest.fixture(autouse=False)
def tvcol(graph):
    collection = graph.vertex_collection(global_data.tvcol_name)
    empty_collection(collection)
    return collection


# noinspection PyShadowingNames
@pytest.fixture(autouse=False)
def bad_fvcol(bad_graph):
    return bad_graph.vertex_collection(global_data.fvcol_name)


# noinspection PyShadowingNames
@pytest.fixture(autouse=False)
def ecol(graph):
    collection = graph.edge_collection(global_data.ecol_name)
    empty_collection(collection)
    return collection


# noinspection PyShadowingNames
@pytest.fixture(autouse=False)
def bad_ecol(bad_graph):
    return bad_graph.edge_collection(global_data.ecol_name)


@pytest.fixture(autouse=False)
def docs():
    return [
        {"_key": "1", "val": 1, "text": "foo", "loc": [1, 1]},
        {"_key": "2", "val": 2, "text": "foo", "loc": [2, 2]},
        {"_key": "3", "val": 3, "text": "foo", "loc": [3, 3]},
        {"_key": "4", "val": 4, "text": "bar", "loc": [4, 4]},
        {"_key": "5", "val": 5, "text": "bar", "loc": [5, 5]},
        {"_key": "6", "val": 6, "text": "bar", "loc": [5, 5]},
    ]


@pytest.fixture(autouse=False)
def fvdocs():
    return [
        {"_key": "1", "val": 1},
        {"_key": "2", "val": 2},
        {"_key": "3", "val": 3},
    ]


@pytest.fixture(autouse=False)
def tvdocs():
    return [
        {"_key": "4", "val": 4},
        {"_key": "5", "val": 5},
        {"_key": "6", "val": 6},
    ]


@pytest.fixture(autouse=False)
def edocs():
    fv = global_data.fvcol_name
    tv = global_data.tvcol_name
    return [
        {"_key": "1", "_from": f"{fv}/1", "_to": f"{tv}/4"},
        {"_key": "2", "_from": f"{fv}/1", "_to": f"{tv}/5"},
        {"_key": "3", "_from": f"{fv}/6", "_to": f"{tv}/2"},
        {"_key": "4", "_from": f"{fv}/8", "_to": f"{tv}/7"},
    ]


@pytest.fixture(autouse=False)
def cluster():
    return global_data.cluster


@pytest.fixture(autouse=False)
def replication():
    return global_data.replication


@pytest.fixture(autouse=False)
def enterprise():
    return global_data.enterprise


@pytest.fixture(autouse=False)
def secret():
    return global_data.secret
