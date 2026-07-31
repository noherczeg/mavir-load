# load-chart

## ADDED Requirements

### Requirement: Static interactive chart of the load data
The system SHALL provide a static web page that fetches the stored JSON and
renders an interactive time-series chart, hostable on GitHub Pages with no
backend.

#### Scenario: Chart loads stored data
- **WHEN** the page loads
- **THEN** it fetches the relevant `data/<date>.json` file(s) over HTTP
- **AND** renders the points as an interactive time-series chart

#### Scenario: Present-moment boundary is shown
- **WHEN** the chart is rendered
- **THEN** the boundary between past actuals and future forecast is marked,
  computed as the last timestamp where any actual column is non-null

### Requirement: Pessimistic default series for human readers
The chart SHALL default to the conservative view: maximum for consumption,
minimum for production.

#### Scenario: Default consumption series
- **WHEN** the chart selects its default consumption series
- **THEN** it uses `gross_actual` for the past and `gross_est` for the future
  (gross being the higher, pessimistic figure)

#### Scenario: Default production series
- **WHEN** the chart selects its default production series
- **THEN** it uses `net_plan_gen`

### Requirement: Hungarian user-facing labels
Every user-facing string in the web app SHALL be in Hungarian.

#### Scenario: Labels render in Hungarian
- **WHEN** any axis title, legend entry, series name, tooltip, or boundary
  marker is displayed
- **THEN** its text is Hungarian (e.g. series use MAVIR's Hungarian column
  names; the boundary marker reads "Most")
- **AND** internal data keys remain English and are not shown to the user
