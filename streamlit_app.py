import pandas as pd
import streamlit as st
from pathlib import Path
from collections import Counter

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

def analyze_lineup_decision(roster):
    lineup_slots, bench_players = build_lineup_slots(roster)

    open_slots = [
        lineup_slot
        for lineup_slot in lineup_slots
        if lineup_slot["player"] is None
    ]

    filled_slots = [
        lineup_slot
        for lineup_slot in lineup_slots
        if lineup_slot["player"] is not None
    ]

    flex_slots = [
        lineup_slot
        for lineup_slot in lineup_slots
        if lineup_slot["slot"] == "W R T"
    ]

    filled_flex_slots = [
        lineup_slot
        for lineup_slot in flex_slots
        if lineup_slot["player"] is not None
    ]

    starter_injury_flags = []

    for lineup_slot in filled_slots:
        player = lineup_slot["player"]
        injury_status = player.get("injury_status")

        if injury_status and str(injury_status).lower() not in ["none", "nan"]:
            starter_injury_flags.append(player)

    lineup_ready = (
        len(open_slots) == 0
        and len(starter_injury_flags) == 0
    )

    if lineup_ready:
        coach_recommendation = (
            "Lineup is ready. Maintain current structure and monitor late-week injury updates."
        )
    elif len(open_slots) > 0:
        coach_recommendation = (
            "Lineup is not complete. Fill all open starter slots before finalizing weekly strategy."
        )
    else:
        coach_recommendation = (
            "Lineup is mostly ready, but injury risk must be reviewed before lock."
        )

    return {
        "lineup_slots": lineup_slots,
        "bench_players": bench_players,
        "open_slots": open_slots,
        "filled_slots": filled_slots,
        "flex_slots": flex_slots,
        "filled_flex_slots": filled_flex_slots,
        "starter_injury_flags": starter_injury_flags,
        "lineup_ready": lineup_ready,
        "coach_recommendation": coach_recommendation,
    }

def analyze_injury_risk(roster):
    injury_flags = []

    for player in roster:
        injury_status = player.get("injury_status")

        if injury_status and str(injury_status).lower() not in ["none", "nan"]:
            injury_flags.append(player)

    questionable_players = [
        player for player in injury_flags
        if str(player.get("injury_status")).lower() == "questionable"
    ]

    out_players = [
        player for player in injury_flags
        if str(player.get("injury_status")).lower() in ["out", "ir", "doubtful"]
    ]

    if len(injury_flags) == 0:
        risk_level = "Low"
        medical_recommendation = (
            "No major injury risk detected. Continue monitoring injury reports before lineup lock."
        )
    elif len(out_players) > 0:
        risk_level = "High"
        medical_recommendation = (
            "High injury risk detected. Replace unavailable players and prepare backup options immediately."
        )
    else:
        risk_level = "Moderate"
        medical_recommendation = (
            "Monitor questionable players closely and identify backup options before kickoff."
        )

    return {
        "injury_flags": injury_flags,
        "questionable_players": questionable_players,
        "out_players": out_players,
        "risk_level": risk_level,
        "medical_recommendation": medical_recommendation,
    }

def collect_executive_reports(front_office, league_state):
    reports = [
        get_league_aware_recommendation(
            executive,
            league_state,
        )
        for executive in front_office.executives
    ]

    president_report = get_league_aware_recommendation(
        front_office.president,
        league_state,
    )

    return [president_report] + reports


def build_front_office_verdict(reports):
    top_report = max(
        reports,
        key=lambda report: report.confidence,
    )

    average_confidence = sum(
        report.confidence for report in reports
    ) / len(reports)

    aligned_departments = [
        report.executive
        for report in reports
        if report.confidence >= 0.85
    ]

    risks = []

    for report in reports:
        risks.extend(report.risks)

    unique_risks = list(dict.fromkeys(risks))

    return {
        "top_report": top_report,
        "average_confidence": average_confidence,
        "aligned_departments": aligned_departments,
        "risks": unique_risks,
    }

