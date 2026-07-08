# NHL Statistics & Machine Learning Project

A Python-based data engineering and machine learning project that collects NHL statistics from the NHL API, processes them into machine-learning-ready datasets, and explores predictive modeling using player and team performance data.

---

## Overview

This project uses NHL API data to build cleaned datasets for statistical analysis and future machine learning experiments.

This project was created to develop practical experience in data engineering, feature engineering, and machine learning using real-world NHL data.

The main goals are to:

* Learn how to work with real-world sports APIs.
* Build reproducible Python data pipelines.
* Practice data cleaning and feature engineering.
* Prepare NHL skater and goalie datasets for future machine learning workflows.
* Develop a portfolio-quality analytics project.

The final machine learning target has not yet been chosen. Potential future directions include:

* Predicting player performance
* Predicting breakout seasons
* Predicting goalie performance
* Predicting team success
* Predicting playoff qualification
* Player similarity analysis and clustering

---

## Current Status

The current stage of the project focuses on data collection, cleaning, standardization, and feature engineering.

The project can currently:

- Fetch NHL skater and goalie statistics for any season available through the NHL API.
- Store raw API responses as JSON files for reproducibility.
- Transform raw API responses into polished player-season datasets.
- Generate machine-learning-ready CSV and Parquet files for all NHL skaters and goalies in a given season.
- Create derived features such as per-game, per-60, workload, efficiency, and point-distribution metrics.

Current processed datasets contain:

- One row per skater-season
- One row per goalie-season
- Core NHL statistics provided by the API
- Engineered features designed for statistical analysis and machine learning

The resulting CSV and Parquet files are intended to serve as the primary datasets for future analysis, visualization, and machine learning experiments.

The final machine learning target has not yet been selected. The current focus is building a reliable and reusable data foundation that can support a variety of future modeling tasks.

---

## Current Workflow

```text
NHL API
    ↓
Raw JSON Storage
    ↓
Data Cleaning & Feature Engineering
    ↓
Machine-Learning-Ready CSV / Parquet Datasets
    ↓
Analysis, Visualization & Modeling
```

---

## Project Structure

```text
nhl-stats/
│
├── README.md
├── requirements.txt
├── .gitignore
│
├── data/
│   ├── raw/
│   └── processed/
│
├── scripts/
│   ├── fetch/
│   └── process/
│
└── notebooks/
```

---

## Data Pipeline

### Raw Data

Location:

```text
data/raw/
```

Raw data stores NHL API responses exactly as received.

Benefits:

* Preserves original API output
* Makes processing reproducible
* Allows processing logic to be changed without re-fetching data
* Makes debugging easier

### Processed Data

Location:

```text
data/processed/
```

Processed data represents the finished analytical layer of the project.

These datasets are designed to be used directly for exploratory analysis, visualization, and machine learning workflows without requiring additional cleaning or feature engineering.

Processing scripts:

* Normalize JSON into tabular datasets
* Standardize column names
* Select relevant statistics
* Generate derived features and rate statistics
* Export CSV and Parquet files

The processed datasets are the primary outputs of the pipeline and are intended to serve as the foundation for future statistical analysis and machine learning experiments.

---

## Current Datasets

### Skaters

* One row per player-season
* Includes all NHL skaters with at least one game played during the selected season
* Contains both NHL API statistics and engineered features

### Goalies

* One row per goalie-season
* Includes all NHL goalies with at least one game played during the selected season
* Contains both NHL API statistics and engineered features

### Data Locations

Raw skater data:
data/raw/stats/rest/en/skater/summary/{season}/all_skaters/

Processed skater data:
data/processed/skaters/

Raw goalie data:
data/raw/stats/rest/en/goalie/summary/{season}/all_goalies/

Processed goalie data:
data/processed/goalies/

---

## NHL API Usage

Primary API hosts:

```text
https://api-web.nhle.com
https://api.nhle.com/stats/rest/en
```

