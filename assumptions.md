# Assumptions

## Input

- Input files are expected to use UTF-8 encoding.
- Each line represents one record. Blank, malformed, or unsupported lines are considered invalid.
- Spaces around individual fields are removed before processing.
- Names and colors must not be empty. Their original casing is preserved.

## Names

- In Format B, the last word of the combined name is treated as the last name. Everything before it is kept as the first name.
- This allows middle initials to remain part of the first name. For example, "Booker T. Washington" becomes firstname="Booker T." and lastname="Washington".
- Internal spacing and capitalization in names are otherwise preserved.

## Phone numbers

- "Exactly 10 digits" is interpreted as ten characters from `0` to `9`.
- Non-digit characters in the phone field are ignored when counting and normalizing the number.
- Unicode digits are not accepted as phone digits.
- Valid phone numbers are normalized to `XXX-XXX-XXXX`.

## ZIP codes

- ZIP codes must contain exactly five digits from `0` to `9`.
- They are kept as strings so leading zeros are preserved. For example, `01234` remains `01234`.

## Invalid records

- An invalid record does not stop the rest of the file from being processed.
- Blank lines, missing fields, extra fields, invalid phone numbers, invalid ZIP codes, and unsupported formats are recorded as errors.
- Error positions use the original zero-based line number from the input file.

## Other behavior

- Colors are not checked against a predefined list.
- Valid records are sorted by last name and then first name.
- Logs may include line numbers and general error reasons, but never the original record or its personal data.