def build_beta_readiness_status(
    league_state,
    use_demo_roster,
    lineup_decision,
    injury_report,
    executive_reports,
):
    checks = [
        {
            "item": "League Connected",
            "ready": bool(league_state.league_id),
            "details": league_state.league_name or "No league connected",
        },
        {
            "item": "Roster Loaded",
            "ready": len(league_state.roster) > 0,
            "details": f"{len(league_state.roster)} players loaded",
        },
        {
            "item": "Lineup Intelligence",
            "ready": lineup_decision is not None,
            "details": "Lineup analysis active" if lineup_decision else "Lineup analysis inactive",
        },
        {
            "item": "Injury Intelligence",
            "ready": injury_report is not None,
            "details": "Injury analysis active" if injury_report else "Injury analysis inactive",
        },
        {
            "item": "Executive Reports",
            "ready": len(executive_reports) > 0,
            "details": f"{len(executive_reports)} reports generated",
        },
        {
            "item": "Demo Mode",
            "ready": use_demo_roster,
            "details": "Demo mode active" if use_demo_roster else "Using live league data",
        },
    ]

    ready_count = sum(1 for check in checks if check["ready"])
    total_count = len(checks)

    beta_ready = ready_count >= 5

    return {
        "checks": checks,
        "ready_count": ready_count,
        "total_count": total_count,
        "beta_ready": beta_ready,
    }

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

def get_position_counts(roster):
    positions = [
        clean_display_value(player.get("position"), "Unknown")
        for player in roster
        if player
    ]

    return Counter(positions)


def analyze_roster_composition(roster):
    counts = get_position_counts(roster)

    insights = []

    if counts.get("QB", 0) >= 2:
        insights.append({
            "type": "Strength",
            "department": "General Manager",
            "message": "QB depth is stable with multiple starting-caliber options."
        })
    else:
        insights.append({
            "type": "Concern",
            "department": "General Manager",
            "message": "QB depth is thin. Add a backup or high-upside QB watchlist target."
        })

    if counts.get("RB", 0) >= 3:
        insights.append({
            "type": "Strength",
            "department": "Director of Analytics",
            "message": "RB room has enough depth to support weekly flexibility."
        })
    else:
        insights.append({
            "type": "Concern",
            "department": "Director of Analytics",
            "message": "RB depth may need attention. Monitor waiver backs and injury replacements."
        })

    if counts.get("WR", 0) >= 4:
        insights.append({
            "type": "Strength",
            "department": "Director of Scouting",
            "message": "WR depth is strong and gives the roster weekly matchup flexibility."
        })
    else:
        insights.append({
            "type": "Concern",
            "department": "Director of Scouting",
            "message": "WR depth is light. Scout upside receivers before the season starts."
        })

    if counts.get("TE", 0) >= 2:
        insights.append({
            "type": "Strength",
            "department": "Head Coach",
            "message": "TE depth gives the coaching staff lineup flexibility."
        })
    else:
        insights.append({
            "type": "Concern",
            "department": "Head Coach",
            "message": "TE depth is limited. Prepare a streaming plan."
        })

    if counts.get("K", 0) == 0:
        insights.append({
            "type": "Concern",
            "department": "Football Intelligence",
            "message": "No kicker found on the roster."
        })

    if counts.get("DEF", 0) == 0:
        insights.append({
            "type": "Concern",
            "department": "Football Intelligence",
            "message": "No defense found on the roster."
        })

    return counts, insights

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
# Owner Command Center
# ---------------------------------------------------------

st.header("📡 Owner Command Center")

if len(league_state.roster) == 0:
    st.warning(
        "Command Center will activate once a roster is drafted or demo mode is enabled."
    )
