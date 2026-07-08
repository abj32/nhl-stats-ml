import json
import requests
from pathlib import Path
from datetime import datetime

# Paths
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parents[1]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

# API Config
ENDPOINT = "https://api.nhle.com/stats/rest/en/goalie/summary"
SEASON = "20252026"     # Change to try other seasons
PARAMS = {
    "isAggregate": "false",
    "isGame": "false",  # Season stats instead of game
    "start": 0,
    "limit": -1,   # All goalies
    "factCayenneExp": "gamesPlayed>=10",    # Have played at least 10 games
    "cayenneExp": f"gameTypeId=2 and seasonId={SEASON}" # 2025-2026 regular season points
}

def fetch(endpoint: str):
    print(f"Requesting: {endpoint}")

    r = requests.get(
        endpoint,
        headers={"Accept": "application/json"},
        params=PARAMS
    )
    r.raise_for_status()
    return r.json()

# Saves output to file in json format
def save_output(data, endpoint):
    output_dir = (
        RAW_DATA_DIR
        / "stats"
        / "rest"
        / "en"
        / "goalie"
        / "summary"
        / SEASON
        / "all_goalies"
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"{timestamp}.json"

    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Saved output to {output_path}")

if __name__ == "__main__":
    data = fetch(ENDPOINT)

    print("\nTop-level keys:")
    print(list(data.keys()) if isinstance(data, dict) else type(data))

    save_output(data, ENDPOINT)