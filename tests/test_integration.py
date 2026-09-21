import json
from pathlib import Path

from data_parser.pipeline import process_file


FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_challenge_fixture_end_to_end(tmp_path):
    input_file = FIXTURES_DIR / "challenge_input.txt"
    expected_file = FIXTURES_DIR / "challenge_expected.json"
    output_file = tmp_path / "result.json"

    process_file(input_file, output_file)

    actual_text = output_file.read_text(encoding="utf-8")
    expected_text = expected_file.read_text(encoding="utf-8")

    assert json.loads(actual_text) == json.loads(expected_text)
    assert actual_text == expected_text
