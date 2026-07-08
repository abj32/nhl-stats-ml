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

BASE_RAW = RAW_DATA_DIR / "stats" / "rest" / "en" / "skater" / "summary"
BASE_OUT = PROCESSED_DIR / "skaters"


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


def process_skaters(season: str) -> pd.DataFrame:
    raw_folder = BASE_RAW / season / "all_skaters"
    payload = load_latest_json(raw_folder)

    if "data" not in payload or not isinstance(payload["data"], list):
        raise ValueError(f"Unexpected JSON shape. Expected key 'data' as list. Keys: {list(payload.keys())}")

    df = pd.json_normalize(payload["data"])

    # --- Standardize names ---
    if "teamAbbrevs" in df.columns:
        df = df.rename(columns={"teamAbbrevs": "teamAbbrev"})

    if "positionCode" in df.columns and "position" not in df.columns:
        df = df.rename(columns={"positionCode": "position"})

    # --- Coerce numeric fields where possible ---
    numeric_cols = [
        "assists", "evGoals", "evPoints", "faceoffWinPct", "gameWinningGoals",
        "gamesPlayed", "goals", "otGoals", "penaltyMinutes", "plusMinus", "points",
        "pointsPerGame", "ppGoals", "ppPoints", "shGoals", "shPoints",
        "shootingPct", "shots", "timeOnIcePerGame"
    ]

    for c in numeric_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # --- Time on ice ---
    df["toi_pg_sec"] = df["timeOnIcePerGame"]
    df["toi_pg_min"] = df["toi_pg_sec"] / 60.0
    df["toi_total_sec"] = df["toi_pg_sec"] * df["gamesPlayed"]
    df["toi_total_min"] = df["toi_total_sec"] / 60.0

    # --- Compute rate stats (keep API versions too) ---
    # API versions for validation
    df["points_pg_api"] = df["pointsPerGame"]
    df["shooting_pct_api"] = df["shootingPct"]

    # points per game
    df["points_pg_calc"] = df["points"] / df["gamesPlayed"]
    # goals per game
    df["goals_pg"] = df["goals"] / df["gamesPlayed"]
    # assists per game
    df["assists_pg"] = df["assists"] / df["gamesPlayed"]

    # shots per game
    df["shots_pg"] = df["shots"] / df["gamesPlayed"]
    # shooting percentage (shots can be 0)
    df["shooting_pct_calc"] = df["goals"] / df["shots"].replace(0, np.nan)

    # penalty minutes per game
    df["pim_pg"] = df["penaltyMinutes"] / df["gamesPlayed"]

    # points per 60
    df["points_per_60"] = df["points"] * 3600 / df["toi_total_sec"]

    # points shares (points can be 0)
    df["ev_points_share"] = df["evPoints"] / df["points"].replace(0, np.nan)
    df["pp_points_share"] = df["ppPoints"] / df["points"].replace(0, np.nan)
    df["sh_points_share"] = df["shPoints"] / df["points"].replace(0, np.nan)

    # --- Ensure season column exists and is consistent ---
    df["seasonId"] = season  # overwrite with the argument for consistency

    # --- Column order ---
    preferred = [
        "seasonId", "playerId", "skaterFullName", "lastName",
        "teamAbbrev", "position", "shootsCatches",
        "gamesPlayed", "toi_total_sec", "toi_total_min", "toi_pg_sec", "toi_pg_min",
        "goals", "assists", "points", "shots",
        "evGoals", "evPoints", "ppGoals", "ppPoints", "shGoals", "shPoints",
        "plusMinus", "penaltyMinutes", "faceoffWinPct",
        "points_pg_calc", "points_per_60", "goals_pg", "assists_pg", "shots_pg", "shooting_pct_calc", "pim_pg",
        "ev_points_share", "pp_points_share", "sh_points_share",
        "otGoals", "gameWinningGoals",
    ]
    cols = [c for c in preferred if c in df.columns]
    return df[cols]


def save_outputs(df: pd.DataFrame, season: str):
    BASE_OUT.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = BASE_OUT / f"skaters_{season}_all_skaters_{stamp}.csv"
    parquet_path = BASE_OUT / f"skaters_{season}_all_skaters_{stamp}.parquet"

    df.to_csv(csv_path, index=False)
    df.to_parquet(parquet_path, index=False)

    print(f"Saved CSV: {csv_path}")
    print(f"Saved Parquet: {parquet_path}")
    print(f"Rows: {len(df):,}  Columns: {df.shape[1]}")


if __name__ == "__main__":
    SEASON = "20252026"

    skaters_df = process_skaters(SEASON)
    save_outputs(skaters_df, SEASON)