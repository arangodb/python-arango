from __future__ import absolute_import, unicode_literals

import pytest

from arango import ArangoClient
from arango.exceptions import (
    CursorNextError,
    CursorCloseError
)

from tests.utils import (
    generate_db_name,
    generate_col_name,
    clean_keys
)

arango_client = ArangoClient()
db_name = generate_db_name()
db = arango_client.create_database(db_name)
col_name = generate_col_name()
col = db.create_collection(col_name)

cursor = None
cursor_id = None
doc1 = {'_key': '1'}
doc2 = {'_key': '2'}
doc3 = {'_key': '3'}
doc4 = {'_key': '4'}


def teardown_module(*_):
    arango_client.delete_database(db_name, ignore_missing=True)


@pytest.mark.order1
def test_read_cursor_init():
    global cursor, cursor_id

    col.import_bulk([doc1, doc2, doc3, doc4])
    cursor = db.aql.execute(
        'FOR d IN {} RETURN d'.format(col_name),
        count=True,
        batch_size=2,
        ttl=1000,
        optimizer_rules=['+all']
    )
    cursor_id = cursor.id
    assert 'ArangoDB cursor' in repr(cursor)
    assert cursor.has_more() is True
    assert cursor.cached() is False
    assert cursor.statistics()['modified'] == 0
    assert cursor.statistics()['filtered'] == 0
    assert cursor.statistics()['ignored'] == 0
    assert cursor.statistics()['scanned_full'] == 4
    assert cursor.statistics()['scanned_index'] == 0
    assert cursor.warnings() == []
    assert cursor.count() == 4
    assert clean_keys(cursor.batch()) == [doc1, doc2]
    assert isinstance(cursor.statistics()['execution_time'], (int, float))


@pytest.mark.order2
def test_read_cursor_first():
    assert clean_keys(cursor.next()) == doc1
    assert cursor.id == cursor_id
    assert cursor.has_more() is True
    assert cursor.cached() is False
    assert cursor.statistics()['modified'] == 0
    assert cursor.statistics()['filtered'] == 0
    assert cursor.statistics()['ignored'] == 0
    assert cursor.statistics()['scanned_full'] == 4
    assert cursor.statistics()['scanned_index'] == 0
    assert cursor.warnings() == []
    assert cursor.count() == 4
    assert clean_keys(cursor.batch()) == [doc2]
    assert isinstance(cursor.statistics()['execution_time'], (int, float))


@pytest.mark.order3
def test_read_cursor_second():
    clean_keys(cursor.next()) == doc2
    assert cursor.id == cursor_id
    assert cursor.has_more() is True
    assert cursor.cached() is False
    assert cursor.statistics()['modified'] == 0
    assert cursor.statistics()['filtered'] == 0
    assert cursor.statistics()['ignored'] == 0
    assert cursor.statistics()['scanned_full'] == 4
    assert cursor.statistics()['scanned_index'] == 0
    assert cursor.warnings() == []
    assert cursor.count() == 4
    assert clean_keys(cursor.batch()) == []
    assert isinstance(cursor.statistics()['execution_time'], (int, float))


@pytest.mark.order4
def test_read_cursor_third():
    clean_keys(cursor.next()) == doc3
    assert cursor.id is None
    assert cursor.has_more() is False
    assert cursor.cached() is False
    assert cursor.statistics()['modified'] == 0
    assert cursor.statistics()['filtered'] == 0
    assert cursor.statistics()['ignored'] == 0
    assert cursor.statistics()['scanned_full'] == 4
    assert cursor.statistics()['scanned_index'] == 0
    assert cursor.warnings() == []
    assert cursor.count() == 4
    assert clean_keys(cursor.batch()) == [doc3]
    assert isinstance(cursor.statistics()['execution_time'], (int, float))


@pytest.mark.order5
def test_read_cursor_finish():
    clean_keys(cursor.next()) == doc4
    assert cursor.id is None
    assert cursor.has_more() is False
    assert cursor.cached() is False
    assert cursor.statistics()['modified'] == 0
    assert cursor.statistics()['filtered'] == 0
    assert cursor.statistics()['ignored'] == 0
    assert cursor.statistics()['scanned_full'] == 4
    assert cursor.statistics()['scanned_index'] == 0
    assert cursor.warnings() == []
    assert cursor.count() == 4
    assert clean_keys(cursor.batch()) == []
    assert isinstance(cursor.statistics()['execution_time'], (int, float))
    with pytest.raises(StopIteration):
        cursor.next()
    assert cursor.close(ignore_missing=True) is False

    incorrect_cursor_data = {'id': 'invalid', 'hasMore': True, 'result': []}
    setattr(cursor, '_data', incorrect_cursor_data)
    with pytest.raises(CursorCloseError):
        cursor.close(ignore_missing=False)
    with pytest.raises(CursorNextError):
        cursor.next()


@pytest.mark.order6
def test_read_cursor_early_finish():
    global cursor, cursor_id

    col.truncate()
    col.import_bulk([doc1, doc2, doc3, doc4])
    cursor = db.aql.execute(
        'FOR d IN {} RETURN d'.format(col_name),
        count=True,
        batch_size=2,
        ttl=1000,
        optimizer_rules=['+all']
    )
    assert cursor.close() is True
    with pytest.raises(CursorCloseError):
        cursor.close(ignore_missing=False)

    assert clean_keys(cursor.batch()) == [doc1, doc2]


