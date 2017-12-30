from __future__ import absolute_import, unicode_literals

import pytest

from arango import ArangoClient
from arango.aql import AQL
from arango.exceptions import (
    AsyncExecuteError,
    BatchExecuteError,
    ArangoError,
    AQLCacheClearError,
    AQLCacheConfigureError,
    AQLCachePropertiesError,
    AQLFunctionCreateError,
    AQLFunctionDeleteError,
    AQLFunctionListError,
    AQLQueryExecuteError,
    AQLQueryExplainError,
    AQLQueryValidateError
)

from tests.utils import (
    generate_db_name,
    generate_col_name,
    generate_user_name
)

arango_client = ArangoClient()

db_name = generate_db_name()
db = arango_client.create_database(db_name)
col_name = generate_col_name()
db.create_collection(col_name)
username = generate_user_name()
user = arango_client.create_user(username, 'password')
func_name = ''
func_body = ''


def teardown_module(*_):
    arango_client.delete_database(db_name, ignore_missing=True)
    arango_client.delete_user(username, ignore_missing=True)


@pytest.mark.order1
def test_init():
    assert isinstance(db.aql, AQL)
    assert 'ArangoDB AQL' in repr(db.aql)


@pytest.mark.order2
def test_query_explain():
    fields_to_check = [
        'estimatedNrItems',
        'estimatedCost',
        'rules',
        'variables',
        'collections',
    ]

    # Test invalid query
    with pytest.raises(AQLQueryExplainError):
        db.aql.explain('THIS IS AN INVALID QUERY')

    # Test valid query (all_plans=True)
    plans = db.aql.explain(
        'FOR d IN {} RETURN d'.format(col_name),
        all_plans=True,
        opt_rules=['-all', '+use-index-range'],
        max_plans=10
    )
    for plan in plans:
        for field in fields_to_check:
            assert field in plan

    # Test valid query (all_plans=False)
    plan = db.aql.explain(
        'FOR d IN {} RETURN d'.format(col_name),
        all_plans=False,
        opt_rules=['-all', '+use-index-range']
    )
    for field in fields_to_check:
        assert field in plan


@pytest.mark.order3
def test_query_validate():
    # Test invalid query
    with pytest.raises(AQLQueryValidateError):
        db.aql.validate('THIS IS AN INVALID QUERY')

    # Test valid query
    result = db.aql.validate('FOR d IN {} RETURN d'.format(col_name))
    assert 'ast' in result
    assert 'bindVars' in result
    assert 'collections' in result
    assert 'parsed' in result


@pytest.mark.order4
def test_query_execute():
    # Test invalid AQL query
    with pytest.raises(AQLQueryExecuteError):
        db.aql.execute('THIS IS AN INVALID QUERY')

    # Test valid AQL query #1
    db.collection(col_name).import_bulk([
        {'_key': 'doc01'},
        {'_key': 'doc02'},
        {'_key': 'doc03'},
    ])
    result = db.aql.execute(
        'FOR d IN {} RETURN d'.format(col_name),
        count=True,
        batch_size=1,
        ttl=10,
        optimizer_rules=['+all']
    )
    assert set(d['_key'] for d in result) == {'doc01', 'doc02', 'doc03'}

    # Test valid AQL query #2
    db.collection(col_name).import_bulk([
        {'_key': 'doc04', 'value': 1},
        {'_key': 'doc05', 'value': 1},
        {'_key': 'doc06', 'value': 3},
    ])
    result = db.aql.execute(
        'FOR d IN {} FILTER d.value == @value RETURN d'.format(col_name),
        bind_vars={'value': 1},
        count=True,
        full_count=True,
        max_plans=100
    )
    assert set(d['_key'] for d in result) == {'doc04', 'doc05'}


@pytest.mark.order5
def test_query_function_create_and_list():
    global func_name, func_body

    assert db.aql.functions() == {}
    func_name = 'myfunctions::temperature::celsiustofahrenheit'
    func_body = 'function (celsius) { return celsius * 1.8 + 32; }'

    # Test create AQL function
    db.aql.create_function(func_name, func_body)
    assert db.aql.functions() == {func_name: func_body}

    # Test create AQL function again (idempotency)
    db.aql.create_function(func_name, func_body)
    assert db.aql.functions() == {func_name: func_body}

    # Test create invalid AQL function
    func_body = 'function (celsius) { invalid syntax }'
    with pytest.raises(AQLFunctionCreateError):
        result = db.aql.create_function(func_name, func_body)
        assert result is True


@pytest.mark.order6
def test_query_function_delete_and_list():
    # Test delete AQL function
    result = db.aql.delete_function(func_name)
    assert result is True

    # Test delete missing AQL function
    with pytest.raises(AQLFunctionDeleteError):
        db.aql.delete_function(func_name)

    # Test delete missing AQL function (ignore_missing)
    result = db.aql.delete_function(func_name, ignore_missing=True)
    assert result is False
    assert db.aql.functions() == {}


@pytest.mark.order7
def test_get_query_cache_properties():
    properties = db.aql.cache.properties()
    assert 'mode' in properties
    assert 'limit' in properties


@pytest.mark.order8
def test_set_query_cache_properties():
    properties = db.aql.cache.configure(
        mode='on', limit=100
    )
    assert properties['mode'] == 'on'
    assert properties['limit'] == 100

    properties = db.aql.cache.properties()
    assert properties['mode'] == 'on'
    assert properties['limit'] == 100


@pytest.mark.order9
def test_clear_query_cache():
    result = db.aql.cache.clear()
    assert isinstance(result, bool)


@pytest.mark.order10
def test_aql_errors():
    bad_db_name = generate_db_name()
    bad_aql = arango_client.database(bad_db_name).aql

    with pytest.raises(ArangoError) as err:
        bad_aql.functions()
    assert isinstance(err.value, AQLFunctionListError) \
        or isinstance(err.value, AsyncExecuteError) \
        or isinstance(err.value, BatchExecuteError)

    with pytest.raises(ArangoError) as err:
        bad_aql.cache.properties()
    assert isinstance(err.value, AQLCachePropertiesError) \
        or isinstance(err.value, AsyncExecuteError) \
        or isinstance(err.value, BatchExecuteError)

    with pytest.raises(ArangoError) as err:
        bad_aql.cache.configure(mode='on')
    assert isinstance(err.value, AQLCacheConfigureError) \
        or isinstance(err.value, AsyncExecuteError) \
        or isinstance(err.value, BatchExecuteError)

    with pytest.raises(ArangoError) as err:
        bad_aql.cache.clear()
    assert isinstance(err.value, AQLCacheClearError) \
        or isinstance(err.value, AsyncExecuteError) \
        or isinstance(err.value, BatchExecuteError)
