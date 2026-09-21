import json
from pathlib import Path

from data_parser.errors import InvalidReason, InvalidRecordError
from data_parser.parser import parse_line


def process_file(
    input_path: str | Path,
    output_path: str | Path | None = None,
    invalid_reasons: list[InvalidReason] | None = None,
) -> dict:
    input_file = Path(input_path)
    output_file = Path(output_path) if output_path else Path("result.json")

    valid_records = []
    invalid_line_numbers = []

    with input_file.open("r", encoding="utf-8") as source:
        for line_number, raw_line in enumerate(source):
            try:
                record = parse_line(raw_line.rstrip("\n"))
            except InvalidRecordError as exc:
                invalid_line_numbers.append(line_number)
                if invalid_reasons is not None:
                    invalid_reasons.append(exc.reason)
                continue

            valid_records.append(record)

    valid_records.sort(key=lambda record: (record.lastname, record.firstname))

    payload = {
        "entries": [record.to_dict() for record in valid_records],
        "errors": invalid_line_numbers,
    }

    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("w", encoding="utf-8") as target:
        json.dump(payload, target, indent=2, sort_keys=True)
        target.write("\n")

    return payload
