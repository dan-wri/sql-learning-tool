"""Compare a learner's SELECT result with the reference result without revealing the expected data."""

from collections import Counter
from dataclasses import dataclass

from app.sql.executor import QueryResult
from app.validation.normalize import normalize_row


@dataclass(frozen=True)
class Verdict:
    passed: bool
    code: str
    message: str


PASS = Verdict(True, "pass", "Correct! Your query returns exactly the right result.")


def _plural(n: int, word: str) -> str:
    return f"{n} {word}" if n == 1 else f"{n} {word}s"


def _column_label(columns: list[str], index: int) -> str:
    return f"column {index + 1} (`{columns[index]}`)"


def compare_results(expected: QueryResult, actual: QueryResult, *, ordered: bool) -> Verdict:
    if actual.truncated:
        return Verdict(False, "too_many_rows",
                       "Your query returns far more rows than expected. Check your filtering and joins.")

    expected_width, actual_width = len(expected.columns), len(actual.columns)
    if expected_width != actual_width:
        return Verdict(False, "column_count",
                       f"Your query returns {_plural(actual_width, 'column')}, but the task needs {expected_width}. "
                       "Re-read which columns the task asks for.")

    expected_rows = [normalize_row(r) for r in expected.rows]
    actual_rows = [normalize_row(r) for r in actual.rows]

    if len(expected_rows) != len(actual_rows):
        direction = "more" if len(actual_rows) > len(expected_rows) else "fewer"
        advice = ("Check whether your WHERE clause or LIMIT is filtering enough." if direction == "more"
                  else "Check whether your WHERE clause or LIMIT is too strict.")
        return Verdict(False, "row_count",
                       f"Your query returns {_plural(len(actual_rows), 'row')}, which is {direction} than expected "
                       f"({len(expected_rows)}). {advice}")

    if Counter(expected_rows) == Counter(actual_rows):
        if ordered and expected_rows != actual_rows:
            return Verdict(False, "row_order",
                           "You have the right rows, but not in the order the task asks for. Check your ORDER BY.")
        return PASS

    expected_columns = [Counter(col) for col in zip(*expected_rows)]
    actual_columns = [Counter(col) for col in zip(*actual_rows)]
    mismatched = [i for i, (e, a) in enumerate(zip(expected_columns, actual_columns)) if e != a]

    if mismatched and sorted(map(_counter_key, expected_columns)) == sorted(map(_counter_key, actual_columns)):
        return Verdict(False, "column_order",
                       "Your columns contain the right data but are in a different order from the task.")

    if mismatched:
        labels = ", ".join(_column_label(actual.columns, i) for i in mismatched)
        return Verdict(False, "wrong_values",
                       f"The values in {labels} don't match what the task expects.")

    return Verdict(False, "wrong_values",
                   "Each column has the right values, but they're combined into the wrong rows.")


def _counter_key(counter: Counter) -> str:
    return repr(sorted(counter.items(), key=repr))
