from src.league.league_state import LeagueState


class SleeperLeagueMapper:

    def build_league_state(self, user, league, rosters, players):
        owner_roster = self._find_owner_roster(
            user_id=user["user_id"],
            rosters=rosters,
        )

        roster_players = self._map_player_ids_to_players(
            player_ids=owner_roster.get("players", []),
            players=players,
        )

        starter_ids = self._clean_player_ids(
            owner_roster.get("starters", [])
        )

        bench_ids = self._find_bench_ids(
            roster_ids=owner_roster.get("players", []),
            starter_ids=starter_ids,
        )

        bench_players = self._map_player_ids_to_players(
            player_ids=bench_ids,
            players=players,
        )

        starter_players = self._map_player_ids_to_players(
            player_ids=starter_ids,
            players=players,
        )

        return LeagueState(
            league_id=league["league_id"],
            league_name=league["name"],
            season=int(league["season"]),
            week=1,
            owner_name=user["display_name"],
            owner_team_name=user["display_name"],
            roster=roster_players,
            starters=starter_players,
            bench=bench_players,
            waiver_order=owner_roster.get("settings", {}).get("waiver_position"),
            faab_remaining=owner_roster.get("settings", {}).get("waiver_budget_used"),
        )

    def _find_owner_roster(self, user_id, rosters):
        for roster in rosters:
            if roster.get("owner_id") == user_id:
                return roster

        return {}

    def _map_player_ids_to_players(self, player_ids, players):
        mapped_players = []

        for player_id in player_ids:
            player = players.get(player_id)

            if player:
                mapped_players.append({
                    "player_id": player_id,
                    "full_name": player.get("full_name"),
                    "position": player.get("position"),
                    "team": player.get("team"),
                    "status": player.get("status"),
                    "injury_status": player.get("injury_status"),
                    "fantasy_positions": player.get("fantasy_positions"),
                })

        return mapped_players
    
    def _clean_player_ids(self, player_ids):
        return [
            player_id
            for player_id in player_ids
            if player_id and player_id != "0"
        ]
    
    def _find_bench_ids(self, roster_ids, starter_ids):
        clean_roster_ids = self._clean_player_ids(roster_ids)

        return [
            player_id
            for player_id in clean_roster_ids
            if player_id not in starter_ids
        ]