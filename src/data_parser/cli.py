import argparse
import logging
import sys
from enum import IntEnum
from pathlib import Path

from data_parser.errors import InvalidReason
from data_parser.pipeline import process_file


logger = logging.getLogger("data_parser")


class ExitCode(IntEnum):
    SUCCESS = 0
    OPERATIONAL_ERROR = 1


def main() -> ExitCode:
    parser = argparse.ArgumentParser(description="Normalize personal records from a text file.")
    parser.add_argument("input_file", help="Path to the input records file")
    parser.add_argument("--output", default="result.json", help="Destination for the JSON output")
    parser.add_argument("--verbose", action="store_true", help="Enable INFO logs for processing summary on stderr")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(levelname)s: %(message)s",
        stream=sys.stderr,
        force=True,
    )

    input_path = Path(args.input_file)
    output_path = Path(args.output)
    invalid_reasons: list[InvalidReason] = []
    try:
        payload = process_file(input_path, output_path, invalid_reasons)
    except FileNotFoundError:
        logger.error("Input file not found: %s", input_path)
        return ExitCode.OPERATIONAL_ERROR
    except OSError as exc:
        logger.error("Unable to process input or output file: %s", exc)
        return ExitCode.OPERATIONAL_ERROR

    invalid_count = len(payload["errors"])
    valid_count = len(payload["entries"])
    total_lines = valid_count + invalid_count

    for line_number, reason in zip(payload["errors"], invalid_reasons):
        logger.warning("Invalid record at line_index=%d (0-based): %s", line_number, reason.value)

    if args.verbose:
        logger.info(
            "Processing summary: total lines=%d, valid records=%d, invalid records=%d, output path=%s",
            total_lines,
            valid_count,
            invalid_count,
            str(output_path),
        )

    return ExitCode.SUCCESS


if __name__ == "__main__":
    raise SystemExit(main())
