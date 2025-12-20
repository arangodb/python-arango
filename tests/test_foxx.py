import json
import os

import pytest

from arango.exceptions import (
    FoxxCommitError,
    FoxxConfigGetError,
    FoxxConfigReplaceError,
    FoxxConfigUpdateError,
    FoxxDependencyGetError,
    FoxxDependencyReplaceError,
    FoxxDependencyUpdateError,
    FoxxDevModeDisableError,
    FoxxDevModeEnableError,
    FoxxDownloadError,
    FoxxReadmeGetError,
    FoxxScriptListError,
    FoxxScriptRunError,
    FoxxServiceCreateError,
    FoxxServiceDeleteError,
    FoxxServiceGetError,
    FoxxServiceListError,
    FoxxServiceReplaceError,
    FoxxServiceUpdateError,
    FoxxSwaggerGetError,
    FoxxTestRunError,
)
from arango.foxx import Foxx
from tests.helpers import assert_raises, extract, generate_service_mount

service_file = "/tests/static/service.zip"
service_name = "test"


def test_foxx_attributes(db, skip_tests):
    if "foxx" in skip_tests:
        pytest.skip("Skipping foxx tests")
    assert isinstance(db.foxx, Foxx)
    assert repr(db.foxx) == f"<Foxx in {db.name}>"


def test_foxx_service_management_json(db, bad_db, cluster, skip_tests, foxx_path):
    if "foxx" in skip_tests:
        pytest.skip("Skipping foxx tests")
    if cluster:
        pytest.skip("Not tested in a cluster setup")

    service_mount = generate_service_mount()
    missing_mount = generate_service_mount()

    # Test list services
    for service in db.foxx.services():
        assert "development" in service
        assert "legacy" in service
        assert "mount" in service
        assert "name" in service
        assert "provides" in service
        assert "version" in service

    # Test list services with bad database
    with assert_raises(FoxxServiceListError) as err:
        bad_db.foxx.services()
    assert err.value.error_code in {11, 1228}

    # Test create service
    service = db.foxx.create_service(
        mount=service_mount,
        source=foxx_path,
        config={},
        dependencies={},
        development=True,
        setup=True,
        legacy=True,
    )
    assert service["mount"] == service_mount
    assert service["name"] == service_name
    assert service["development"] is True
    assert service["legacy"] is True
    assert service["manifest"]["configuration"] == {}
    assert service["manifest"]["dependencies"] == {}

    # Test create duplicate service
    with assert_raises(FoxxServiceCreateError) as err:
        db.foxx.create_service(service_mount, "service.zip")
    assert err.value.error_code == 3011

    # Test get service
    service = db.foxx.service(service_mount)
    assert service["mount"] == service_mount
    assert service["name"] == service_name
    assert service["development"] is True
    assert service["manifest"]["configuration"] == {}
    assert service["manifest"]["dependencies"] == {}
    assert "checksum" in service
    assert "options" in service
    assert "path" in service
    assert "version" in service

    # Test get missing service
    with assert_raises(FoxxServiceGetError) as err:
        db.foxx.service(missing_mount)
    assert err.value.error_code == 3009

    # Test update service
    service = db.foxx.update_service(
        mount=service_mount,
        source=service_file,
        config={},
        dependencies={},
        teardown=True,
        setup=True,
        legacy=False,
        force=False,
    )
    assert service["mount"] == service_mount
    assert service["name"] == service_name
    assert service["legacy"] is False

    # Test update missing service
    with assert_raises(FoxxServiceUpdateError) as err:
        db.foxx.update_service(missing_mount, "service.zip")
    assert err.value.error_code == 3009

    # Test replace service
    service = db.foxx.replace_service(
        mount=service_mount,
        source=foxx_path,
        config={},
        dependencies={},
        teardown=True,
        setup=True,
        legacy=True,
        force=False,
    )
    assert service["mount"] == service_mount
    assert service["name"] == service_name
    assert service["legacy"] is True

    # Test replace missing service
    with assert_raises(FoxxServiceReplaceError) as err:
        db.foxx.replace_service(missing_mount, "service.zip")
    assert err.value.error_code == 3009

    assert db.foxx.delete_service(service_mount, teardown=False) is True
    assert service_mount not in extract("mount", db.foxx.services())

    # Test delete missing service
    with assert_raises(FoxxServiceDeleteError) as err:
        db.foxx.delete_service(missing_mount, teardown=False)
    assert err.value.error_code == 3009


