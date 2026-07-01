import pandas as pd
import streamlit as st
from pathlib import Path

from src.executives.front_office import FrontOffice
from src.meetings.executive_meeting import ExecutiveMeeting
from src.integrations.sleeper import SleeperClient
from src.league.sleeper_mapper import SleeperLeagueMapper
from src.brain.league_aware_recommendations import get_league_aware_recommendation


st.set_page_config(
    page_title="Fantasy Football Front Office AI",
    page_icon="🏈",
    layout="wide",
)

st.markdown(
    """
    <style>
    .main-title {
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 0px;
    }

    .subtitle {
        font-size: 18px;
        color: #A0AEC0;
        margin-top: 0px;
        margin-bottom: 28px;
    }

    .section-card {
        border: 1px solid #2D3748;
        border-radius: 18px;
        padding: 22px;
        background-color: #111827;
        margin-bottom: 22px;
    }

    .gold-card {
        border: 2px solid #D4AF37;
        border-radius: 18px;
        padding: 26px;
        background: linear-gradient(135deg, #111827 0%, #16213E 100%);
        margin-bottom: 30px;
    }

    .priority-text {
        font-size: 28px;
        font-weight: 800;
        color: #F7FAFC;
    }

    .muted-text {
        color: #A0AEC0;
        font-size: 14px;
    }

    .status-pill {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 999px;
        background-color: #065F46;
        color: #D1FAE5;
        font-size: 13px;
        font-weight: 700;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


PROJECT_ROOT = Path(__file__).resolve().parent
PLAYER_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "sleeper_players_clean.csv"

players_df = pd.read_csv(PLAYER_DATA_PATH)


def clean_display_value(value, fallback="N/A"):
    if pd.isna(value):
        return fallback

    if str(value).lower() == "nan":
        return fallback

    if value == "":
        return fallback

    return value


def find_demo_player(players_df, player_name, fallback_position, used_player_ids):
    name_matches = (
        players_df["full_name"]
        .fillna("")
        .astype(str)
        .str.lower()
        == player_name.lower()
    )

    exact_matches = players_df[name_matches].copy()

    if not exact_matches.empty:
        if "status" in exact_matches.columns:
            active_matches = exact_matches[exact_matches["status"] == "Active"]
            if not active_matches.empty:
                exact_matches = active_matches

        if "team" in exact_matches.columns:
            team_matches = exact_matches[exact_matches["team"].notna()]
            if not team_matches.empty:
                exact_matches = team_matches

        player = exact_matches.iloc[0].to_dict()
        player_id = player.get("player_id")

        if player_id and not pd.isna(player_id):
            used_player_ids.add(player_id)

        return player

    fallback_players = players_df[
        (players_df["status"] == "Active")
        & (players_df["position"] == fallback_position)
        & (players_df["team"].notna())
    ].copy()

    if "player_id" in fallback_players.columns:
        fallback_players = fallback_players[
            ~fallback_players["player_id"].isin(used_player_ids)
        ]

    if fallback_players.empty:
        return None

    player = fallback_players.iloc[0].to_dict()
    player_id = player.get("player_id")

    if player_id and not pd.isna(player_id):
        used_player_ids.add(player_id)

    return player


def build_demo_roster(players_df):
    demo_player_targets = [
        ("Josh Allen", "QB"),
        ("Christian McCaffrey", "RB"),
        ("Bijan Robinson", "RB"),
        ("CeeDee Lamb", "WR"),
        ("Justin Jefferson", "WR"),
        ("Ja'Marr Chase", "WR"),
        ("Travis Kelce", "TE"),
        ("Brandon Aubrey", "K"),
        ("Dallas Cowboys", "DEF"),
        ("Lamar Jackson", "QB"),
        ("Jahmyr Gibbs", "RB"),
        ("Amon-Ra St. Brown", "WR"),
        ("Puka Nacua", "WR"),
        ("Sam LaPorta", "TE"),
        ("Baltimore Ravens", "DEF"),
    ]

    used_player_ids = set()
    demo_roster = []

    for player_name, fallback_position in demo_player_targets:
        player = find_demo_player(
            players_df=players_df,
            player_name=player_name,
            fallback_position=fallback_position,
            used_player_ids=used_player_ids,
        )

        if player:
            demo_roster.append(player)

    has_defense = any(
        player.get("position") == "DEF"
        for player in demo_roster
    )

    if not has_defense:
        demo_roster.append({
            "player_id": "DAL_DEF_DEMO",
            "full_name": "Dallas Cowboys Defense",
            "position": "DEF",
            "team": "DAL",
            "status": "Active",
            "injury_status": None,
        })

        demo_roster.append({
            "player_id": "BAL_DEF_DEMO",
            "full_name": "Baltimore Ravens Defense",
            "position": "DEF",
            "team": "BAL",
            "status": "Active",
            "injury_status": None,
        })

    return demo_roster


LINEUP_SLOTS = [
    {"label": "QB", "eligible": ["QB"]},
    {"label": "RB", "eligible": ["RB"]},
    {"label": "RB", "eligible": ["RB"]},
    {"label": "WR", "eligible": ["WR"]},
    {"label": "WR", "eligible": ["WR"]},
    {"label": "TE", "eligible": ["TE"]},
    {"label": "W R T", "eligible": ["WR", "RB", "TE"]},
    {"label": "W R T", "eligible": ["WR", "RB", "TE"]},
    {"label": "K", "eligible": ["K"]},
    {"label": "DEF", "eligible": ["DEF"]},
]


def build_lineup_slots(roster):
    available_players = roster.copy()
    lineup = []

    for slot in LINEUP_SLOTS:
        selected_player = None

        for player in available_players:
            if player.get("position") in slot["eligible"]:
                selected_player = player
                break

        if selected_player:
            available_players.remove(selected_player)

        lineup.append({
            "slot": slot["label"],
            "player": selected_player,
        })

    bench = available_players

    return lineup, bench

def render_roster_row(slot_label, player=None, is_bench=False):
    if player is None:
        player_name = "Empty"
        player_details = ""
    else:
        player_name = clean_display_value(player.get("full_name"), "Unknown Player")
        team = clean_display_value(player.get("team"), "FA")
        status = clean_display_value(player.get("status"), "Unknown")
        injury = clean_display_value(player.get("injury_status"), "None")
        player_details = f"Team: {team} | Status: {status} | Injury: {injury}"

    slot_color = "#93C5FD" if is_bench else "#60A5FA"

    st.markdown(
        f"""
<div style="display: flex; align-items: center; border-radius: 14px; padding: 16px; margin-bottom: 12px; background-color: #111827; border: 1px solid #2D3748;">
<div style="width: 64px; text-align: center; border-radius: 10px; padding: 10px; margin-right: 16px; background-color: #1F2937; font-weight: 800; color: {slot_color};">{slot_label}</div>
<div>
<div style="font-size: 18px; font-weight: 800;">{player_name}</div>
<div style="font-size: 13px; color: #A0AEC0;">{player_details}</div>
</div>
</div>
""",
        unsafe_allow_html=True,
    )


st.markdown(
    """
    <div class="main-title">🏟️ Fantasy Football Front Office AI</div>
    <div class="subtitle">Data Wins Championships.</div>
    """,
    unsafe_allow_html=True,
)

st.subheader("Team Headquarters")
st.write("Welcome back, Mr. Merchant. Your AI front office is standing by.")

col1, col2, col3, col4 = st.columns(4)

total_players = len(players_df)
active_players = (
    len(players_df[players_df["status"] == "Active"])
    if "status" in players_df.columns
    else 0
)
teams = players_df["team"].nunique()
positions = players_df["position"].nunique()

col1.metric("NFL Players", f"{total_players:,}")
col2.metric("Active Players", f"{active_players:,}")
col3.metric("NFL Teams", teams)
col4.metric("Positions", positions)

st.divider()


# ---------------------------------------------------------
# Sidebar League Import
# ---------------------------------------------------------

st.sidebar.header("🏈 League Import")

sleeper_username = st.sidebar.text_input(
    "Sleeper Username",
    value="jmerch81",
)

selected_season = st.sidebar.number_input(
    "Season",
    min_value=2020,
    max_value=2030,
    value=2026,
    step=1,
)

client = SleeperClient()
use_demo_roster = False

try:
    user = client.get_user(sleeper_username)

    leagues = client.get_user_leagues(
        user["user_id"],
        int(selected_season),
    )

    if not leagues:
        st.error(
            f"No Sleeper leagues found for {sleeper_username} in {selected_season}."
        )
        st.stop()

    league_options = {
        league["name"]: league
        for league in leagues
    }

    selected_league_name = st.sidebar.selectbox(
        "Select League",
        list(league_options.keys()),
    )

    league = league_options[selected_league_name]

    rosters = client.get_rosters(
        league["league_id"]
    )

    player_database = client.get_players()

    mapper = SleeperLeagueMapper()

    league_state = mapper.build_league_state(
        user=user,
        league=league,
        rosters=rosters,
        players=player_database,
    )

    use_demo_roster = st.sidebar.checkbox(
        "Use Demo Roster",
        value=False,
    )

    if use_demo_roster and len(league_state.roster) == 0:
        demo_players = build_demo_roster(players_df)

        demo_lineup_slots, demo_bench_players = build_lineup_slots(demo_players)

        league_state.roster = demo_players
        league_state.starters = [
            lineup_slot["player"]
            for lineup_slot in demo_lineup_slots
            if lineup_slot["player"] is not None
        ]
        league_state.bench = demo_bench_players

        st.sidebar.info("Curated demo roster loaded")

    st.sidebar.success("League connected")

except Exception as error:
    st.error("Unable to connect to Sleeper league.")
    st.exception(error)
    st.stop()


# ---------------------------------------------------------
# Owner Dashboard
# ---------------------------------------------------------

st.header("👑 Owner Dashboard")

owner_col1, owner_col2, owner_col3, owner_col4 = st.columns(4)

if use_demo_roster:
    team_status = "Demo Mode"
elif len(league_state.roster) == 0:
    team_status = "Preseason"
else:
    team_status = "In Season"

owner_col1.metric("Owner", league_state.owner_name)
owner_col2.metric("League", league_state.league_name)
owner_col3.metric("Week", league_state.week)
owner_col4.metric("Status", team_status)

front_office = FrontOffice()
president = front_office.president

president_recommendation = get_league_aware_recommendation(
    president,
    league_state,
)

st.markdown(
    f"""
<div style="
    border: 1px solid #D4AF37;
    border-radius: 16px;
    padding: 22px;
    background-color: #111827;
    margin-top: 18px;
    margin-bottom: 25px;
">
<h3>🏆 Today's Priority</h3>
<div class="priority-text">{president_recommendation.recommendation}</div>
<p><strong>Executive Consensus:</strong> {president_recommendation.confidence:.0%}</p>
<p><strong>Owner Action Required:</strong> Review recommendation and prepare roster strategy.</p>
</div>
""",
    unsafe_allow_html=True,
)

priority_col1, priority_col2, priority_col3, priority_col4 = st.columns(4)

priority_col1.metric("Roster Size", len(league_state.roster))
priority_col2.metric("Starters", len(league_state.starters))
priority_col3.metric("Bench", len(league_state.bench))
priority_col4.metric(
    league_state.waiver_metric_label(),
    league_state.waiver_metric_value(),
)

st.divider()


# ---------------------------------------------------------
# Live Roster
# ---------------------------------------------------------

st.header("🏈 Live Roster")

if len(league_state.roster) == 0:
    st.warning(
        "Roster not drafted yet. Complete a draft or connect a league with active rosters to activate roster analysis."
    )
else:
    if use_demo_roster:
        st.info("Demo roster mode is active. These players are sample roster data for product testing.")

    lineup_slots, bench_players = build_lineup_slots(league_state.roster)

    st.subheader("STARTERS")
    st.caption("Lineup slots are automatically filled based on roster eligibility.")

    for lineup_slot in lineup_slots:
        render_roster_row(
            slot_label=lineup_slot["slot"],
            player=lineup_slot["player"],
            is_bench=False,
        )

    st.subheader("BENCH")

    if not bench_players:
        for _ in range(5):
            render_roster_row(
                slot_label="BN",
                player=None,
                is_bench=True,
            )
    else:
        for player in bench_players:
            render_roster_row(
                slot_label="BN",
                player=player,
                is_bench=True,
            )

st.divider()

# ---------------------------------------------------------
# Executive Staff Status
# ---------------------------------------------------------

st.header("🏢 Executive Staff Status")

president = front_office.president

president_recommendation = get_league_aware_recommendation(
    president,
    league_state,
)

st.markdown(
    f"""
<div style="
    border:2px solid #D4AF37;
    border-radius:18px;
    padding:24px;
    background:#16213E;
    margin-bottom:30px;
">
<h2>👑 {president.title}</h2>
<h4>{president.name}</h4>
<p><em>{president.signature_phrase}</em></p>
<hr>
<h3>🏆 Final Recommendation</h3>
<p>{president_recommendation.recommendation}</p>
<p><strong>Executive Consensus:</strong> {president_recommendation.confidence:.0%}</p>
<p><strong>Status:</strong> <span class="status-pill">Decision Finalized</span></p>
<p><strong>Departments Reviewed:</strong> General Manager, Head Coach, Analytics, Scouting, Medical, Football Intelligence</p>
</div>
""",
    unsafe_allow_html=True,
)

st.subheader("Executive Leadership Team")

executive_cards = []

for executive in front_office.executives:
    recommendation = get_league_aware_recommendation(
        executive,
        league_state,
    )

    executive_cards.append({
        "title": executive.title,
        "name": executive.name,
        "recommendation": recommendation.recommendation,
        "confidence": recommendation.confidence,
        "signature": executive.signature_phrase,
    })

cols = st.columns(3)

for index, card in enumerate(executive_cards):
    with cols[index % 3]:
        st.markdown(
            f"""
<div style="
    border: 1px solid #333;
    border-radius: 14px;
    padding: 18px;
    margin-bottom: 18px;
    background-color: #111827;
    min-height: 260px;
">
<h4>{card["title"]}</h4>
<p><strong>{card["name"]}</strong></p>
<p><em>{card["signature"]}</em></p>
<p><strong>Status:</strong> <span class="status-pill">Ready</span></p>
<p><strong>Recommendation:</strong><br>{card["recommendation"]}</p>
<p><strong>Confidence:</strong> {card["confidence"]:.0%}</p>
</div>
""",
            unsafe_allow_html=True,
        )

st.divider()


# ---------------------------------------------------------
# Player Explorer
# ---------------------------------------------------------

st.header("📋 Player Explorer")

position_filter = st.selectbox(
    "Filter by Position",
    ["All"] + sorted(players_df["position"].dropna().unique().tolist()),
)

team_filter = st.selectbox(
    "Filter by Team",
    ["All"] + sorted(players_df["team"].dropna().unique().tolist()),
)

search = st.text_input("Search Player")

filtered_players = players_df.copy()

if position_filter != "All":
    filtered_players = filtered_players[
        filtered_players["position"] == position_filter
    ]

if team_filter != "All":
    filtered_players = filtered_players[
        filtered_players["team"] == team_filter
    ]

if search:
    filtered_players = filtered_players[
        filtered_players["full_name"].str.contains(search, case=False, na=False)
    ]

st.dataframe(filtered_players, use_container_width=True)

st.write(f"Showing {len(filtered_players):,} players")

st.divider()


# ---------------------------------------------------------
# Tuesday Executive Meeting
# ---------------------------------------------------------

st.header("🏛 Tuesday Executive Meeting")

meeting = ExecutiveMeeting(
    meeting_name="Tuesday Executive Meeting",
    president=front_office.president,
    attendees=front_office.executives,
)

st.success(meeting.call_to_order())

reports = [
    get_league_aware_recommendation(
        executive,
        league_state,
    )
    for executive in front_office.executives
]

for report in reports:
    with st.container():
        st.subheader(report.executive)
        st.write(f"**Recommendation:** {report.recommendation}")
        st.progress(report.confidence)
        st.caption(report.justification)
        st.divider()

st.header("👔 President's Summary")

top_report = max(reports, key=lambda report: report.confidence)

st.info(
    f"President's Summary: {top_report.recommendation} "
    f"Current organizational priority is based on live league state."
)