@pytest.mark.order7
def test_write_cursor_init():
    global cursor, cursor_id
    col.truncate()
    col.import_bulk([doc1, doc2, doc3])
    cursor = db.aql.execute(
        '''
        FOR d IN {col} FILTER d._key == @first OR d._key == @second
        UPDATE {{_key: d._key, _val: @val }} IN {col}
        RETURN NEW
        '''.format(col=col_name),
        bind_vars={'first': '1', 'second': '2', 'val': 42},
        count=True,
        batch_size=1,
        ttl=1000,
        optimizer_rules=['+all']
    )
    cursor_id = cursor.id
    assert cursor.has_more() is True
    assert cursor.cached() is False
    assert cursor.statistics()['modified'] == 2
    assert cursor.statistics()['filtered'] == 0
    assert cursor.statistics()['ignored'] == 0
    assert cursor.statistics()['scanned_full'] == 0
    assert cursor.statistics()['scanned_index'] == 2
    assert cursor.warnings() == []
    assert cursor.count() == 2
    assert clean_keys(cursor.batch()) == [doc1]
    assert isinstance(cursor.statistics()['execution_time'], (int, float))


@pytest.mark.order8
def test_write_cursor_first():
    assert clean_keys(cursor.next()) == doc1
    assert cursor.id == cursor_id
    assert cursor.has_more() is True
    assert cursor.cached() is False
    assert cursor.statistics()['modified'] == 2
    assert cursor.statistics()['filtered'] == 0
    assert cursor.statistics()['ignored'] == 0
    assert cursor.statistics()['scanned_full'] == 0
    assert cursor.statistics()['scanned_index'] == 2
    assert cursor.warnings() == []
    assert cursor.count() == 2
    assert clean_keys(cursor.batch()) == []
    assert isinstance(cursor.statistics()['execution_time'], (int, float))


@pytest.mark.order9
def test_write_cursor_second():
    clean_keys(cursor.next()) == doc2
    assert cursor.id is None
    assert cursor.has_more() is False
    assert cursor.cached() is False
    assert cursor.statistics()['modified'] == 2
    assert cursor.statistics()['filtered'] == 0
    assert cursor.statistics()['ignored'] == 0
    assert cursor.statistics()['scanned_full'] == 0
    assert cursor.statistics()['scanned_index'] == 2
    assert cursor.warnings() == []
    assert cursor.count() == 2
    assert clean_keys(cursor.batch()) == []
    assert isinstance(cursor.statistics()['execution_time'], (int, float))
    with pytest.raises(StopIteration):
        cursor.next()
    assert cursor.close(ignore_missing=True) is False

    incorrect_cursor_data = {'id': 'invalid', 'hasMore': True, 'result': []}
    setattr(cursor, '_data', incorrect_cursor_data)
    with pytest.raises(CursorCloseError):
        cursor.close(ignore_missing=False)
    with pytest.raises(CursorNextError):
        cursor.next()


@pytest.mark.order10
def test_write_cursor_early_finish():
    global cursor, cursor_id
    col.truncate()
    col.import_bulk([doc1, doc2, doc3])
    cursor = db.aql.execute(
        '''
        FOR d IN {col} FILTER d._key == @first OR d._key == @second
        UPDATE {{_key: d._key, _val: @val }} IN {col}
        RETURN NEW
        '''.format(col=col_name),
        bind_vars={'first': '1', 'second': '2', 'val': 42},
        count=True,
        batch_size=1,
        ttl=1000,
        optimizer_rules=['+all']
    )
    assert cursor.close() is True
    with pytest.raises(CursorCloseError):
        cursor.close(ignore_missing=False)
    assert cursor.close(ignore_missing=True) is False

    col.truncate()
    col.import_bulk([doc1, doc2, doc3, doc4])

    cursor = db.aql.execute(
        'FOR d IN {} RETURN d'.format(col_name),
        count=False,
        batch_size=1,
        ttl=1000,
        optimizer_rules=['+all']
    )


@pytest.mark.order11
def test_cursor_context_manager():
    global cursor, cursor_id

    col.truncate()
    col.import_bulk([doc1, doc2, doc3])

    with db.aql.execute(
        'FOR d IN {} RETURN d'.format(col_name),
        count=False,
        batch_size=2,
        ttl=1000,
        optimizer_rules=['+all']
    ) as cursor:
        assert clean_keys(cursor.next()) == doc1
    with pytest.raises(CursorCloseError):
        cursor.close(ignore_missing=False)

    with db.aql.execute(
        'FOR d IN {} RETURN d'.format(col_name),
        count=False,
        batch_size=2,
        ttl=1000,
        optimizer_rules=['+all']
    ) as cursor:
        assert clean_keys(cursor.__next__()) == doc1
    with pytest.raises(CursorCloseError):
        cursor.close(ignore_missing=False)
    assert cursor.close(ignore_missing=True) is False


@pytest.mark.order12
def test_cursor_repr_no_id():
    col.truncate()
    col.import_bulk([doc1, doc2, doc3, doc4])
    cursor = db.aql.execute(
        'FOR d IN {} RETURN d'.format(col_name),
        count=True,
        batch_size=2,
        ttl=1000,
        optimizer_rules=['+all']
    )
    getattr(cursor, '_data')['id'] = None
    assert repr(cursor) == '<ArangoDB cursor>'