def test_foxx_service_management_file(db, cluster, skip_tests, foxx_path):
    if "foxx" in skip_tests:
        pytest.skip("Skipping foxx tests")
    if cluster:
        pytest.skip("Not tested in a cluster setup")

    bad_path = os.path.join(os.path.dirname(__file__), "static", "service")

    service_mount = generate_service_mount()
    missing_mount = generate_service_mount()

    # Test create service by file with wrong extension
    with assert_raises(ValueError):
        db.foxx.create_service_with_file(service_mount, bad_path)

    # Test create service by file
    service = db.foxx.create_service_with_file(
        mount=service_mount,
        filename=foxx_path,
        development=True,
        setup=True,
        legacy=True,
        config={"foo": "bar"},
        dependencies={},
    )
    assert service["mount"] == service_mount
    assert service["name"] == service_name
    assert service["development"] is True
    assert service["legacy"] is True
    assert service["manifest"]["configuration"] == {}
    assert service["manifest"]["dependencies"] == {}

    # Test create duplicate service
    with assert_raises(FoxxServiceCreateError) as err:
        db.foxx.create_service_with_file(service_mount, foxx_path)
    assert err.value.error_code == 3011

    # Update config and dependencies
    assert db.foxx.update_config(service_mount, {}) == {"values": {}}
    assert db.foxx.update_dependencies(service_mount, {}) == {"values": {}}

    # Test update service by file
    service = db.foxx.update_service_with_file(
        mount=service_mount,
        filename=foxx_path,
        teardown=False,
        setup=False,
        legacy=False,
        force=False,
        config={},
        dependencies={},
    )
    assert service["mount"] == service_mount
    assert service["name"] == service_name
    assert service["legacy"] is False
    assert service["manifest"]["configuration"] == {}
    assert service["manifest"]["dependencies"] == {}

    # Test update missing service
    with assert_raises(FoxxServiceUpdateError) as err:
        db.foxx.update_service_with_file(missing_mount, foxx_path)
    assert err.value.error_code == 3009

    # Test replace service by file
    service = db.foxx.replace_service_with_file(
        mount=service_mount,
        filename=foxx_path,
        teardown=True,
        setup=True,
        legacy=True,
        force=False,
        config={},
        dependencies={},
    )
    assert service["mount"] == service_mount
    assert service["name"] == service_name
    assert service["legacy"] is True
    assert service["manifest"]["configuration"] == {}
    assert service["manifest"]["dependencies"] == {}

    # Test replace missing service
    with assert_raises(FoxxServiceReplaceError) as err:
        db.foxx.replace_service_with_file(missing_mount, foxx_path)
    assert err.value.error_code == 3009

    assert db.foxx.delete_service(service_mount, teardown=False) is True
    assert service_mount not in extract("mount", db.foxx.services())


def test_foxx_config_management(db, cluster, skip_tests):
    if "foxx" in skip_tests:
        pytest.skip("Skipping foxx tests")
    if cluster:
        pytest.skip("Not tested in a cluster setup")

    service_mount = generate_service_mount()
    missing_mount = generate_service_mount()

    # Prep the test service
    db.foxx.create_service(
        mount=service_mount,
        source=service_file,
        config={},
    )

    # Test get service config
    assert db.foxx.config(service_mount) == {}

    # Test get missing service config
    with assert_raises(FoxxConfigGetError) as err:
        db.foxx.config(missing_mount)
    assert err.value.error_code == 3009

    # Test update service config
    assert db.foxx.update_config(service_mount, {}) == {"values": {}}

    # Test update missing service config
    with assert_raises(FoxxConfigUpdateError) as err:
        db.foxx.update_config(missing_mount, {})
    assert err.value.error_code == 3009

    # Test replace service config
    assert db.foxx.replace_config(service_mount, {}) == {"values": {}}

    # Test replace missing service config
    with assert_raises(FoxxConfigReplaceError) as err:
        db.foxx.replace_config(missing_mount, {})
    assert err.value.error_code == 3009


def test_foxx_dependency_management(db, cluster, skip_tests):
    if "foxx" in skip_tests:
        pytest.skip("Skipping foxx tests")
    if cluster:
        pytest.skip("Not tested in a cluster setup")

    service_mount = generate_service_mount()
    missing_mount = generate_service_mount()

    # Prep the test service
    db.foxx.create_service(mount=service_mount, source=service_file, dependencies={})

    # Test get service dependencies
    assert db.foxx.dependencies(service_mount) == {}

    # Test get missing service dependencies
    with assert_raises(FoxxDependencyGetError) as err:
        db.foxx.dependencies(missing_mount)
    assert err.value.error_code == 3009

    # Test update service dependencies
    assert db.foxx.update_dependencies(service_mount, {}) == {"values": {}}

    # Test update missing service dependencies
    with assert_raises(FoxxDependencyUpdateError) as err:
        db.foxx.update_dependencies(missing_mount, {})
    assert err.value.error_code == 3009

    # Test replace service dependencies
    assert db.foxx.replace_dependencies(service_mount, {}) == {"values": {}}

    # Test replace missing service dependencies
    with assert_raises(FoxxDependencyReplaceError) as err:
        db.foxx.replace_dependencies(missing_mount, {})
    assert err.value.error_code == 3009


