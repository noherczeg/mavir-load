# load-sync

## ADDED Requirements

### Requirement: Periodic fetch of the MAVIR export
The system SHALL fetch the MAVIR xlsx export on a schedule of every 30 minutes,
covering a window of the previous 12 hours through the next 12 hours relative to
the current time in `Europe/Budapest`.

#### Scenario: Scheduled run computes the ±12h window
- **WHEN** the sync job runs
- **THEN** it computes `fromTime = now - 12h` and `toTime = now + 12h` as epoch
  milliseconds using a timezone-aware `Europe/Budapest` `now`
- **AND** it requests the export with `periodType=min` and `period=15`

#### Scenario: Fetch retries on failure
- **WHEN** a fetch attempt returns a non-200 status, times out, or yields a body
  that cannot be parsed as an xlsx
- **THEN** the job retries
- **AND** it makes at most 3 total attempts (1 initial + 2 retries)
- **AND** if all attempts fail it exits with a non-zero status

### Requirement: Parse and normalize the export
The system SHALL parse the xlsx and normalize each row into a point with ISO-8601
timestamps and stable English field keys.

#### Scenario: Timestamp normalization
- **WHEN** a cell timestamp `2026.07.31 01:15:00 +0200` is read
- **THEN** it is normalized to `2026-07-31T01:15:00+02:00`

#### Scenario: Column mapping
- **WHEN** a data row is parsed
- **THEN** columns map to keys: F→`gross_actual`, C→`gross_est`,
  I→`net_load`, J→`net_actual`, K→`net_est`, D→`net_plan_gen`,
  E→`net_plan_load`, G→`gross_plan`
- **AND** empty cells become explicit `null`
- **AND** the certified columns B and H are ignored in v1

### Requirement: Upsert into versioned daily JSON storage
The system SHALL store points in `data/<YYYY-MM-DD>.json` (Europe/Budapest day),
merging by timestamp and preferring newer non-null values, without a database.

#### Scenario: New point is inserted
- **WHEN** a fetched point has a timestamp not yet present in the day's file
- **THEN** the point is appended in chronological order

#### Scenario: Existing point is upserted preferring non-null
- **WHEN** a fetched point matches an existing timestamp
- **THEN** each null field in the stored point is filled from the fetched point
- **AND** a non-null stored field is NEVER overwritten with a null fetched value

#### Scenario: Commit only on change
- **WHEN** a run produces no change to any `data/*.json` file
- **THEN** no git commit is created

### Requirement: Run failure is observable
The system SHALL surface run failures so an operator can tell what happened.

#### Scenario: Failure signal
- **WHEN** a run fails after all retries
- **THEN** it logs the reason (status/timeout/parse) and exits non-zero so the
  CI scheduler reports the failure
