from __future__ import absolute_import, unicode_literals

from arango.exceptions import (
    ViewCreateError,
    ViewDeleteError,
    ViewGetError,
    ViewListError,
    ViewRenameError,
    ViewReplaceError,
    ViewUpdateError
)
from tests.helpers import assert_raises, generate_view_name


def test_view_management(db, bad_db):
    # Test create view
    view_name = generate_view_name()
    bad_view_name = generate_view_name()
    view_type = 'arangosearch'
    view_properties = {
        'consolidationIntervalMsec': 50000,
        # 'consolidationPolicy': {'segmentThreshold': 200}
    }

    result = db.create_view(view_name, view_type, view_properties)
    assert 'id' in result
    assert result['name'] == view_name
    assert result['type'] == view_type
    assert result['consolidationIntervalMsec'] == 50000
    view_id = result['id']

    # Test create duplicate view
    with assert_raises(ViewCreateError) as err:
        db.create_view(view_name, view_type, view_properties)
    assert err.value.error_code == 1207

    # Test list views
    result = db.views()
    assert len(result) == 1
    view = result[0]
    assert view['id'] == view_id
    assert view['name'] == view_name
    assert view['type'] == view_type

    # Test list view with bad database
    with assert_raises(ViewListError) as err:
        bad_db.views()
    assert err.value.error_code in {11, 1228}

    # Test get view
    view = db.view(view_name)
    assert view['id'] == view_id
    assert view['name'] == view_name
    assert view['type'] == view_type
    assert view['consolidationIntervalMsec'] == 50000

    # Test get missing view
    with assert_raises(ViewGetError) as err:
        db.view(bad_view_name)
    assert err.value.error_code == 1203

    # Test update view
    view = db.update_view(view_name, {'consolidationIntervalMsec': 70000})
    assert view['id'] == view_id
    assert view['name'] == view_name
    assert view['type'] == view_type
    assert view['consolidationIntervalMsec'] == 70000

    # Test update with bad database
    with assert_raises(ViewUpdateError) as err:
        bad_db.update_view(view_name, {'consolidationIntervalMsec': 80000})
    assert err.value.error_code in {11, 1228}

    # Test replace view
    view = db.replace_view(view_name, {'consolidationIntervalMsec': 40000})
    assert view['id'] == view_id
    assert view['name'] == view_name
    assert view['type'] == view_type
    assert view['consolidationIntervalMsec'] == 40000

    # Test replace with bad database
    with assert_raises(ViewReplaceError) as err:
        bad_db.replace_view(view_name, {'consolidationIntervalMsec': 7000})
    assert err.value.error_code in {11, 1228}

    # Test rename view
    new_view_name = generate_view_name()
    assert db.rename_view(view_name, new_view_name) is True
    result = db.views()
    assert len(result) == 1
    view = result[0]
    assert view['id'] == view_id
    assert view['name'] == new_view_name

    # Test rename missing view
    with assert_raises(ViewRenameError) as err:
        db.rename_view(bad_view_name, view_name)
    assert err.value.error_code == 1203

    # Test delete view
    assert db.delete_view(new_view_name) is True
    assert len(db.views()) == 0

    # Test delete missing view
    with assert_raises(ViewDeleteError) as err:
        db.delete_view(new_view_name)
    assert err.value.error_code == 1203

    # Test delete missing view with ignore_missing set to True
    assert db.delete_view(view_name, ignore_missing=True) is False