def test_foxx_development_toggle(db, cluster, skip_tests):
    if "foxx" in skip_tests:
        pytest.skip("Skipping foxx tests")
    if cluster:
        pytest.skip("Not tested in a cluster setup")

    service_mount = generate_service_mount()
    missing_mount = generate_service_mount()

    # Prep the test service
    db.foxx.create_service(
        mount=service_mount,
        source=service_file,
        development=False,
    )

    # Test enable development mode
    service = db.foxx.enable_development(service_mount)
    assert service["mount"] == service_mount
    assert service["name"] == service_name
    assert service["development"] is True

    # Test enable development mode for missing service
    with assert_raises(FoxxDevModeEnableError) as err:
        db.foxx.enable_development(missing_mount)
    assert err.value.error_code == 3009

    # Test disable development mode
    service = db.foxx.disable_development(service_mount)
    assert service["mount"] == service_mount
    assert service["name"] == service_name
    assert service["development"] is False

    # Test disable development mode for missing service
    with assert_raises(FoxxDevModeDisableError) as err:
        db.foxx.disable_development(missing_mount)
    assert err.value.error_code == 3009


def test_foxx_misc_functions(db, bad_db, cluster, skip_tests):
    if "foxx" in skip_tests:
        pytest.skip("Skipping foxx tests")
    if cluster:
        pytest.skip("Not tested in a cluster setup")

    service_mount = generate_service_mount()
    missing_mount = generate_service_mount()

    # Prep the test service
    db.foxx.create_service(
        mount=service_mount,
        source=service_file,
    )

    # Test get service readme
    assert "Apache 2" in db.foxx.readme(service_mount)

    # Test get missing service readme
    with assert_raises(FoxxReadmeGetError) as err:
        db.foxx.readme(missing_mount)
    assert err.value.error_code == 3009

    # Test get service swagger
    swagger = db.foxx.swagger(service_mount)
    assert "swagger" in swagger
    assert "paths" in swagger
    assert "info" in swagger
    assert "base_path" in swagger

    # Test get missing service swagger
    with assert_raises(FoxxSwaggerGetError) as err:
        db.foxx.swagger(missing_mount)
    assert err.value.error_code == 3009

    # Test download service
    assert isinstance(db.foxx.download(service_mount), str)

    # Test download missing service
    with assert_raises(FoxxDownloadError) as err:
        db.foxx.download(missing_mount)
    assert err.value.error_code == 3009

    # Test commit service state
    assert db.foxx.commit(replace=True) is True
    assert db.foxx.commit(replace=False) is True

    # Test commit service state with bad database
    with assert_raises(FoxxCommitError) as err:
        bad_db.foxx.commit(replace=True)
    assert err.value.error_code in {11, 1228}

    # Test list service scripts
    scripts = db.foxx.scripts(service_mount)
    assert "setup" in scripts
    assert "teardown" in scripts

    # Test list missing service scripts
    with assert_raises(FoxxScriptListError) as err:
        db.foxx.scripts(missing_mount)
    assert err.value.error_code == 3009

    # Test run service script
    assert db.foxx.run_script(service_mount, "setup", []) == {}
    assert db.foxx.run_script(service_mount, "teardown", []) == {}

    # Test run missing service script
    with assert_raises(FoxxScriptRunError) as err:
        db.foxx.run_script(service_mount, "invalid", ())
    assert err.value.error_code == 3016

    # Test run tests on service
    result_str = db.foxx.run_tests(
        mount=service_mount, reporter="suite", idiomatic=True, name_filter="science"
    )
    result_json = json.loads(result_str)
    assert "stats" in result_json
    assert "tests" in result_json
    assert "suites" in result_json

    result_str = db.foxx.run_tests(
        mount=service_mount, reporter="stream", output_format="x-ldjson"
    )
    for result_part in result_str.split("\r\n"):
        if len(result_part) == 0:
            continue
        assert result_part.startswith("[")
        assert result_part.endswith("]")

    result_str = db.foxx.run_tests(
        mount=service_mount, reporter="stream", output_format="text"
    )
    assert result_str.startswith("[")
    assert result_str.endswith("]") or result_str.endswith("\r\n")

    result_str = db.foxx.run_tests(
        mount=service_mount, reporter="xunit", output_format="xml"
    )
    assert result_str.startswith("[")
    assert result_str.endswith("]") or result_str.endswith("\r\n")

    # Test run tests on missing service
    with assert_raises(FoxxTestRunError) as err:
        db.foxx.run_tests(missing_mount)
    assert err.value.error_code == 3009
