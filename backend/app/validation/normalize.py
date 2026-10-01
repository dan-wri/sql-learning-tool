FLOAT_PLACES = 6


def normalize_value(value):
    """Make values that a learner would consider equal compare equal (3 vs 3.0, float noise)."""
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, float):
        rounded = round(value, FLOAT_PLACES)
        return int(rounded) if rounded.is_integer() else rounded
    return value


def normalize_row(row: tuple) -> tuple:
    return tuple(normalize_value(v) for v in row)
