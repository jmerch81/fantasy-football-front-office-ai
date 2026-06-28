import requests
import pandas as pd

from pathlib import Path


SLEEPER_PLAYERS_URL = "https://api.sleeper.app/v1/players/nfl"

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"

RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

def fetch_nfl_players():
    """
    Pull NFL player data from the Sleeper API.
    """
    response = requests.get(SLEEPER_PLAYERS_URL)

    if response.status_code != 200:
        raise Exception(f"API request failed with status code {response.status_code}")

    players_json = response.json()

    players_df = pd.DataFrame.from_dict(players_json, orient="index")

    return players_df


def clean_player_data(players_df):
    """
    Keep the columns we care about for fantasy football analysis.
    """
    columns_to_keep = [
        "player_id",
        "full_name",
        "first_name",
        "last_name",
        "position",
        "team",
        "status",
        "injury_status",
        "age",
        "years_exp",
        "height",
        "weight",
        "college",
        "fantasy_positions",
    ]

    available_columns = [col for col in columns_to_keep if col in players_df.columns]

    clean_df = players_df[available_columns].copy()

    return clean_df

def validate_player_data(players_df):
    """
    Validate that the dataset contains the required columns
    and enough records for downstream processing.
    """

    required_columns = [
        "player_id",
        "full_name",
        "position",
        "team",
    ]

    missing_columns = [
        col for col in required_columns
        if col not in players_df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    if len(players_df) < 1000:
        raise ValueError(
            "Player dataset appears incomplete."
        )

    print("✅ Data validation passed.")

if __name__ == "__main__":
    print("Starting Sleeper API player data pipeline...")

    players = fetch_nfl_players()
    print(f"Raw players pulled: {len(players)}")

    clean_players = clean_player_data(players)
    validate_player_data(clean_players)
    print(f"Clean players created: {len(clean_players)}")

    players.to_csv(RAW_DATA_DIR / "sleeper_players_raw.csv", index=False)
    clean_players.to_csv(PROCESSED_DATA_DIR / "sleeper_players_clean.csv", index=False)

    print("Files saved successfully.")
    print(clean_players.head())