Common report endpoints:

```text
/stats/rest/en/skater/summary
/stats/rest/en/goalie/summary
```

Reference documentation used during development:

https://gitlab.com/dword4/nhlapi
https://gitlab.com/dword4/nhlapi/-/blob/master/new-api.md

### Important API Parameters

#### seasonId

Specifies the NHL season.

Example:

```text
20252026
```

Represents the 2025-2026 NHL season.

#### gameTypeId

Specifies game type.

| Value | Meaning        |
| ----- | -------------- |
| 2     | Regular Season |
| 3     | Playoffs       |

Example:

```text
gameTypeId=2
```

#### cayenneExp

Primary filtering expression.

Example:

```text
gameTypeId=2 and seasonId=20252026
```

Used to filter records returned by the NHL API.

#### factCayenneExp

Fact-level filtering expression.

Example:

```text
gamesPlayed>=1
```

Used to remove players who did not appear in a game.

#### isGame

Controls the granularity of returned records.

| Value | Meaning              |
| ----- | -------------------- |
| false | Season totals        |
| true  | Game-by-game records |

This project currently uses:

```text
isGame=false
```

#### isAggregate

Controls aggregation behavior.

This project currently uses:

```text
isAggregate=false
```

to preserve one row per player-season.

#### sort

Controls API-side sorting.

Useful for leaderboard requests but generally unnecessary when collecting complete player datasets.

#### limit

Controls the number of records returned.

| Example     | Meaning                       |
|-------------|-------------------------------|
| `limit=100` | Returns up to 100 records     |
| `limit=-1`  | Returns all available records |

---

## Processed Skater Dataset

Each row represents one skater-season.

Source endpoint:

```text
/stats/rest/en/skater/summary
```

### Identification Columns

| Column         | Source            | Description                                |
| -------------- | ----------------- | ------------------------------------------ |
| seasonId       | Derived           | Season value enforced by processing script |
| playerId       | API               | Unique NHL player identifier               |
| skaterFullName | API               | Full player name                           |
| lastName       | API               | Player last name                           |
| teamAbbrev     | Renamed API field | Renamed from `teamAbbrevs`                 |
| position       | Renamed API field | Renamed from `positionCode`                |
| shootsCatches  | API               | Shooting handedness                        |

### Usage Columns

| Column        | Source        | Description                                                 |
| ------------- | ------------- | ----------------------------------------------------------- |
| gamesPlayed   | API           | Games played                                                |
| toi_total_sec | Derived       | Estimated total TOI in seconds (`toi_pg_sec × gamesPlayed`) |
| toi_total_min | Derived       | Estimated total TOI in minutes                              |
| toi_pg_sec    | API (renamed) | Time on ice per game in seconds                             |
| toi_pg_min    | Derived       | Time on ice per game in minutes                             |

### Production Columns

| Column  | Source | Description     |
| ------- | ------ | --------------- |
| goals   | API    | Goals           |
| assists | API    | Assists         |
| points  | API    | Goals + assists |
| shots   | API    | Shots on goal   |

### Situation-Specific Production

| Column   | Source | Description          |
| -------- | ------ | -------------------- |
| evGoals  | API    | Even-strength goals  |
| evPoints | API    | Even-strength points |
| ppGoals  | API    | Power-play goals     |
| ppPoints | API    | Power-play points    |
| shGoals  | API    | Short-handed goals   |
| shPoints | API    | Short-handed points  |

### Additional Skater Statistics

| Column         | Source | Description            |
| -------------- | ------ | ---------------------- |
| plusMinus      | API    | Plus-minus rating      |
| penaltyMinutes | API    | Penalty minutes        |
| faceoffWinPct  | API    | Faceoff win percentage |

### Derived Rate Statistics

