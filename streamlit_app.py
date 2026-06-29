import pandas as pd
import streamlit as st
from pathlib import Path
from src.executives.front_office import FrontOffice
from src.meetings.executive_meeting import ExecutiveMeeting

st.set_page_config(
    page_title="Fantasy Football Front Office AI",
    page_icon="🏈",
    layout="wide"
)

PROJECT_ROOT = Path(__file__).resolve().parent
PLAYER_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "sleeper_players_clean.csv"

players = pd.read_csv(PLAYER_DATA_PATH)

st.title("🏟️ Fantasy Football Front Office AI")
st.subheader("Team Headquarters")

st.markdown("""
Welcome back, Mr. Merchant.

Your AI front office is standing by.
""")

col1, col2, col3, col4 = st.columns(4)

total_players = len(players)
active_players = len(players[players["status"] == "Active"]) if "status" in players.columns else 0
teams = players["team"].nunique()
positions = players["position"].nunique()

col1.metric("NFL Players", f"{total_players:,}")
col2.metric("Active Players", f"{active_players:,}")
col3.metric("NFL Teams", teams)
col4.metric("Positions", positions)

st.divider()

st.header("🏢 Executive Staff Status")

staff = pd.DataFrame({
    "Department": [
        "President of Football Operations",
        "General Manager",
        "Head Coach",
        "Director of Analytics",
        "Director of Scouting",
        "Sports Medicine",
        "Football Intelligence",
        "Trade Committee"
    ],
    "Status": [
        "Ready",
        "Ready",
        "Ready",
        "Ready",
        "Ready",
        "Monitoring",
        "Monitoring",
        "Standing By"
    ],
    "Primary Focus": [
        "Final recommendations",
        "Roster strategy",
        "Weekly lineup",
        "Projections and rankings",
        "Sleepers and breakouts",
        "Injury risk",
        "Weather and schedule context",
        "Trade evaluation"
    ]
})

st.dataframe(staff, use_container_width=True)

st.divider()

st.header("📋 Player Explorer")

position_filter = st.selectbox(
    "Filter by Position",
    ["All"] + sorted(players["position"].dropna().unique().tolist())
)

team_filter = st.selectbox(
    "Filter by Team",
    ["All"] + sorted(players["team"].dropna().unique().tolist())
)

search = st.text_input("Search Player")

filtered_players = players.copy()

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