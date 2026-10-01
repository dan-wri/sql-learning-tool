import pytest

from app.sql.executor import QueryResult
from app.validation.result_validator import compare_results


def result(columns, rows, truncated=False):
    return QueryResult(columns=columns, rows=rows, truncated=truncated)


EXPECTED = result(["first_name", "total"], [
                  ("Ada", 10), ("Bob", 7), ("Cy", 3)])


def test_identical_results_pass():
    assert compare_results(EXPECTED, EXPECTED, ordered=True).passed


def test_column_names_are_ignored():
    actual = result(["name", "sum"], EXPECTED.rows)
    assert compare_results(EXPECTED, actual, ordered=False).passed


def test_row_order_ignored_when_not_required():
    actual = result(EXPECTED.columns, list(reversed(EXPECTED.rows)))
    assert compare_results(EXPECTED, actual, ordered=False).passed


def test_row_order_enforced_when_required():
    actual = result(EXPECTED.columns, list(reversed(EXPECTED.rows)))
    verdict = compare_results(EXPECTED, actual, ordered=True)
    assert not verdict.passed
    assert verdict.code == "row_order"


@pytest.mark.parametrize(
    "expected_value, actual_value",
    [(3, 3.0), (0.3, 0.1 + 0.2), (42.5, 42.500000001), (None, None)],
)
def test_numeric_normalisation(expected_value, actual_value):
    expected = result(["v"], [(expected_value,)])
    actual = result(["v"], [(actual_value,)])
    assert compare_results(expected, actual, ordered=True).passed


def test_meaningful_numeric_difference_fails():
    verdict = compare_results(result(["v"], [(42.5,)]), result(
        ["v"], [(42.51,)]), ordered=True)
    assert verdict.code == "wrong_values"


def test_null_is_not_zero_or_empty_string():
    assert not compare_results(result(["v"], [(None,)]), result(
        ["v"], [(0,)]), ordered=True).passed
    assert not compare_results(result(["v"], [(None,)]), result(
        ["v"], [("",)]), ordered=True).passed


def test_text_is_not_number():
    assert not compare_results(result(["v"], [(1,)]), result(
        ["v"], [("1",)]), ordered=True).passed


def test_column_count_mismatch():
    actual = result(["first_name"], [(r[0],) for r in EXPECTED.rows])
    verdict = compare_results(EXPECTED, actual, ordered=False)
    assert verdict.code == "column_count"
    assert "1 column" in verdict.message and "2" in verdict.message


@pytest.mark.parametrize("rows, hint", [(EXPECTED.rows[:2], "fewer"), (EXPECTED.rows + [("Dee", 1)], "more")])
def test_row_count_mismatch(rows, hint):
    verdict = compare_results(EXPECTED, result(
        EXPECTED.columns, rows), ordered=False)
    assert verdict.code == "row_count"
    assert hint in verdict.message


def test_duplicates_matter():
    expected = result(["v"], [(1,), (2,)])
    actual = result(["v"], [(1,), (1,)])
    assert compare_results(
        expected, actual, ordered=False).code == "wrong_values"


def test_swapped_columns_are_reported():
    actual = result(["total", "first_name"], [(r[1], r[0])
                    for r in EXPECTED.rows])
    verdict = compare_results(EXPECTED, actual, ordered=False)
    assert verdict.code == "column_order"


def test_wrong_values_names_the_learners_column():
    actual = result(["first_name", "my_total"], [
                    ("Ada", 10), ("Bob", 7), ("Cy", 4)])
    verdict = compare_results(EXPECTED, actual, ordered=False)
    assert verdict.code == "wrong_values"
    assert "my_total" in verdict.message
    assert "3" not in verdict.message  # never leak expected values


def test_truncated_learner_result_fails():
    verdict = compare_results(EXPECTED, result(
        EXPECTED.columns, EXPECTED.rows, truncated=True), ordered=False)
    assert verdict.code == "too_many_rows"


def test_feedback_never_contains_expected_values():
    actual = result(["a", "b"], [("Zed", 1), ("Yan", 2), ("Xi", 5)])
    verdict = compare_results(EXPECTED, actual, ordered=False)
    for value in ("Ada", "Bob", "Cy", "10"):
        assert value not in verdict.message
