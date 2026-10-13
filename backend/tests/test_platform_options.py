"""Optional validation features from the curriculum: column-name matching (D2) and required constructs (D5)."""

import pytest

from app.challenges.registry import Challenge
from app.sql.executor import QueryResult
from app.sql.orchestrator import submit
from app.validation.features import missing_features
from app.validation.result_validator import compare_results


def _result(columns, rows):
    return QueryResult(columns=columns, rows=rows, truncated=False)


def test_column_names_are_ignored_by_default():
    expected, actual = _result(["total"], [(1,)]), _result(["whatever"], [(1,)])
    assert compare_results(expected, actual, ordered=False).passed


def test_column_names_are_enforced_when_requested():
    expected = _result(["total"], [(1,)])
    verdict = compare_results(expected, _result(["n"], [(1,)]), ordered=False, match_column_names=True)
    assert not verdict.passed and verdict.code == "column_names"
    assert "total" not in verdict.message
    assert compare_results(expected, _result(["TOTAL"], [(1,)]), ordered=False, match_column_names=True).passed


@pytest.mark.parametrize("sql, required, missing", [
    ("WITH a AS (SELECT 1 AS n) SELECT n FROM a", ["cte"], []),
    ("SELECT n FROM (SELECT 1 AS n)", ["cte"], ["cte"]),
    ("SELECT ROW_NUMBER() OVER (ORDER BY name) FROM products", ["window"], []),
    ("SELECT COUNT(*) FROM products", ["window"], ["window"]),
    ("WITH a AS (SELECT 1 AS n) SELECT n FROM a", ["cte", "window"], ["window"]),
    ("SELECT FROM WHERE (((", ["cte"], []),
])
def test_feature_detection(sql, required, missing):
    assert missing_features(sql, required) == missing


def _challenge(**extra):
    return Challenge(id="x", title="T", difficulty="beginner", story="S", instructions="I",
                     reference_sql="SELECT COUNT(*) AS n FROM categories", hints=["h"], **extra)


@pytest.fixture
def conn(store, learner_id):
    with store.connection(learner_id) as connection:
        yield connection


def test_required_feature_fails_equivalent_sql_that_skips_the_construct(conn):
    challenge = _challenge(required_features=["cte"])
    outcome = submit(conn, challenge, "SELECT COUNT(*) AS n FROM categories")
    assert not outcome.passed and outcome.code == "missing_feature"
    assert not conn.in_transaction

    passing = submit(conn, challenge, "WITH c AS (SELECT * FROM categories) SELECT COUNT(*) AS n FROM c")
    assert passing.passed


def test_required_feature_does_not_mask_a_wrong_result(conn):
    outcome = submit(conn, _challenge(required_features=["cte"]), "SELECT 99")
    assert outcome.code == "wrong_values"


def test_match_column_names_through_the_orchestrator(conn):
    challenge = _challenge(match_column_names=True)
    assert submit(conn, challenge, "SELECT COUNT(*) FROM categories").code == "column_names"
    assert submit(conn, challenge, "SELECT COUNT(*) AS N FROM categories").passed
