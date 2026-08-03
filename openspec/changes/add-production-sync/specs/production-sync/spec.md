# production-sync

## ADDED Requirements

### Requirement: Fetch the MAVIR production export alongside load
The system SHALL fetch the MAVIR production (generation) export (chart `4401`)
on the same schedule and for the same previous-12h-through-next-12h window in
`Europe/Budapest` as the existing load export, using `periodType=min` and
`period=15`.

#### Scenario: Production export is fetched each run
- **WHEN** the sync job runs
- **THEN** it requests the `4401` export for the same ±12h window as `7678`
- **AND** it requests it with `periodType=min` and `period=15`

### Requirement: Parse and normalize the production export
The system SHALL parse the `4401` xlsx and normalize each row into fields with
ISO-8601 timestamps and stable `prod_*` keys distinct from the load keys.

#### Scenario: Production column mapping
- **WHEN** a `4401` data row is parsed
- **THEN** columns map to keys: B→`prod_gross_plan`, C→`prod_gross_actual`,
  D→`prod_net_plan`, E→`prod_net_actual`
- **AND** the timestamp column A maps to the shared `t` key
- **AND** empty cells become explicit `null`

### Requirement: Independent per-chart failure isolation
The system SHALL fetch each chart independently so a failure of one chart does
not prevent committing fresh data from the other.

#### Scenario: One chart fails, the other still commits
- **WHEN** the `4401` fetch or parse fails after its retries but `7678` succeeds
- **THEN** the run logs the `4401` failure and skips it
- **AND** the `7678` points are still upserted and committed
- **AND** existing `prod_*` values in storage are left unchanged (never
  overwritten with null)

### Requirement: Production fields merge into the same daily storage
The system SHALL merge production fields into the same
`data/<YYYY-MM-DD>.json` point objects as load, matched by the shared `t`
timestamp, preferring newer non-null values.

#### Scenario: Production fields join an existing load point
- **WHEN** a fetched `4401` point shares a timestamp with a stored point
- **THEN** its `prod_*` fields are merged into that point
- **AND** a non-null stored field is NEVER overwritten with a null value

### Requirement: Per-chart run outcome is observable
The system SHALL log which charts succeeded and how many points each yielded.

#### Scenario: Per-chart summary
- **WHEN** a run completes
- **THEN** it logs, per chart, whether the fetch succeeded and the point count
