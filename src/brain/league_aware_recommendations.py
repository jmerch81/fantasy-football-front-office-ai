from collections import Counter

from src.brain.recommendation import Recommendation


EMPTY_ROSTER_RECOMMENDATIONS = {
    "President of Football Operations": {
        "recommendation": "Complete the draft before full front office analysis begins.",
        "justification": "The organization cannot issue a true championship plan until a roster exists.",
        "evidence": [
            "Roster Size: 0",
            "No active starters available",
            "No bench depth available",
        ],
        "risks": [
            "Draft strategy has not been evaluated yet",
            "Waiver and trade recommendations are limited before roster construction",
        ],
        "confidence": 0.95,
    },
    "General Manager": {
        "recommendation": "Prioritize building a balanced roster through the draft.",
        "justification": "Roster construction cannot be evaluated until players are drafted.",
        "evidence": [
            "No players currently assigned to the roster",
            "No positional depth chart available",
            "No bench assets available",
        ],
        "risks": [
            "Weak draft balance could create season-long roster problems",
            "Lack of depth may limit trade flexibility",
        ],
        "confidence": 0.93,
    },
    "Head Coach": {
        "recommendation": "Lineup planning will activate once starters are available.",
        "justification": "Start/sit decisions require actual player matchups and roster assignments.",
        "evidence": [
            "No starting lineup available",
            "No matchup data can be applied yet",
            "No player roles have been assigned",
        ],
        "risks": [
            "Lineup optimization is unavailable before the draft",
            "Weekly matchup planning cannot begin yet",
        ],
        "confidence": 0.9,
    },
    "Director of Analytics": {
        "recommendation": "Prepare projections model, but delay roster scoring until the draft is complete.",
        "justification": "Analytics models need player-level roster data before producing useful recommendations.",
        "evidence": [
            "Roster Size: 0",
            "No player projections attached to team roster",
            "No positional value gaps detected yet",
        ],
        "risks": [
            "Any current projection would be theoretical",
            "Draft decisions may change the team's analytical profile",
        ],
        "confidence": 0.91,
    },
    "Director of Scouting": {
        "recommendation": "Focus scouting reports on draft targets and post-draft waiver candidates.",
        "justification": "Scouting becomes more actionable once team needs are known.",
        "evidence": [
            "No drafted players available for evaluation",
            "No roster weaknesses identified yet",
            "Draft pool remains the primary scouting focus",
        ],
        "risks": [
            "Scouting priorities may shift after the draft",
            "Undrafted roster needs are still unknown",
        ],
        "confidence": 0.89,
    },
    "Sports Medicine Director": {
        "recommendation": "Injury risk analysis will activate after players are drafted.",
        "justification": "Medical analysis requires a player roster to evaluate injury exposure.",
        "evidence": [
            "No rostered players available",
            "No injury exposure detected",
            "No questionable or injured starters identified",
        ],
        "risks": [
            "Drafting injured players could create early-season instability",
            "Medical risk cannot be scored without roster data",
        ],
        "confidence": 0.9,
    },
    "Football Intelligence Director": {
        "recommendation": "Monitor league activity and prepare intelligence reports for draft strategy.",
        "justification": "Opponent, waiver, and transaction intelligence becomes more valuable after rosters are formed.",
        "evidence": [
            "League connected successfully",
            "Roster not drafted yet",
            "No transactions available for team-specific analysis",
        ],
        "risks": [
            "Competitive intelligence is limited before the draft",
            "Opponent tendencies cannot be fully evaluated yet",
        ],
        "confidence": 0.88,
    },
}


def get_position_counts(league_state):
    positions = []

    for player in league_state.roster:
        position = player.get("position")

        if position:
            positions.append(position)

    return Counter(positions)


def get_injury_flags(league_state):
    injury_flags = []

    for player in league_state.roster:
        injury_status = player.get("injury_status")

        if injury_status and str(injury_status).lower() not in ["none", "nan"]:
            injury_flags.append(player)

    return injury_flags


def build_roster_evidence(position_counts, injury_flags):
    return [
        f"QB Count: {position_counts.get('QB', 0)}",
        f"RB Count: {position_counts.get('RB', 0)}",
        f"WR Count: {position_counts.get('WR', 0)}",
        f"TE Count: {position_counts.get('TE', 0)}",
        f"K Count: {position_counts.get('K', 0)}",
        f"DEF Count: {position_counts.get('DEF', 0)}",
        f"Injury Flags: {len(injury_flags)}",
    ]


def get_roster_strength(position_counts):
    if position_counts.get("WR", 0) >= 4:
        return "WR depth is the strongest part of the roster."
    if position_counts.get("RB", 0) >= 4:
        return "RB depth is the strongest part of the roster."
    if position_counts.get("QB", 0) >= 2:
        return "QB depth gives the roster weekly stability."

    return "Roster balance is still developing."


def get_roster_concern(position_counts, injury_flags):
    if len(injury_flags) > 0:
        return "Injury exposure should be monitored before finalizing the lineup."
    if position_counts.get("RB", 0) < 3:
        return "RB depth is thin and should be monitored on waivers."
    if position_counts.get("WR", 0) < 4:
        return "WR depth is light and could limit flex flexibility."
    if position_counts.get("TE", 0) < 2:
        return "TE depth is limited and may require a streaming plan."
    if position_counts.get("DEF", 0) == 0:
        return "No defense is currently available for the starting lineup."

    return "No major roster construction concern detected."


