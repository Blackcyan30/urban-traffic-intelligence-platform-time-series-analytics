# Urban Traffic Intelligence Platform (Time-Series Analytics)

A Python + SQL command-line app for analyzing Chicago traffic camera data.

It lets you query red-light and speed-camera violations over time, compare trends, and inspect camera activity by location, date, month, and year.

## What the App Does

The app supports these workflows:

1. Find intersections by name (supports SQL wildcards)
2. Find all cameras at a specific intersection
3. Compare red-light vs. speed violation percentages for a specific date
4. Show number of cameras at each intersection
5. Show number of violations by intersection for a given year
6. Show yearly violations for a camera ID
7. Show monthly violations for a camera ID and year
8. Compare daily red-light vs. speed violations for a year
9. Find cameras on a street and optionally plot them on a Chicago map

## Dataset Summary

- Intersections: 251
- Red-light cameras: 365
- Speed cameras: 184
- Red violation records: 998,470
- Speed violation records: 408,256
- Total time-series records: 1,406,726
- Date range: 2014-07-01 to 2024-11-28
- Total violations counted: 22,983,611

Tables used:

- `Intersections`
- `RedCameras`
- `SpeedCameras`
- `RedViolations`
- `SpeedViolations`

## How It Works

- Connects to a local SQLite database (`chicago-traffic-cameras.db`)
- Runs parameterized SQL queries for filtering and aggregation
- Uses time bucketing with `strftime(...)` for daily/monthly/yearly rollups
- Prints results in the terminal and can generate optional plots with Matplotlib

### Example Query Pattern

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
- SQL
- SQLite
- Matplotlib

## Run Locally

### Prerequisites

- Python 3.10+
- `matplotlib`

### Install

```bash
pip install matplotlib
```

### Run

```bash
python3 main.py
```

## Project Files

- `main.py` — CLI logic and SQL workflows
- `chicago-traffic-cameras.db` — SQLite database
