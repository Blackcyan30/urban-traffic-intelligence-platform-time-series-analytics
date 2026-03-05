# Urban Traffic Intelligence Platform (Time-Series Analytics)

Interactive Python + SQL analytics tool for exploring Chicago traffic camera data at city scale.

This project analyzes red-light and speed-camera violations over time, helps identify operational hotspots, and supports data-driven decision making through query-driven reports and optional visualizations.

## Why This Project Matters

- Demonstrates practical SQL analytics on a large, real-world dataset.
- Shows end-to-end data workflow: querying, aggregation, time-series analysis, and visualization.
- Highlights skills relevant to data, backend, and analytics roles: Python, SQL, metrics, and reporting.

## What It Does

The CLI application provides 9 workflows:

1. Find intersections by name (supports SQL wildcards).
2. Find all cameras at a specific intersection.
3. Compute red-light vs. speed violation percentages for a specific date.
4. Report number of cameras at each intersection.
5. Report number of violations by intersection for a given year.
6. Report yearly violations for a camera ID.
7. Report monthly violations for a camera ID and year.
8. Compare daily red-light vs. speed violations for a year.
9. Find cameras on a given street and optionally plot them on a Chicago map.

## Dataset At a Glance

- Intersections: 251
- Red-light cameras: 365
- Speed cameras: 184
- Red violation records: 998,470
- Speed violation records: 408,256
- Total time-series records: 1,406,726
- Date range: 2014-07-01 to 2024-11-28
- Total violations analyzed: 22,983,611

Data source tables:

- `Intersections`
- `RedCameras`
- `SpeedCameras`
- `RedViolations`
- `SpeedViolations`

## How It Works (High Level)

1. Connects to a local SQLite database (`chicago-traffic-cameras.db`).
2. Uses parameterized SQL queries for filtering and aggregation.
3. Applies time bucketing with `strftime(...)` to produce daily/monthly/yearly insights.
4. Prints tabular summaries in the terminal and optionally renders plots with Matplotlib.

## Example SQL Patterns Used

- Aggregations: `SUM`, `COUNT`, `AVG`
- Joins across camera/intersection/violation tables
- Set operations: `UNION ALL`
- Time bucketing: `strftime('%Y', Violation_Date)`, `strftime('%m', Violation_Date)`, `strftime('%Y-%m-%d', Violation_Date)`
- Parameterized filtering (`?`) for safer, reusable query logic

Example:

```sql
SELECT strftime('%Y', Violation_Date) AS year, SUM(Num_Violations) AS total_violations
FROM (
  SELECT Violation_Date, Num_Violations FROM RedViolations WHERE Camera_ID = ?
  UNION ALL
  SELECT Violation_Date, Num_Violations FROM SpeedViolations WHERE Camera_ID = ?
)
GROUP BY year
ORDER BY year ASC;
```

## Tech Stack

- Python
- SQLite
- SQL
- Matplotlib

## Run Locally

### Prerequisites

- Python 3.10+ (or compatible)
- `matplotlib`
- SQLite DB file included in this repo

### Install dependency

```bash
pip install matplotlib
```

### Run

```bash
python3 main.py
```

## Repository Structure

- `main.py`: Main CLI application logic and SQL-driven workflows
- `chicago-traffic-cameras.db`: SQLite dataset
- `chicago.png`: Optional base map for street camera plotting
- `Project 01 - Chicago Traffic Camera Analysis(1).pdf`: Project specification and expected behavior

## Reference

- Project specification PDF: [Project 01 - Chicago Traffic Camera Analysis(1).pdf](./Project%2001%20-%20Chicago%20Traffic%20Camera%20Analysis(1).pdf)