def get_active_roster_recommendation(executive, league_state):
    position_counts = get_position_counts(league_state)
    injury_flags = get_injury_flags(league_state)
    evidence = build_roster_evidence(position_counts, injury_flags)

    roster_strength = get_roster_strength(position_counts)
    roster_concern = get_roster_concern(position_counts, injury_flags)

    recommendations = {
        "President of Football Operations": Recommendation(
            executive=executive.title,
            recommendation="Proceed with roster optimization and weekly decision planning.",
            justification=(
                f"{roster_strength} {roster_concern} "
                "The front office has enough roster data to begin coordinated weekly analysis."
            ),
            evidence=evidence,
            confidence=0.91,
            risks=[
                roster_concern,
                "Recommendations should be updated once matchups, projections, and injuries are refreshed.",
            ],
            departments_consulted=[
                "General Manager",
                "Head Coach",
                "Analytics",
                "Scouting",
                "Sports Medicine",
                "Football Intelligence",
            ],
        ),
        "General Manager": Recommendation(
            executive=executive.title,
            recommendation="Maintain roster balance while monitoring waiver upgrades at weaker depth spots.",
            justification=(
                f"Current construction shows {position_counts.get('QB', 0)} QB, "
                f"{position_counts.get('RB', 0)} RB, {position_counts.get('WR', 0)} WR, "
                f"and {position_counts.get('TE', 0)} TE. {roster_concern}"
            ),
            evidence=evidence,
            confidence=0.9,
            risks=[
                "Bench depth may become a problem if injuries hit one position group.",
                "Roster balance should be reviewed weekly.",
            ],
            departments_consulted=[
                "Roster Intelligence",
                "Analytics",
                "Scouting",
            ],
        ),
        "Head Coach": Recommendation(
            executive=executive.title,
            recommendation="Use the current lineup structure as the baseline, then optimize flex spots weekly.",
            justification=(
                "The starting lineup can be built from the current roster. "
                "Flex decisions should be matchup-driven each week."
            ),
            evidence=evidence,
            confidence=0.88,
            risks=[
                "Flex spots may be misused without weekly matchup and projection data.",
                "Starting lineup should be reviewed after injury reports.",
            ],
            departments_consulted=[
                "Lineup Management",
                "Analytics",
                "Sports Medicine",
            ],
        ),
        "Director of Analytics": Recommendation(
            executive=executive.title,
            recommendation="Prioritize flex optimization and positional value scoring.",
            justification=(
                f"{roster_strength} The next analytical layer should compare weekly projected value "
                "between RB, WR, and TE flex candidates."
            ),
            evidence=evidence,
            confidence=0.89,
            risks=[
                "Current recommendation does not yet include projected points.",
                "Player value should be updated when projections are added.",
            ],
            departments_consulted=[
                "Roster Composition",
                "Projection Model",
                "Decision Engine",
            ],
        ),
        "Director of Scouting": Recommendation(
            executive=executive.title,
            recommendation="Build a waiver watchlist around the roster's weakest depth position.",
            justification=(
                f"{roster_concern} Scouting should focus on backup plans, breakout candidates, "
                "and injury replacement opportunities."
            ),
            evidence=evidence,
            confidence=0.87,
            risks=[
                "Waiver opportunities may change after league transactions.",
                "Scouting reports should be refreshed weekly.",
            ],
            departments_consulted=[
                "Waiver Intelligence",
                "Roster Depth",
                "Player Research",
            ],
        ),
        "Sports Medicine Director": Recommendation(
            executive=executive.title,
            recommendation="Monitor injury exposure before locking weekly starters.",
            justification=(
                f"The roster currently has {len(injury_flags)} injury flag(s). "
                "Medical risk should be checked before every lineup decision."
            ),
            evidence=evidence,
            confidence=0.86,
            risks=[
                "Late-week injury designations could change lineup recommendations.",
                "Questionable players need backup plans.",
            ],
            departments_consulted=[
                "Injury Intelligence",
                "Lineup Management",
                "Roster Risk",
            ],
        ),
        "Football Intelligence Director": Recommendation(
            executive=executive.title,
            recommendation="Track waiver activity, opponent needs, and depth chart movement.",
            justification=(
                "The roster is active, so league intelligence can now support waiver, trade, "
                "and lineup decisions."
            ),
            evidence=evidence,
            confidence=0.85,
            risks=[
                "Opponent and transaction data are not fully integrated yet.",
                "Market intelligence should improve once waiver data is added.",
            ],
            departments_consulted=[
                "League Activity",
                "Transaction Monitoring",
                "Opponent Intelligence",
            ],
        ),
    }

    return recommendations.get(
        executive.title,
        executive.make_recommendation(),
    )


def get_empty_roster_recommendation(executive):
    guidance = EMPTY_ROSTER_RECOMMENDATIONS.get(
        executive.title,
        {
            "recommendation": "Complete the draft before this department begins full analysis.",
            "justification": "This department needs roster data before making a complete recommendation.",
            "evidence": ["Roster Size: 0"],
            "risks": ["Recommendation is limited before the draft"],
            "confidence": 0.85,
        },
    )

    return Recommendation(
        executive=executive.title,
        recommendation=guidance["recommendation"],
        justification=guidance["justification"],
        evidence=guidance["evidence"],
        confidence=guidance["confidence"],
        risks=guidance["risks"],
        departments_consulted=[
            "League State",
            "Roster Intelligence",
            "Front Office AI",
        ],
    )


def get_league_aware_recommendation(executive, league_state=None):
    if league_state is None:
        return executive.make_recommendation()

    if len(league_state.roster) == 0:
        return get_empty_roster_recommendation(executive)

    return get_active_roster_recommendation(
        executive=executive,
        league_state=league_state,
    )