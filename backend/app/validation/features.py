"""Broad structural feature checks for the few levels that introduce a construct (CTE, window function).

Result validation stays the definition of correctness; this only confirms the lesson's construct was used.
"""

import sqlglot
from sqlglot import exp
from sqlglot.errors import SqlglotError

FEATURE_NODES: dict[str, type[exp.Expression]] = {
    "cte": exp.CTE,
    "window": exp.Window,
}

FEATURE_LABELS = {"cte": "a common table expression (WITH ...)", "window": "a window function (... OVER ...)"}


def missing_features(sql: str, required: list[str]) -> list[str]:
    """Required features absent from the SQL. Unparseable SQL is left to SQLite to report."""
    try:
        tree = sqlglot.parse_one(sql, read="sqlite")
    except SqlglotError:
        return []
    if tree is None:
        return []
    return [name for name in required if tree.find(FEATURE_NODES[name]) is None]
