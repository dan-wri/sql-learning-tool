"""Compare a learner's database changes with the reference changes without revealing the expected data."""

from collections import Counter

from app.sql.snapshot import TableChanges
from app.validation.normalize import normalize_row
from app.validation.result_validator import Verdict

PASS = Verdict(True, "pass", "Correct! Your changes match the task.")


def _plural(n: int, word: str = "row") -> str:
    return f"{n} {word}" if n == 1 else f"{n} {word}s"


def _projector(columns: list[str], ignored: list[str]):
    keep = [i for i, name in enumerate(columns) if name not in ignored]
    return lambda row: normalize_row(tuple(row[i] for i in keep)), [columns[i] for i in keep]


def _differing_columns(expected: list[tuple], actual: list[tuple], columns: list[str]) -> list[str]:
    expected_cols = [Counter(col) for col in zip(*expected)]
    actual_cols = [Counter(col) for col in zip(*actual)]
    return [columns[i] for i, (e, a) in enumerate(zip(expected_cols, actual_cols)) if e != a]


def _count_message(kind: str, table: str, actual: int, expected: int) -> str:
    if kind == "inserted":
        return f"Your INSERT created {_plural(actual)} in {table}; this task expects {expected}."
    return f"Your query {kind} {_plural(actual)} in {table}; this task expects {expected}."


def compare_changes(expected: dict[str, TableChanges], actual: dict[str, TableChanges], *,
                    ignore_columns: dict[str, list[str]]) -> Verdict:
    extra = sorted(actual.keys() - expected.keys())
    if extra and expected:
        return Verdict(False, "side_effect",
                       f"Your query also changed the {extra[0]} table, which this task doesn't ask for.")

    for table in sorted(expected.keys() | actual.keys()):
        exp = expected.get(table)
        act = actual.get(table)
        columns = (exp or act).columns
        project, kept_columns = _projector(
            columns, ignore_columns.get(table, []))

        exp_lists = {k: getattr(exp, k) if exp else []
                     for k in ("inserted", "updated", "deleted")}
        act_lists = {k: getattr(act, k) if act else []
                     for k in ("inserted", "updated", "deleted")}
        for kind in ("inserted", "updated", "deleted"):
            if len(exp_lists[kind]) != len(act_lists[kind]):
                return Verdict(False, "row_count",
                               _count_message(kind, table, len(act_lists[kind]), len(exp_lists[kind])))

        exp_inserted = [project(r) for r in exp_lists["inserted"]]
        act_inserted = [project(r) for r in act_lists["inserted"]]
        if Counter(exp_inserted) != Counter(act_inserted):
            columns_text = ", ".join(_differing_columns(
                exp_inserted, act_inserted, kept_columns))
            what = "a row" if len(act_inserted) == 1 else "rows"
            message = f"You inserted {what} into {table}, but one or more values don't match the task."
            return Verdict(False, "wrong_values", message + (f" Check: {columns_text}." if columns_text else ""))

        exp_before = [project(old) for old, _ in exp_lists["updated"]]
        act_before = [project(old) for old, _ in act_lists["updated"]]
        if Counter(exp_before) != Counter(act_before):
            return Verdict(False, "wrong_rows", f"Your query updated the wrong rows in {table}. Check your WHERE clause.")
        exp_after = [project(new) for _, new in exp_lists["updated"]]
        act_after = [project(new) for _, new in act_lists["updated"]]
        if Counter(exp_after) != Counter(act_after):
            columns_text = ", ".join(_differing_columns(
                exp_after, act_after, kept_columns))
            message = f"You updated the right rows in {table}, but the new values don't match the task."
            return Verdict(False, "wrong_values", message + (f" Check: {columns_text}." if columns_text else ""))

        if Counter(map(project, exp_lists["deleted"])) != Counter(map(project, act_lists["deleted"])):
            return Verdict(False, "wrong_rows", f"Your query deleted the wrong rows from {table}. Check your WHERE clause.")

    return PASS
