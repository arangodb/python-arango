from __future__ import absolute_import, unicode_literals

import pytest

from arango.errno import (
    DATABASE_NOT_FOUND,
    FORBIDDEN
)
from arango.exceptions import (
    ClusterHealthError,
    ClusterMaintenanceModeError,
    ClusterServerIDError,
    ClusterServerRoleError,
    ClusterStatisticsError,
)
from tests.helpers import assert_raises


def test_cluster_server_id(sys_db, bad_db, cluster):
    if not cluster:
        pytest.skip('Only tested in a cluster setup')

    result = sys_db.cluster.server_id()
    assert isinstance(result, str)

    with assert_raises(ClusterServerIDError) as err:
        bad_db.cluster.server_id()
    assert err.value.error_code in {FORBIDDEN, DATABASE_NOT_FOUND}


def test_cluster_server_role(sys_db, bad_db, cluster):
    if not cluster:
        pytest.skip('Only tested in a cluster setup')

    result = sys_db.cluster.server_role()
    assert isinstance(result, str)

    with assert_raises(ClusterServerRoleError) as err:
        bad_db.cluster.server_role()
    assert err.value.error_code in {FORBIDDEN, DATABASE_NOT_FOUND}


def test_cluster_health(sys_db, bad_db, cluster):
    if not cluster:
        pytest.skip('Only tested in a cluster setup')

    result = sys_db.cluster.health()
    assert 'Health' in result
    assert 'ClusterId' in result

    with assert_raises(ClusterHealthError) as err:
        bad_db.cluster.health()
    assert err.value.error_code in {FORBIDDEN, DATABASE_NOT_FOUND}


def test_cluster_statistics(sys_db, bad_db, cluster):
    if not cluster:
        pytest.skip('Only tested in a cluster setup')

    server_id = sys_db.cluster.server_id()
    result = sys_db.cluster.statistics(server_id)
    assert 'time' in result
    assert 'system' in result
    assert 'enabled' in result

    with assert_raises(ClusterStatisticsError) as err:
        bad_db.cluster.statistics(server_id)
    assert err.value.error_code in {FORBIDDEN, DATABASE_NOT_FOUND}


def test_cluster_toggle_maintenance_mode(sys_db, bad_db, cluster):
    if not cluster:
        pytest.skip('Only tested in a cluster setup')

    result = sys_db.cluster.toggle_maintenance_mode('on')
    assert 'error' in result
    assert 'warning' in result

    result = sys_db.cluster.toggle_maintenance_mode('off')
    assert 'error' in result
    assert 'warning' in result

    with assert_raises(ClusterMaintenanceModeError) as err:
        bad_db.cluster.toggle_maintenance_mode('on')
    assert err.value.error_code in {FORBIDDEN, DATABASE_NOT_FOUND}
