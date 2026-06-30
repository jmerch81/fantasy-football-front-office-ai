from src.integrations.sleeper import SleeperClient
from src.league.sleeper_mapper import SleeperLeagueMapper

client = SleeperClient()

username = input("Sleeper Username: ")

user = client.get_user(username)

print(user)

print()

print("Welcome")

print(user["display_name"])

print()

leagues = client.get_user_leagues(
    user["user_id"],
    2026
)

print("Your Leagues")

league = leagues[0]

print(league["name"])

print()

print("Loading roster...")

rosters = client.get_rosters(
    league["league_id"]
)

print(rosters)

print()

print("Loading NFL player database...")

players = client.get_players()

print(f"Loaded {len(players)} players.")

sample_id = next(iter(players))
sample_player = players[sample_id]

print()
print("Sample Player")
print("----------------")
print("ID:", sample_id)
print("Name:", sample_player.get("full_name"))
print("Position:", sample_player.get("position"))
print("Team:", sample_player.get("team"))

for league in leagues:
    print(
        league["name"],
        league["league_id"]
    )

mapper = SleeperLeagueMapper()

league_state = mapper.build_league_state(
    user=user,
    league=league,
    rosters=rosters,
    players=players,
)

print()
print("LEAGUE STATE SUMMARY")
print("--------------------")
print(league_state.summary())