else:
    command_lineup = analyze_lineup_decision(league_state.roster)
    command_injury = analyze_injury_risk(league_state.roster)
    command_reports = collect_executive_reports(front_office, league_state)
    command_verdict = build_front_office_verdict(command_reports)

    command_col1, command_col2, command_col3, command_col4 = st.columns(4)

    command_col1.metric(
        "Roster Status",
        "Active" if len(league_state.roster) > 0 else "Not Drafted",
    )

    command_col2.metric(
        "Lineup",
        "Ready" if command_lineup["lineup_ready"] else "Needs Review",
    )

    command_col3.metric(
        "Injury Risk",
        command_injury["risk_level"],
    )

    command_col4.metric(
        "Exec Confidence",
        f"{command_verdict['average_confidence']:.0%}",
    )

    st.markdown(
        f"""
<div style="
    border: 2px solid #D4AF37;
    border-radius: 18px;
    padding: 22px;
    margin-top: 18px;
    margin-bottom: 22px;
    background: linear-gradient(135deg, #111827 0%, #16213E 100%);
">
<h3>Owner Priority Brief</h3>
<h2>{command_verdict["top_report"].recommendation}</h2>
<p><strong>Lead Department:</strong> {command_verdict["top_report"].executive}</p>
<p><strong>Confidence:</strong> {command_verdict["top_report"].confidence:.0%}</p>
<p><strong>Immediate Action:</strong> Review lineup readiness, monitor injury updates, and prepare weekly decision strategy.</p>
</div>
""",
        unsafe_allow_html=True,
    )

st.divider()

# ---------------------------------------------------------
# Beta Launch Readiness
# ---------------------------------------------------------

st.header("🚀 Beta Launch Readiness")

if len(league_state.roster) == 0:
    beta_lineup_decision = None
    beta_injury_report = None
    beta_executive_reports = []
else:
    beta_lineup_decision = analyze_lineup_decision(league_state.roster)
    beta_injury_report = analyze_injury_risk(league_state.roster)
    beta_executive_reports = collect_executive_reports(
        front_office,
        league_state,
    )

beta_status = build_beta_readiness_status(
    league_state=league_state,
    use_demo_roster=use_demo_roster,
    lineup_decision=beta_lineup_decision,
    injury_report=beta_injury_report,
    executive_reports=beta_executive_reports,
)

readiness_col1, readiness_col2, readiness_col3 = st.columns(3)

readiness_col1.metric(
    "Ready Checks",
    f"{beta_status['ready_count']}/{beta_status['total_count']}",
)

readiness_col2.metric(
    "Beta Status",
    "Ready for Review" if beta_status["beta_ready"] else "Needs Work",
)

readiness_col3.metric(
    "Mode",
    "Demo" if use_demo_roster else "Live",
)

st.subheader("Launch Checklist")

for check in beta_status["checks"]:
    if check["ready"]:
        st.success(f"✅ {check['item']}: {check['details']}")
    else:
        st.warning(f"⚠️ {check['item']}: {check['details']}")

if beta_status["beta_ready"]:
    st.markdown(
        """
<div style="
    border: 2px solid #22C55E;
    border-radius: 18px;
    padding: 22px;
    margin-top: 18px;
    margin-bottom: 22px;
    background-color: #052E16;
">
<h3>Beta Review Status</h3>
<p>This build is ready for beta review. Core league import, roster intelligence, lineup intelligence, injury intelligence, and executive recommendations are active.</p>
</div>
""",
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        """
<div style="
    border: 2px solid #F59E0B;
    border-radius: 18px;
    padding: 22px;
    margin-top: 18px;
    margin-bottom: 22px;
    background-color: #422006;
">
<h3>Beta Review Status</h3>
<p>This build still needs work before beta review. Complete the missing readiness checks above.</p>
</div>
""",
        unsafe_allow_html=True,
    )

st.divider()

# ---------------------------------------------------------
# Roster Composition Intelligence
# ---------------------------------------------------------

st.header("🧠 Roster Composition Intelligence")

if len(league_state.roster) == 0:
    st.warning(
        "Roster intelligence will activate once a roster is drafted or demo mode is enabled."
    )
else:
    position_counts, roster_insights = analyze_roster_composition(
        league_state.roster
    )

    count_col1, count_col2, count_col3, count_col4, count_col5, count_col6 = st.columns(6)

    count_col1.metric("QB", position_counts.get("QB", 0))
    count_col2.metric("RB", position_counts.get("RB", 0))
    count_col3.metric("WR", position_counts.get("WR", 0))
    count_col4.metric("TE", position_counts.get("TE", 0))
    count_col5.metric("K", position_counts.get("K", 0))
    count_col6.metric("DEF", position_counts.get("DEF", 0))

    st.subheader("Front Office Readout")

    insight_cols = st.columns(2)

    for index, insight in enumerate(roster_insights):
        with insight_cols[index % 2]:
            st.markdown(
                f"""
<div style="
    border: 1px solid #2D3748;
    border-radius: 14px;
    padding: 16px;
    margin-bottom: 14px;
    background-color: #111827;
">
<h4>{insight["type"]}: {insight["department"]}</h4>
<p>{insight["message"]}</p>
</div>
""",
                unsafe_allow_html=True,
            )

