import pandas as pd
import streamlit as st
from pathlib import Path
from src.executives.front_office import FrontOffice
from src.meetings.executive_meeting import ExecutiveMeeting
from src.integrations.sleeper import SleeperClient
from src.league.sleeper_mapper import SleeperLeagueMapper

st.set_page_config(
    page_title="Fantasy Football Front Office AI",
    page_icon="🏈",
    layout="wide"
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
active_players = len(players_df[players_df["status"] == "Active"]) if "status" in players_df.columns else 0
teams = players_df["team"].nunique()
positions = players_df["position"].nunique()

col1.metric("NFL Players", f"{total_players:,}")
col2.metric("Active Players", f"{active_players:,}")
col3.metric("NFL Teams", teams)
col4.metric("Positions", positions)

st.divider()

client = SleeperClient()

user = client.get_user("jmerch81")

league = client.get_user_leagues(
    user["user_id"],
    2026
)[0]

rosters = client.get_rosters(
    league["league_id"]
)

players = client.get_players()

mapper = SleeperLeagueMapper()

league_state = mapper.build_league_state(
    user=user,
    league=league,
    rosters=rosters,
    players=players,
)

st.header("👑 Owner Dashboard")

owner_col1, owner_col2, owner_col3, owner_col4 = st.columns(4)

owner_col1.metric("Owner", league_state.owner_name)
owner_col2.metric("League", league_state.league_name)
owner_col3.metric("Week", league_state.week)
owner_col4.metric("Status", "Preseason" if league_state.roster == [] else "In Season")

front_office = FrontOffice()
president = front_office.president
president_recommendation = president.make_recommendation()

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
<p><strong>Owner Action Required:</strong> Review recommendation and prepare waiver strategy.</p>
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
    league_state.waiver_metric_value()
)

st.divider()

st.divider()

st.header("🏈 Live Roster")

if len(league_state.roster) == 0:
    st.warning(
        "Roster not drafted yet. Complete a draft or connect a league with active rosters to activate roster analysis."
    )
else:
    positions = ["QB", "RB", "WR", "TE", "K", "DEF"]

    for position in positions:
        position_players = [
            player for player in league_state.roster
            if player.get("position") == position
        ]

        if position_players:
            st.subheader(position)

            cols = st.columns(3)

            for index, player in enumerate(position_players):
                with cols[index % 3]:
                    st.markdown(
                        f"""
<div style="
    border: 1px solid #333;
    border-radius: 14px;
    padding: 16px;
    margin-bottom: 16px;
    background-color: #111827;
">
<h4>{player.get("full_name", "Unknown Player")}</h4>
<p><strong>Team:</strong> {player.get("team", "FA")}</p>
<p><strong>Position:</strong> {player.get("position", "N/A")}</p>
<p><strong>Status:</strong> {player.get("status", "Unknown")}</p>
<p><strong>Injury:</strong> {player.get("injury_status") or "None"}</p>
</div>
""",
                        unsafe_allow_html=True,
                    )

    bench_players = league_state.bench

    if bench_players:
        st.subheader("Bench")

        cols = st.columns(3)

        for index, player in enumerate(bench_players):
            with cols[index % 3]:
                st.markdown(
                    f"""
<div style="
    border: 1px solid #333;
    border-radius: 14px;
    padding: 16px;
    margin-bottom: 16px;
    background-color: #111827;
">
<h4>{player.get("full_name", "Unknown Player")}</h4>
<p><strong>Team:</strong> {player.get("team", "FA")}</p>
<p><strong>Position:</strong> {player.get("position", "N/A")}</p>
<p><strong>Status:</strong> {player.get("status", "Unknown")}</p>
<p><strong>Injury:</strong> {player.get("injury_status") or "None"}</p>
</div>
""",
                    unsafe_allow_html=True,
                )

st.header("🏢 Executive Staff Status")

front_office = FrontOffice()

president = front_office.president
president_recommendation = president.make_recommendation()

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
    recommendation = executive.make_recommendation()

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
            unsafe_allow_html=True
        )

st.divider()

st.header("📋 Player Explorer")

position_filter = st.selectbox(
    "Filter by Position",
    ["All"] + sorted(players_df["position"].dropna().unique().tolist())
)

team_filter = st.selectbox(
    "Filter by Team",
    ["All"] + sorted(players_df["team"].dropna().unique().tolist())
)

search = st.text_input("Search Player")

filtered_players = players_df.copy()

if position_filter != "All":
    filtered_players = filtered_players[filtered_players["position"] == position_filter]

if team_filter != "All":
    filtered_players = filtered_players[filtered_players["team"] == team_filter]

if search:
    filtered_players = filtered_players[
        filtered_players["full_name"].str.contains(search, case=False, na=False)
    ]

st.dataframe(filtered_players, use_container_width=True)

st.write(f"Showing {len(filtered_players):,} players")

st.header("🏛 Tuesday Executive Meeting")

front_office = FrontOffice()

meeting = ExecutiveMeeting(
    meeting_name="Tuesday Executive Meeting",
    president=front_office.president,
    attendees=front_office.executives,
)

st.success(meeting.call_to_order())

reports = meeting.collect_reports()

for report in reports:

    with st.container():

        st.subheader(report.executive)

        st.write(f"**Recommendation:** {report.recommendation}")

        st.progress(report.confidence)

        st.caption(report.justification)

        st.divider()

st.header("👔 President's Summary")

st.info(meeting.summarize_meeting())