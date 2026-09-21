import csv

from data_parser.errors import InvalidReason, InvalidRecordError
from data_parser.models import PersonRecord
from data_parser.normalization import normalize_color, normalize_name
from data_parser.validation import normalize_phone, normalize_zipcode, validate_phone, validate_zipcode


def _clean_fields(fields):
    return [field.strip() for field in fields]


def _looks_like_phone(value: str) -> bool:
    if value is None:
        return False
    cleaned = value.strip()
    if not cleaned:
        return False
    return validate_phone(cleaned)


def _looks_like_zip(value: str) -> bool:
    if value is None:
        return False
    return validate_zipcode(value.strip())


def _parse_format_a(fields):
    if len(fields) != 5:
        raise InvalidRecordError("Format A requires 5 fields")
    lastname = normalize_name(fields[0], "lastname")
    firstname = normalize_name(fields[1], "firstname")
    phone = normalize_phone(fields[2])
    color = normalize_color(fields[3])
    zipcode = normalize_zipcode(fields[4])
    return PersonRecord(
        firstname=firstname,
        lastname=lastname,
        phonenumber=phone,
        color=color,
        zipcode=zipcode,
    )


def _parse_format_b(fields):
    if len(fields) != 4:
        raise InvalidRecordError("Format B requires 4 fields")
    combined_name = fields[0].strip()
    if " " not in combined_name:
        raise InvalidRecordError("Format B requires a first and last name separated by whitespace")

    firstname, lastname = combined_name.rsplit(" ", 1)
    firstname = normalize_name(firstname, "firstname")
    lastname = normalize_name(lastname, "lastname")
    color = normalize_color(fields[1])
    zipcode = normalize_zipcode(fields[2])
    phone = normalize_phone(fields[3])
    return PersonRecord(
        firstname=firstname,
        lastname=lastname,
        phonenumber=phone,
        color=color,
        zipcode=zipcode,
    )


def _parse_format_c(fields):
    if len(fields) != 5:
        raise InvalidRecordError("Format C requires 5 fields")
    firstname = normalize_name(fields[0], "firstname")
    lastname = normalize_name(fields[1], "lastname")
    zipcode = normalize_zipcode(fields[2])
    phone = normalize_phone(fields[3])
    color = normalize_color(fields[4])
    return PersonRecord(
        firstname=firstname,
        lastname=lastname,
        phonenumber=phone,
        color=color,
        zipcode=zipcode,
    )


def detect_format(fields):
    cleaned = _clean_fields(fields)
    if len(cleaned) == 4:
        return "B"
    if len(cleaned) == 5:
        # Phone position distinguishes A from C without making assumptions
        # about color, which may itself look like a ZIP code or phone number.
        if _looks_like_phone(cleaned[2]):
            return "A"
        if _looks_like_phone(cleaned[3]):
            return "C"
        # Fall back to ZIP position so malformed phones are still attributed
        # to the intended format and rejected by its normal validation.
        if _looks_like_zip(cleaned[4]):
            return "A"
        if _looks_like_zip(cleaned[2]):
            return "C"
    raise InvalidRecordError("Unsupported record structure", InvalidReason.UNSUPPORTED_FORMAT)


def parse_line(raw_line: str) -> PersonRecord:
    if raw_line is None or raw_line.strip() == "":
        raise InvalidRecordError("Blank line is not a valid record")

    try:
        tokens = next(csv.reader([raw_line], strict=True))
    except csv.Error as exc:  # pragma: no cover - covered by invalid input behavior
        raise InvalidRecordError("Unable to parse CSV record", InvalidReason.MALFORMED_CSV) from exc

    if not tokens or not any(token.strip() for token in tokens):
        raise InvalidRecordError("Empty record")

    cleaned = _clean_fields(tokens)
    format_name = detect_format(cleaned)

    if format_name == "A":
        return _parse_format_a(cleaned)
    if format_name == "B":
        return _parse_format_b(cleaned)
    if format_name == "C":
        return _parse_format_c(cleaned)

    raise InvalidRecordError("Unsupported record format")
