import json
import sys

from data_parser.cli import ExitCode, main
from data_parser.pipeline import process_file


def test_process_file_outputs_valid_entries_and_error_lines(tmp_path):
    input_file = tmp_path / "records.txt"
    output_file = tmp_path / "result.json"
    input_file.write_text(
        "Booker T., Washington, 87360, 373 781 7380, yellow\n"
        "Chandler, Kerri, (623)-668-9293, pink, 123123121\n"
        "James Murphy, yellow, 83880, 018 154 6474\n"
        "error500\n",
        encoding="utf-8",
    )

    result = process_file(input_file, output_file)

    expected = {
        "entries": [
            {
                "color": "yellow",
                "firstname": "James",
                "lastname": "Murphy",
                "phonenumber": "018-154-6474",
                "zipcode": "83880",
            },
            {
                "color": "yellow",
                "firstname": "Booker T.",
                "lastname": "Washington",
                "phonenumber": "373-781-7380",
                "zipcode": "87360",
            },
        ],
        "errors": [1, 3],
    }

    assert result == expected
    assert json.loads(output_file.read_text(encoding="utf-8")) == expected


def test_process_file_handles_blank_lines_and_leading_zero_zip(tmp_path):
    input_file = tmp_path / "records.txt"
    output_file = tmp_path / "result.json"
    input_file.write_text(
        "\n"
        "Zed, Alpha, 01234, 123 456 7890, orange\n"
        "Bad, Record, 1234, 123 456 7890, blue\n"
        "\n"
        "Hugh, Grant, 54321, 1112223333, green\n"
        "Bad, Record, 111-222-3333, red, 1234a\n",
        encoding="utf-8",
    )

    result = process_file(input_file, output_file)
    assert result["errors"] == [0, 2, 3, 5]
    assert result["entries"][0]["zipcode"] == "01234"
    assert result["entries"][0]["lastname"] == "Alpha"
    assert result["entries"][1]["lastname"] == "Grant"


def test_json_contract_has_only_entries_and_errors_and_sorted_keys(tmp_path):
    input_file = tmp_path / "records.txt"
    output_file = tmp_path / "result.json"
    input_file.write_text(
        "Washington, Booker T., (703)-742-0996, Blue, 10013\n"
        "Smith, John, (212)-555-0199, Red, 10001\n",
        encoding="utf-8",
    )

    process_file(input_file, output_file)
    text = output_file.read_text(encoding="utf-8")
    data = json.loads(text)
    assert list(data.keys()) == ["entries", "errors"]
    assert list(data["entries"][0].keys()) == [
        "color",
        "firstname",
        "lastname",
        "phonenumber",
        "zipcode",
    ]
    assert "  " in text
    assert "    \"color\": \"Blue\"" in text


def test_cli_without_verbose_keeps_json_unchanged_and_no_info_log(tmp_path, monkeypatch, capsys):
    input_file = tmp_path / "records.txt"
    output_file = tmp_path / "result.json"
    input_file.write_text(
        "Washington, Booker T., (703)-742-0996, Blue, 10013\n"
        "error500\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(sys, "argv", ["prog", str(input_file), "--output", str(output_file)])
    exit_code = main()
    captured = capsys.readouterr()

    assert exit_code is ExitCode.SUCCESS
    assert "Processing summary" not in captured.err
    assert "line_index=1 (0-based)" in captured.err
    data = json.loads(output_file.read_text(encoding="utf-8"))
    assert data["errors"] == [1]
    assert data["entries"][0]["lastname"] == "Washington"


def test_cli_verbose_emits_summary_and_keeps_invalid_records(tmp_path, monkeypatch, capsys):
    input_file = tmp_path / "records.txt"
    output_file = tmp_path / "result.json"
    input_file.write_text(
        "Washington, Booker T., (703)-742-0996, Blue, 10013\n"
        "James Murphy, Red, 11237, 703 955 0373\n"
        "bad record\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        sys,
        "argv",
        ["prog", str(input_file), "--output", str(output_file), "--verbose"],
    )
    main()
    captured = capsys.readouterr()

    assert "Processing summary" in captured.err
    assert "valid records=" in captured.err
    assert "invalid records=" in captured.err
    assert "line_index=2 (0-based)" in captured.err
    assert "invalid record" in captured.err.lower()
    data = json.loads(output_file.read_text(encoding="utf-8"))
    assert data["errors"] == [2]
    assert len(data["entries"]) == 2


def test_cli_logs_controlled_reasons_for_invalid_records(tmp_path, monkeypatch, capsys):
    input_file = tmp_path / "records.txt"
    output_file = tmp_path / "result.json"
    input_file.write_text(
        "Chandler, Kerri, (623)-668-9293, pink, 123123121\n"
        "Washington, Booker T., 703-abc-0996, Blue, 10013\n"
        "error500\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(sys, "argv", ["prog", str(input_file), "--output", str(output_file)])
    main()
    captured = capsys.readouterr()

    assert "line_index=0 (0-based): invalid ZIP code" in captured.err
    assert "line_index=1 (0-based): invalid phone" in captured.err
    assert "line_index=2 (0-based): unsupported format" in captured.err
    data = json.loads(output_file.read_text(encoding="utf-8"))
    assert data == {"entries": [], "errors": [0, 1, 2]}


def test_cli_logs_do_not_expose_input_pii(tmp_path, monkeypatch, capsys):
    input_file = tmp_path / "records.txt"
    output_file = tmp_path / "result.json"
    input_file.write_text(
        "SensitiveLast, SensitiveFirst, 123-456-789, SecretColor, 98765\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(sys, "argv", ["prog", str(input_file), "--output", str(output_file), "--verbose"])
    main()
    captured = capsys.readouterr()

    assert "invalid phone" in captured.err
    for sensitive_value in [
        "SensitiveLast",
        "SensitiveFirst",
        "123-456-789",
        "SecretColor",
        "98765",
    ]:
        assert sensitive_value not in captured.err


def test_cli_missing_input_returns_operational_error_without_traceback(tmp_path, monkeypatch, capsys):
    input_file = tmp_path / "missing.txt"
    output_file = tmp_path / "result.json"

    monkeypatch.setattr(sys, "argv", ["prog", str(input_file), "--output", str(output_file)])
    exit_code = main()
    captured = capsys.readouterr()

    assert exit_code is ExitCode.OPERATIONAL_ERROR
    assert f"ERROR: Input file not found: {input_file}" in captured.err
    assert "Traceback" not in captured.err
    assert not output_file.exists()