| Column            | Source  | Description              |
| ----------------- | ------- | ------------------------ |
| points_pg_calc    | Derived | Points per game          |
| points_per_60     | Derived | Points per 60 minutes    |
| goals_pg          | Derived | Goals per game           |
| assists_pg        | Derived | Assists per game         |
| shots_pg          | Derived | Shots per game           |
| shooting_pct_calc | Derived | Shooting percentage      |
| pim_pg            | Derived | Penalty minutes per game |

### Derived Share Statistics

| Column          | Source  | Description                              |
| --------------- | ------- | ---------------------------------------- |
| ev_points_share | Derived | Share of points scored at even strength  |
| pp_points_share | Derived | Share of points scored on the power play |
| sh_points_share | Derived | Share of points scored short-handed      |

### Special Goal Types

| Column           | Source | Description        |
| ---------------- | ------ | ------------------ |
| otGoals          | API    | Overtime goals     |
| gameWinningGoals | API    | Game-winning goals |

---

## Processed Goalie Dataset

Each row represents one goalie-season.

Source endpoint:

```text
/stats/rest/en/goalie/summary
```

### Identification Columns

| Column         | Source            | Description                                |
| -------------- | ----------------- | ------------------------------------------ |
| seasonId       | Derived           | Season value enforced by processing script |
| playerId       | API               | Unique NHL player identifier               |
| goalieFullName | API               | Full goalie name                           |
| lastName       | API               | Goalie last name                           |
| teamAbbrev     | Renamed API field | Renamed from `teamAbbrevs`                 |
| shootsCatches  | API               | Catching hand                              |

### Usage Columns

| Column        | Source        | Description                     |
| ------------- | ------------- | ------------------------------- |
| gamesPlayed   | API           | Games played                    |
| gamesStarted  | API           | Games started                   |
| starts_pct    | Derived       | Starts divided by games played  |
| toi_total_sec | API (renamed) | Total time on ice in seconds    |
| toi_total_min | Derived       | Total time on ice in minutes    |
| toi_pg_sec    | Derived       | Time on ice per game in seconds |
| toi_pg_min    | Derived       | Time on ice per game in minutes |

### Workload Statistics

| Column       | Source | Description   |
| ------------ | ------ | ------------- |
| shotsAgainst | API    | Shots faced   |
| saves        | API    | Saves made    |
| goalsAgainst | API    | Goals allowed |
| shutouts     | API    | Shutouts      |

### Results

| Column   | Source | Description       |
| -------- | ------ | ----------------- |
| wins     | API    | Wins              |
| losses   | API    | Regulation losses |
| otLosses | API    | Overtime losses   |

### Derived Rate Statistics

| Column               | Source  | Description                |
| -------------------- | ------- | -------------------------- |
| save_pct_calc        | Derived | Save percentage            |
| gaa_calc             | Derived | Goals against average      |
| shots_against_pg     | Derived | Shots faced per game       |
| saves_pg             | Derived | Saves per game             |
| goals_against_pg     | Derived | Goals allowed per game     |
| win_pct              | Derived | Win percentage             |
| shots_against_per_60 | Derived | Shots faced per 60 minutes |
| saves_per_60         | Derived | Saves per 60 minutes       |

### Additional Statistics

| Column         | Source | Description     |
| -------------- | ------ | --------------- |
| penaltyMinutes | API    | Penalty minutes |
| assists        | API    | Assists         |

---

## File Formats

Processed datasets are saved as both CSV and Parquet.

### CSV

Benefits:

* Human-readable
* Easy to inspect
* Supported by spreadsheets and most tools

### Parquet

Benefits:

* Smaller file sizes
* Faster reads and writes
* Preserves data types
* Better suited for analytics and machine learning workflows

---

## Environment Setup

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it.

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Update requirements after adding packages:

```bash
pip freeze > requirements.txt
```

---

## Future Work

Potential future additions include:

* Multi-season dataset generation
* Team-level feature engineering
* Historical standings integration
* Automated data refresh pipelines
* Exploratory data analysis notebooks
* Machine learning model development
* Model evaluation and comparison
* Visualization dashboards