st.divider()

# ---------------------------------------------------------
# Lineup Decision Intelligence
# ---------------------------------------------------------

st.header("🎯 Lineup Decision Intelligence")

if len(league_state.roster) == 0:
    st.warning(
        "Lineup intelligence will activate once a roster is drafted or demo mode is enabled."
    )
else:
    lineup_decision = analyze_lineup_decision(league_state.roster)

    status_col1, status_col2, status_col3, status_col4 = st.columns(4)

    status_col1.metric(
        "Lineup Status",
        "Ready" if lineup_decision["lineup_ready"] else "Needs Review",
    )

    status_col2.metric(
        "Open Slots",
        len(lineup_decision["open_slots"]),
    )

    status_col3.metric(
        "Injury Flags",
        len(lineup_decision["starter_injury_flags"]),
    )

    status_col4.metric(
        "Bench Options",
        len(lineup_decision["bench_players"]),
    )

    st.subheader("Head Coach Recommendation")

    st.markdown(
        f"""
<div style="
    border: 1px solid #2D3748;
    border-radius: 14px;
    padding: 18px;
    margin-bottom: 16px;
    background-color: #111827;
">
<h4>Marcus Reed — Head Coach</h4>
<p>{lineup_decision["coach_recommendation"]}</p>
</div>
""",
        unsafe_allow_html=True,
    )

    if lineup_decision["open_slots"]:
        st.subheader("Open Starter Slots")

        for open_slot in lineup_decision["open_slots"]:
            st.warning(
                f"{open_slot['slot']} slot is currently empty."
            )

    if lineup_decision["starter_injury_flags"]:
        st.subheader("Starter Injury Watch")

        for player in lineup_decision["starter_injury_flags"]:
            player_name = clean_display_value(
                player.get("full_name"),
                "Unknown Player",
            )
            injury_status = clean_display_value(
                player.get("injury_status"),
                "Unknown",
            )

            st.error(
                f"{player_name} is currently listed as {injury_status}."
            )

    st.subheader("Flex Slot Review")

    filled_flex_count = len(lineup_decision["filled_flex_slots"])
    total_flex_count = len(lineup_decision["flex_slots"])

    if filled_flex_count == total_flex_count:
        st.success(
            f"All FLEX slots are filled: {filled_flex_count}/{total_flex_count}."
        )
    else:
        st.warning(
            f"FLEX slots need attention: {filled_flex_count}/{total_flex_count} filled."
        )

st.divider()

# ---------------------------------------------------------
# Injury Risk Intelligence
# ---------------------------------------------------------

st.header("🩺 Injury Risk Intelligence")

if len(league_state.roster) == 0:
    st.warning(
        "Injury intelligence will activate once a roster is drafted or demo mode is enabled."
    )
else:
    injury_report = analyze_injury_risk(league_state.roster)

    injury_col1, injury_col2, injury_col3, injury_col4 = st.columns(4)

    injury_col1.metric("Risk Level", injury_report["risk_level"])
    injury_col2.metric("Injury Flags", len(injury_report["injury_flags"]))
    injury_col3.metric("Questionable", len(injury_report["questionable_players"]))
    injury_col4.metric("Out / IR / Doubtful", len(injury_report["out_players"]))

    st.subheader("Sports Medicine Recommendation")

    st.markdown(
        f"""
<div style="
    border: 1px solid #2D3748;
    border-radius: 14px;
    padding: 18px;
    margin-bottom: 16px;
    background-color: #111827;
">
<h4>Sports Medicine Director</h4>
<p>{injury_report["medical_recommendation"]}</p>
</div>
""",
        unsafe_allow_html=True,
    )

    if injury_report["injury_flags"]:
        st.subheader("Players to Monitor")

        for player in injury_report["injury_flags"]:
            player_name = clean_display_value(
                player.get("full_name"),
                "Unknown Player",
            )
            position = clean_display_value(
                player.get("position"),
                "N/A",
            )
            team = clean_display_value(
                player.get("team"),
                "FA",
            )
            injury_status = clean_display_value(
                player.get("injury_status"),
                "Unknown",
            )

            st.warning(
                f"{player_name} | {position} | {team} | Injury Status: {injury_status}"
            )
    else:
        st.success("No injury flags detected across the current roster.")

