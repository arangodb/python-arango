from packaging import version

from arango.exceptions import (
    AnalyzerCreateError,
    AnalyzerDeleteError,
    AnalyzerGetError,
    AnalyzerListError,
)
from tests.helpers import assert_raises, generate_analyzer_name


def test_analyzer_management(db, bad_db, skip_tests, db_version):
    analyzer_name = generate_analyzer_name()
    full_analyzer_name = db.name + "::" + analyzer_name
    bad_analyzer_name = generate_analyzer_name()

    # Test create identity analyzer
    result = db.create_analyzer(analyzer_name, "identity", {})
    assert result["name"] == full_analyzer_name
    assert result["type"] == "identity"
    assert result["properties"] == {}
    assert result["features"] == []

    # Test create delimiter analyzer
    result = db.create_analyzer(
        name=generate_analyzer_name(),
        analyzer_type="delimiter",
        properties={"delimiter": ","},
    )
    assert result["type"] == "delimiter"
    assert result["properties"] == {"delimiter": ","}
    assert result["features"] == []

    # Test create duplicate with bad database
    with assert_raises(AnalyzerCreateError) as err:
        bad_db.create_analyzer(analyzer_name, "identity", {}, [])
    assert err.value.error_code in {11, 1228}

    # Test get analyzer
    result = db.analyzer(analyzer_name)
    assert result["name"] == full_analyzer_name
    assert result["type"] == "identity"
    assert result["properties"] == {}
    assert result["features"] == []

    # Test get missing analyzer
    with assert_raises(AnalyzerGetError) as err:
        db.analyzer(bad_analyzer_name)
    assert err.value.error_code in {1202}

    # Test list analyzers
    result = db.analyzers()
    assert full_analyzer_name in [a["name"] for a in result]

    # Test list analyzers with bad database
    with assert_raises(AnalyzerListError) as err:
        bad_db.analyzers()
    assert err.value.error_code in {11, 1228}

    # Test delete analyzer
    assert db.delete_analyzer(analyzer_name, force=True) is True
    assert full_analyzer_name not in [a["name"] for a in db.analyzers()]

    # Test delete missing analyzer
    with assert_raises(AnalyzerDeleteError) as err:
        db.delete_analyzer(analyzer_name)
    assert err.value.error_code in {1202}

    # Test delete missing analyzer with ignore_missing set to True
    assert db.delete_analyzer(analyzer_name, ignore_missing=True) is False

    # Test create geo_s2 analyzer (EE only)
    if "enterprise" not in skip_tests:
        analyzer_name = generate_analyzer_name()
        result = db.create_analyzer(analyzer_name, "geo_s2", {})
        assert result["type"] == "geo_s2"
        assert result["features"] == []
        assert result["properties"] == {
            "options": {"maxCells": 20, "minLevel": 4, "maxLevel": 23},
            "type": "shape",
            "format": "latLngDouble",
        }
        assert db.delete_analyzer(analyzer_name)

    # Test create delimieter analyzer with multiple delimiters
    if db_version >= version.parse("3.12.0"):
        result = db.create_analyzer(
            name=generate_analyzer_name(),
            analyzer_type="multi_delimiter",
            properties={"delimiters": [",", "."]},
        )

        assert result["type"] == "multi_delimiter"
        assert result["properties"] == {"delimiters": [",", "."]}
        assert result["features"] == []

    if db_version >= version.parse("3.12.0"):
        analyzer_name = generate_analyzer_name()
        result = db.create_analyzer(analyzer_name, "wildcard", {"ngramSize": 4})
        assert result["type"] == "wildcard"
        assert result["features"] == []
        assert result["properties"] == {"ngramSize": 4}
