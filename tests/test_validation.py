import pytest

from data_parser.errors import InvalidRecordError
from data_parser.validation import normalize_phone, validate_phone, validate_zipcode


@pytest.mark.parametrize(
    ("raw_phone", "expected"),
    [
        ("646 111 0101", "646-111-0101"),
        ("(646)-111-0101", "646-111-0101"),
        ("646-111-0101", "646-111-0101"),
        ("646.111.0101", "646-111-0101"),
        ("6461110101", "646-111-0101"),
        ("(646) 111 0101", "646-111-0101"),
        ("abc646xxx111!!0101", "646-111-0101"),
    ],
)
def test_normalize_phone(raw_phone, expected):
    assert normalize_phone(raw_phone) == expected


@pytest.mark.parametrize(
    "value",
    [
        "646 111 0101",
        "(646)-111-0101",
        "646-111-0101",
        "646.111.0101",
        "6461110101",
        "(646) 111 0101",
        "abc646xxx111!!0101",
        "646_111_0101",
        "646--111--0101",
    ],
)
def test_valid_phone_numbers(value):
    assert validate_phone(value)


@pytest.mark.parametrize(
    "value",
    [
        "646-111-010",
        "646-111-01011",
        "703-abc-0373",
        "abc-def-ghij",
        "６４６１１１０１０１",
    ],
)
def test_invalid_phone_numbers(value):
    assert not validate_phone(value)


@pytest.mark.parametrize("value", ["10013", "01234", "00000"])
def test_valid_zip_codes(value):
    assert validate_zipcode(value)


@pytest.mark.parametrize("value", ["1234", "123456", "abcde", "12-34", "1234a", "1 234", "１２３４５"])
def test_invalid_zip_codes(value):
    assert not validate_zipcode(value)


@pytest.mark.parametrize(
    "value",
    [
        "646-111-010",
        "646-111-01011",
        "６４６１１１０１０１",
    ],
)
def test_normalize_phone_rejects_invalid_digit_counts_and_unicode(value):
    with pytest.raises(InvalidRecordError):
        normalize_phone(value)
