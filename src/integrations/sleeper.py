import requests

BASE_URL = "https://api.sleeper.app/v1"


class SleeperClient:

    def __init__(self):
        self.base_url = BASE_URL

    def get_user(self, username: str):
        response = requests.get(
            f"{self.base_url}/user/{username}"
        )
        response.raise_for_status()
        return response.json()

    def get_user_leagues(
        self,
        user_id: str,
        season: int
    ):
        response = requests.get(
            f"{self.base_url}/user/{user_id}/leagues/nfl/{season}"
        )
        response.raise_for_status()
        return response.json()

    def get_rosters(
        self,
        league_id: str
    ):
        response = requests.get(
            f"{self.base_url}/league/{league_id}/rosters"
        )
        response.raise_for_status()
        return response.json()

    def get_users(
        self,
        league_id: str
    ):
        response = requests.get(
            f"{self.base_url}/league/{league_id}/users"
        )
        response.raise_for_status()
        return response.json()

    def get_matchups(
        self,
        league_id: str,
        week: int
    ):
        response = requests.get(
            f"{self.base_url}/league/{league_id}/matchups/{week}"
        )
        response.raise_for_status()
        return response.json()
    
    def get_players(self):
        response = requests.get(
            "https://api.sleeper.app/v1/players/nfl"
        )
        response.raise_for_status()
        return response.json()
    
    