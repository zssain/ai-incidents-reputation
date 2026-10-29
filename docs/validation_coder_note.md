# Validation coding — 20 rows

Please code every row in validation_remaining20_human.csv, using only coding_manual_v3.md and the original incident reports.

- Open each row's incident_url and read the incident and enough linked reports to decide. Some titles are shortened, so do not code from the title alone (§4).
- Fill correct_ticker, responsibility_type, duplicate_of, corrected_event_date, keep and reason in the order set out in §5. Leave optional fields blank where the manual requires it.
- If date_flag has a value, check the date as described in §13. Enter a corrected date only if the listed date is wrong. Follow §13 also if the original report date is missing.
- keep is mechanical: Y only if type is 1, ticker is Y and the incident is not a duplicate (§14).
- If unsure, start reason with "UNCERTAIN:".
- If you can't open or read a source, write UNREADABLE in reason, leave every other coding field blank, and don't guess (§4).
- Work independently. Do not inspect other coders' or AI labels, repository validation results, or adjudication records, and do not discuss rows until returning the file.
- Return a separate file, for example validation_remaining20_human_completed.csv.
