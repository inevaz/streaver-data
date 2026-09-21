from data_parser.errors import InvalidRecordError


def normalize_name(value: str, label: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise InvalidRecordError(f"Missing {label} value")
    return cleaned


def normalize_color(value: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise InvalidRecordError("Missing color value")
    return cleaned
