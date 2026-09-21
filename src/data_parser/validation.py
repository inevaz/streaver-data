import re

from data_parser.errors import InvalidReason, InvalidRecordError


_ZIP_PATTERN = re.compile(r"^[0-9]{5}$")


def _extract_ascii_digits(value: str) -> str:
    return "".join(character for character in value if "0" <= character <= "9")


def validate_phone(value: str) -> bool:
    if value is None:
        return False
    cleaned = value.strip()
    if not cleaned:
        return False
    if any(character.isdigit() and not character.isascii() for character in cleaned):
        return False
    return len(_extract_ascii_digits(cleaned)) == 10


def validate_zipcode(value: str) -> bool:
    if value is None:
        return False
    cleaned = value.strip()
    return bool(_ZIP_PATTERN.fullmatch(cleaned))


def normalize_phone(value: str) -> str:
    cleaned = value.strip()
    if not validate_phone(cleaned):
        raise InvalidRecordError("Invalid phone number", InvalidReason.INVALID_PHONE)
    digits = _extract_ascii_digits(cleaned)
    return f"{digits[:3]}-{digits[3:6]}-{digits[6:10]}"


def normalize_zipcode(value: str) -> str:
    cleaned = value.strip()
    if not validate_zipcode(cleaned):
        raise InvalidRecordError("Invalid ZIP code", InvalidReason.INVALID_ZIP)
    return cleaned
