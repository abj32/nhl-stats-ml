import json
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np

# Paths
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parents[1]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

BASE_RAW = RAW_DATA_DIR / "stats" / "rest" / "en" / "goalie" / "summary"
BASE_OUT = PROCESSED_DIR / "goalies"


def load_latest_json(raw_folder: Path) -> dict:
    """
    Loads the most recent JSON file in raw_folder by filename sort (timestamped).
    Assumes files are saved as YYYYMMDD_HHMMSS.json
    """
    if not raw_folder.exists():
        raise FileNotFoundError(f"Raw folder not found: {raw_folder}")

    json_files = sorted(raw_folder.glob("*.json"))
    if not json_files:
        raise FileNotFoundError(f"No .json files found in: {raw_folder}")

    latest = json_files[-1]
    with open(latest, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data


def process_goalies(season: str) -> pd.DataFrame:
    raw_folder = BASE_RAW / season / "all_goalies"
    payload = load_latest_json(raw_folder)

    if "data" not in payload or not isinstance(payload["data"], list):
        raise ValueError(f"Unexpected JSON shape. Expected key 'data' as list. Keys: {list(payload.keys())}")


    df = pd.json_normalize(payload["data"])

    # --- Standardize names ---
    if "teamAbbrevs" in df.columns:
        df = df.rename(columns={"teamAbbrevs": "teamAbbrev"})

    # --- Coerce numeric columns ---
    numeric_cols = [
        "assists", "gamesPlayed", "gamesStarted", "goals",
        "goalsAgainst", "goalsAgainstAverage", "losses",
        "otLosses", "penaltyMinutes", "points", "savePct",
        "saves", "shotsAgainst", "shutouts", "timeOnIce",
        "wins"
    ]

    for c in numeric_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # --- Time on ice ---
    df["toi_total_sec"] = df["timeOnIce"]
    df["toi_total_min"] = df["toi_total_sec"] / 60.0
    df["toi_pg_sec"] = df["toi_total_sec"] / df["gamesPlayed"]
    df["toi_pg_min"] = df["toi_pg_sec"] / 60

    # starts percentage
    df["starts_pct"] = df["gamesStarted"] / df["gamesPlayed"]

    # per-60 workload stats
    toi = df["toi_total_sec"].replace(0, np.nan)
    df["shots_against_per_60"] = df["shotsAgainst"] * 3600 / toi
    df["saves_per_60"] = df["saves"] * 3600 / toi

    # --- Compute rate stats (keep API versions too) ---
    # API versions for validation
    df["save_pct_api"] = df["savePct"]
    df["gaa_api"] = df["goalsAgainstAverage"]

    # save percentage
    df["save_pct_calc"] = df["saves"] / df["shotsAgainst"]
    # goals against average 
    df["gaa_calc"] = (df["goalsAgainst"] * 3600) / df["timeOnIce"]

    # shots against per game
    df["shots_against_pg"] = df["shotsAgainst"] / df["gamesPlayed"]
    # saves per game
    df["saves_pg"] = df["saves"] / df["gamesPlayed"]
    # goals against per game
    df["goals_against_pg"] = df["goalsAgainst"] / df["gamesPlayed"]

    # win percentage
    df["win_pct"] = df["wins"] / df["gamesPlayed"]

    # --- Ensure season column exists and is consistent ---
    df["seasonId"] = season     # overwrite with the argument for consistency

    # --- Column order ---
    preferred = [
        "seasonId", "playerId", "goalieFullName", "lastName",
        "teamAbbrev", "shootsCatches",
        "gamesPlayed", "gamesStarted", "starts_pct",
        "toi_total_sec", "toi_total_min", "toi_pg_sec", "toi_pg_min",
        "shotsAgainst", "saves", "goalsAgainst", "shutouts",
        "wins", "losses", "otLosses",
        "save_pct_calc", "gaa_calc", "shots_against_pg", "saves_pg", "goals_against_pg", "win_pct",
        "shots_against_per_60", "saves_per_60",
        "penaltyMinutes", "assists"
    ]

    cols = [c for c in preferred if c in df.columns]
    return df[cols]


def save_outputs(df: pd.DataFrame, season: str):
    BASE_OUT.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = BASE_OUT / f"goalies_{season}_all_goalies_{stamp}.csv"
    parquet_path = BASE_OUT / f"goalies_{season}_all_goalies_{stamp}.parquet"

    df.to_csv(csv_path, index=False)
    df.to_parquet(parquet_path, index=False)

    print(f"Saved CSV: {csv_path}")
    print(f"Saved Parquet: {parquet_path}")
    print(f"Rows: {len(df):,}  Columns: {df.shape[1]}")


if __name__ == "__main__":
    SEASON = "20252026"

    df_goalies = process_goalies(SEASON)
    save_outputs(df_goalies, SEASON)