st.divider()

# ---------------------------------------------------------
# Executive Consensus Summary
# ---------------------------------------------------------

st.header("🏛️ Executive Consensus Summary")

if len(league_state.roster) == 0:
    st.warning(
        "Executive consensus will activate once a roster is drafted or demo mode is enabled."
    )
else:
    consensus_reports = collect_executive_reports(
        front_office,
        league_state,
    )

    front_office_verdict = build_front_office_verdict(
        consensus_reports
    )

    top_report = front_office_verdict["top_report"]

    consensus_col1, consensus_col2, consensus_col3 = st.columns(3)

    consensus_col1.metric(
        "Final Confidence",
        f"{front_office_verdict['average_confidence']:.0%}",
    )

    consensus_col2.metric(
        "Departments Aligned",
        len(front_office_verdict["aligned_departments"]),
    )

    consensus_col3.metric(
        "Risks Identified",
        len(front_office_verdict["risks"]),
    )

    st.markdown(
        f"""
<div style="
    border: 2px solid #D4AF37;
    border-radius: 18px;
    padding: 24px;
    margin-top: 18px;
    margin-bottom: 18px;
    background: linear-gradient(135deg, #111827 0%, #16213E 100%);
">
<h3>Final Front Office Verdict</h3>
<h2>{top_report.recommendation}</h2>
<p><strong>Lead Department:</strong> {top_report.executive}</p>
<p><strong>Confidence:</strong> {top_report.confidence:.0%}</p>
<p><strong>Why:</strong> {top_report.justification}</p>
</div>
""",
        unsafe_allow_html=True,
    )

    st.subheader("Owner Action Plan")

    st.success(
        "Review the lineup, monitor injury updates, and use the current roster structure as the baseline for weekly decisions."
    )

    if front_office_verdict["risks"]:
        st.subheader("Key Risks to Monitor")

        for risk in front_office_verdict["risks"][:5]:
            st.warning(risk)

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

executive_reports = []

for executive in front_office.executives:
    recommendation = get_league_aware_recommendation(
        executive,
        league_state,
    )

    executive_reports.append({
        "title": executive.title,
        "name": executive.name,
        "signature": executive.signature_phrase,
        "recommendation": recommendation.recommendation,
        "justification": recommendation.justification,
        "confidence": recommendation.confidence,
        "evidence": recommendation.evidence,
        "risks": recommendation.risks,
        "departments": recommendation.departments_consulted,
    })

cols = st.columns(2)

for index, report in enumerate(executive_reports):
    evidence_html = "".join(
        f"<li>{item}</li>"
        for item in report["evidence"][:3]
    )

    risks_html = "".join(
        f"<li>{risk}</li>"
        for risk in report["risks"][:2]
    )

    departments = ", ".join(report["departments"][:3])

    with cols[index % 2]:
        st.markdown(
            f"""
<div style="
    border: 1px solid #2D3748;
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 20px;
    background-color: #111827;
    min-height: 430px;
">
<h3>{report["title"]}</h3>
<p><strong>{report["name"]}</strong></p>
<p><em>{report["signature"]}</em></p>

<hr>

<p><strong>Recommendation:</strong><br>{report["recommendation"]}</p>
<p><strong>Why:</strong><br>{report["justification"]}</p>
<p><strong>Confidence:</strong> {report["confidence"]:.0%}</p>

<p><strong>Evidence:</strong></p>
<ul>{evidence_html}</ul>

<p><strong>Risks:</strong></p>
<ul>{risks_html}</ul>

<p><strong>Departments Consulted:</strong><br>{departments}</p>
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