import json
import requests
from pathlib import Path
from datetime import datetime

# Paths
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parents[1]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

# API Config
BASE_URL = "https://api-web.nhle.com"
TEAM_ABBR = "PHI"       # Change this line to try different teams
SEASON = "20252026"     # Change this line to try different seasons
ENDPOINT = f"/v1/roster/{TEAM_ABBR}/{SEASON}"

def fetch(endpoint: str):
    url = BASE_URL + endpoint
    print(f"Requesting: {url}")

    r = requests.get(
        url,
        headers={"Accept": "application/json"}
    )
    r.raise_for_status()
    return r.json()

# Saves output to file in json format
def save_output(data, team: str, season: str):
    output_dir = (
        RAW_DATA_DIR
        / "v1"
        / "roster"
        / team.upper()
        / season
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
    print(list(data.keys()))

    save_output(data, TEAM_ABBR, SEASON)