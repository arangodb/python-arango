import time
import warnings

import pytest
from packaging import version

from arango.errno import DATABASE_NOT_FOUND, FORBIDDEN
from arango.exceptions import (
    ClusterEndpointsError,
    ClusterHealthError,
    ClusterMaintenanceModeError,
    ClusterRebalanceError,
    ClusterServerCountError,
    ClusterServerEngineError,
    ClusterServerIDError,
    ClusterServerRoleError,
    ClusterServerStatisticsError,
    ClusterServerVersionError,
)
from tests.helpers import assert_raises


def test_cluster_server_id(sys_db, bad_db, cluster):
    if not cluster:
        pytest.skip("Only tested in a cluster setup")

    result = sys_db.cluster.server_id()
    assert isinstance(result, str)

    with assert_raises(ClusterServerIDError) as err:
        bad_db.cluster.server_id()
    assert err.value.error_code in {FORBIDDEN, DATABASE_NOT_FOUND}


def test_cluster_server_role(sys_db, bad_db, cluster):
    if not cluster:
        pytest.skip("Only tested in a cluster setup")

    result = sys_db.cluster.server_role()
    assert isinstance(result, str)

    with assert_raises(ClusterServerRoleError) as err:
        bad_db.cluster.server_role()
    assert err.value.error_code in {FORBIDDEN, DATABASE_NOT_FOUND}


def test_cluster_health(sys_db, bad_db, cluster):
    if not cluster:
        pytest.skip("Only tested in a cluster setup")

    result = sys_db.cluster.health()
    assert "Health" in result
    assert "ClusterId" in result

    with assert_raises(ClusterHealthError) as err:
        bad_db.cluster.health()
    assert err.value.error_code in {FORBIDDEN, DATABASE_NOT_FOUND}


def test_cluster_server_version(sys_db, bad_db, cluster):
    if not cluster:
        pytest.skip("Only tested in a cluster setup")

    server_id = sys_db.cluster.server_id()
    result = sys_db.cluster.server_version(server_id)
    assert "server" in result
    assert "version" in result

    with assert_raises(ClusterServerVersionError) as err:
        bad_db.cluster.server_version(server_id)
    assert err.value.error_code in {FORBIDDEN, DATABASE_NOT_FOUND}


def test_cluster_server_engine(sys_db, bad_db, cluster):
    if not cluster:
        pytest.skip("Only tested in a cluster setup")

    server_id = sys_db.cluster.server_id()
    result = sys_db.cluster.server_engine(server_id)
    assert "name" in result
    assert "supports" in result

    with assert_raises(ClusterServerEngineError) as err:
        bad_db.cluster.server_engine(server_id)
    assert err.value.error_code in {FORBIDDEN, DATABASE_NOT_FOUND}


def test_cluster_server_statistics(sys_db, bad_db, cluster):
    if not cluster:
        pytest.skip("Only tested in a cluster setup")

    server_id = sys_db.cluster.server_id()
    result = sys_db.cluster.server_statistics(server_id)
    assert "time" in result
    assert "system" in result
    assert "enabled" in result

    with assert_raises(ClusterServerStatisticsError) as err:
        bad_db.cluster.server_statistics(server_id)
    assert err.value.error_code in {FORBIDDEN, DATABASE_NOT_FOUND}


def test_cluster_server_maintenance_mode(sys_db, bad_db, cluster):
    if not cluster:
        pytest.skip("Only tested in a cluster setup")

    server_id = sys_db.cluster.server_id()
    result = sys_db.cluster.server_maintenance_mode(server_id)
    assert result == {}

    with assert_raises(ClusterMaintenanceModeError) as err:
        bad_db.cluster.server_maintenance_mode(server_id)
    assert err.value.error_code in {FORBIDDEN, DATABASE_NOT_FOUND}

    sys_db.cluster.toggle_server_maintenance_mode(server_id, "maintenance", timeout=1)
    result = sys_db.cluster.server_maintenance_mode(server_id)
    assert "Mode" in result
    assert "Until" in result

    time.sleep(5)
    result = sys_db.cluster.server_maintenance_mode(server_id)
    assert result == {}


def test_cluster_toggle_maintenance_mode(sys_db, bad_db, cluster):
    if not cluster:
        pytest.skip("Only tested in a cluster setup")

    result = sys_db.cluster.toggle_maintenance_mode("on")
    assert "error" in result or "warning" in result

    result = sys_db.cluster.toggle_maintenance_mode("off")
    assert "error" in result or "warning" in result

    with assert_raises(ClusterMaintenanceModeError) as err:
        bad_db.cluster.toggle_maintenance_mode("on")
    assert err.value.error_code in {FORBIDDEN, DATABASE_NOT_FOUND}


def test_cluster_endpoints(db, bad_db, cluster):
    if not cluster:
        pytest.skip("Only tested in a cluster setup")

    # Test get server endpoints
    assert len(db.cluster.endpoints()) > 0

    # Test get server endpoints with bad database
    with assert_raises(ClusterEndpointsError) as err:
        bad_db.cluster.endpoints()
    assert err.value.error_code in {FORBIDDEN, DATABASE_NOT_FOUND}


def test_cluster_server_count(db, bad_db, cluster):
    if not cluster:
        pytest.skip("Only tested in a cluster setup")

    # Test get server count
    db.cluster.server_count()

    # Test get server endpoints with bad database
    with assert_raises(ClusterServerCountError) as err:
        bad_db.cluster.server_count()
    assert err.value.error_code in {FORBIDDEN, DATABASE_NOT_FOUND}


def test_cluster_rebalance(sys_db, bad_db, cluster, db_version):
    if not cluster:
        pytest.skip("Only tested in a cluster setup")

    if db_version < version.parse("3.10.0"):
        pytest.skip("Only tested on ArangoDB 3.10+")

    # Test imbalance retrieval
    imbalance = sys_db.cluster.calculate_imbalance()
    assert "leader" in imbalance
    assert "shards" in imbalance
    assert imbalance["pendingMoveShards"] == 0
    assert imbalance["todoMoveShards"] == 0

    with assert_raises(ClusterRebalanceError) as err:
        bad_db.cluster.calculate_imbalance()
    assert err.value.error_code == FORBIDDEN

    # Test rebalance computation
    rebalance = sys_db.cluster.calculate_rebalance_plan(
        max_moves=3,
        leader_changes=True,
        move_leaders=True,
        move_followers=True,
        pi_factor=1234.5,
        databases_excluded=["_system"],
    )
    assert "imbalanceBefore" in rebalance
    assert "imbalanceAfter" in rebalance
    assert "moves" in rebalance

    with assert_raises(ClusterRebalanceError) as err:
        bad_db.cluster.calculate_rebalance_plan()
    assert err.value.error_code == FORBIDDEN

    # Test rebalance execution
    if sys_db.cluster.execute_rebalance_plan(rebalance["moves"]) is False:
        warnings.warn(
            "Rebalance plan was not executed."
            "This may happen independent of the driver."
        )
    with assert_raises(ClusterRebalanceError) as err:
        bad_db.cluster.execute_rebalance_plan(rebalance["moves"])
    assert err.value.error_code == FORBIDDEN

    # Rebalance cluster in one go
    rebalance = sys_db.cluster.rebalance()
    assert "imbalanceBefore" in rebalance
    assert "imbalanceAfter" in rebalance
    assert "moves" in rebalance

    with assert_raises(ClusterRebalanceError) as err:
        bad_db.cluster.rebalance()
    assert err.value.error_code == FORBIDDEN
