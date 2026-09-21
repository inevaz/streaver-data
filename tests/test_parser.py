import pytest

from data_parser.errors import InvalidRecordError
from data_parser.models import PersonRecord
from data_parser.parser import parse_line


def test_parse_format_a():
    record = parse_line("Washington, Booker T., (703)-742-0996, Blue, 10013")
    assert record == PersonRecord(
        firstname="Booker T.",
        lastname="Washington",
        phonenumber="703-742-0996",
        color="Blue",
        zipcode="10013",
    )


def test_parse_format_b():
    record = parse_line("James Murphy, Red, 11237, 703 955 0373")
    assert record == PersonRecord(
        firstname="James",
        lastname="Murphy",
        phonenumber="703-955-0373",
        color="Red",
        zipcode="11237",
    )


def test_parse_format_b_with_middle_initial():
    record = parse_line("Booker T. Washington, Blue, 10013, (703)-742-0996")
    assert record == PersonRecord(
        firstname="Booker T.",
        lastname="Washington",
        phonenumber="703-742-0996",
        color="Blue",
        zipcode="10013",
    )


def test_parse_format_c():
    record = parse_line("Kerri, Chandler, 10013, 646 111 0101, Green")
    assert record == PersonRecord(
        firstname="Kerri",
        lastname="Chandler",
        phonenumber="646-111-0101",
        color="Green",
        zipcode="10013",
    )


def test_parse_format_c_allows_color_that_looks_like_zip():
    record = parse_line("Kerri, Chandler, 10013, 646 111 0101, 12345")
    assert record.color == "12345"
    assert record.firstname == "Kerri"
    assert record.lastname == "Chandler"


def test_parse_format_c_allows_color_that_looks_like_phone():
    record = parse_line("Kerri, Chandler, 10013, 646 111 0101, (212)-555-0199")
    assert record.color == "(212)-555-0199"
    assert record.phonenumber == "646-111-0101"


@pytest.mark.parametrize(
    ("value", "expected_phone"),
    [
        ("Washington, Booker T., abc703xxx742!!0996, Blue, 10013", "703-742-0996"),
        ("James Murphy, Red, 11237, 703.955.0373", "703-955-0373"),
        ("Kerri, Chandler, 10013, abc646xxx111!!0101, 12345", "646-111-0101"),
    ],
    ids=["format-a", "format-b", "format-c-with-zip-like-color"],
)
def test_format_detection_is_independent_of_phone_separators(value, expected_phone):
    assert parse_line(value).phonenumber == expected_phone


@pytest.mark.parametrize(
    "value",
    [
        "Washington, Booker T., (703)-742-099x, Blue, 10013",
        "Washington, Booker T., (703)-742-0996, Blue, 1001x",
        "James Murphy, Red, 11237, 703 955 037x",
        "James Murphy, Red, 1123x, 703 955 0373",
        "Kerri, Chandler, 10013, 646 111 010x, Green",
        "Kerri, Chandler, 1001x, 646 111 0101, Green",
    ],
    ids=[
        "format-a-invalid-phone",
        "format-a-invalid-zip",
        "format-b-invalid-phone",
        "format-b-invalid-zip",
        "format-c-invalid-phone",
        "format-c-invalid-zip",
    ],
)
def test_supported_formats_reject_invalid_phone_or_zip(value):
    with pytest.raises(InvalidRecordError):
        parse_line(value)


@pytest.mark.parametrize(
    "value",
    [
        "error500",
        "",
        " ",
        "Alpha, Beta, Gamma, Delta",
        '"Booker T., Washington, 87360, 373 781 7380, yellow',
        "Alpha,Beta,10013,703 123 4567,Red,extra",
        "Washington, Booker T., 703-742-0996, Blue, 1234",
        "Washington, Booker T., (703)-742-099x, Blue, 10013",
    ],
)
def test_parse_invalid_record_raises(value):
    with pytest.raises(InvalidRecordError):
        parse_line(value)
