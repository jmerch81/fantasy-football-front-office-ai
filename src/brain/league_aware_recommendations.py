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


def get_league_aware_recommendation(executive, league_state=None):
    if league_state is not None and len(league_state.roster) == 0:
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

    return executive.make_recommendation()