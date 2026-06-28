import requests
import pandas as pd


SLEEPER_PLAYERS_URL = "https://api.sleeper.app/v1/players/nfl"


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


if __name__ == "__main__":
    players = fetch_nfl_players()
    clean_players = clean_player_data(players)

    print(clean_players.head())
    print(f"Total players pulled: {len(clean_players)}")