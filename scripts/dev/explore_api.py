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
BASE_URL = "https://api.nhle.com"
ENDPOINT = "/stats/rest/en/skater/summary"
SEASON = "20252026"     # Change to try other seasons
PARAMS = {
    "isAggregate": "false",
    "isGame": "false",  # Season stats instead of game
    "start": 0,
    "limit": -1,   # All players
    "factCayenneExp": "gamesPlayed>=1",
    "cayenneExp": f"gameTypeId=2 and seasonId={SEASON}" # 2025-2026 regular season points
}

def fetch(endpoint: str):
    url = BASE_URL + ENDPOINT
    print(f"Requesting: {url}")

    r = requests.get(
        url,
        headers={"Accept": "application/json"},
        params=PARAMS
    )
    r.raise_for_status()
    return r.json()

# Saves output to file in json format
def save_output(data, endpoint):
    safe_name = endpoint.strip("/").replace("/", "_")
    endpoint_dir = RAW_DATA_DIR / safe_name
    endpoint_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = endpoint_dir / f"{timestamp}.json"

    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Saved output to {output_path}")

if __name__ == "__main__":
    print("Project root:", PROJECT_ROOT)
    print("Saving to:", RAW_DATA_DIR)

    data = fetch(ENDPOINT)

    print("\nTop-level keys:")
    print(list(data.keys()) if isinstance(data, dict) else type(data))

    save_output(data, ENDPOINT)