# load-chart

## MODIFIED Requirements

### Requirement: Pessimistic default series for human readers
The chart SHALL default to the conservative view: maximum for consumption,
minimum for production, using real production actuals when available.

#### Scenario: Default consumption series
- **WHEN** the chart selects its default consumption series
- **THEN** it uses `gross_actual` for the past and `gross_est` for the future
  (gross being the higher, pessimistic figure)

#### Scenario: Default production series
- **WHEN** the chart selects its default production series
- **THEN** it uses `prod_gross_actual` for the past and `prod_gross_plan` for
  the future (keeping the gross family consistent across the actual→plan handoff)

## ADDED Requirements

### Requirement: Production series overlay
The chart SHALL overlay the MAVIR production (generation) series from the
`prod_*` fields on the same time axis and MW value axis as the load series,
using the existing per-series toggle and persistence.

#### Scenario: Production series render alongside load
- **WHEN** the page loads a day whose points contain `prod_*` fields
- **THEN** the production series are drawn on the same chart as the load series
- **AND** each is individually toggleable, with visibility persisted by key

#### Scenario: Present-moment boundary includes production actuals
- **WHEN** the boundary between past actuals and future forecast is computed
- **THEN** `prod_gross_actual` is included among the actual columns that
  determine the last non-null actual timestamp

### Requirement: Hungarian labels for production series
Every production series' user-facing label SHALL be in Hungarian, using MAVIR's
exact column names.

#### Scenario: Production labels render in Hungarian
- **WHEN** a production series' legend entry, tooltip, or name is displayed
- **THEN** its text is Hungarian (e.g. `prod_gross_actual` →
  "Bruttó tény erőművi termelés")
- **AND** the internal `prod_*` keys are not shown to the user
