from enum import StrEnum


class InvalidReason(StrEnum):
    INVALID_RECORD = "invalid record"
    INVALID_PHONE = "invalid phone"
    INVALID_ZIP = "invalid ZIP code"
    MALFORMED_CSV = "malformed CSV"
    UNSUPPORTED_FORMAT = "unsupported format"


class InvalidRecordError(ValueError):
    """Raised when a record cannot be parsed or validated."""

    def __init__(self, message: str, reason: InvalidReason = InvalidReason.INVALID_RECORD):
        super().__init__(message)
        self.reason = reason
