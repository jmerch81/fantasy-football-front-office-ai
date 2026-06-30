from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class LeagueState:
    """
    Central source of truth for the current fantasy league.

    Every executive reads from this object.
    Only the integrations (Sleeper, ESPN, Yahoo) write to it.
    """

    # League Information
    league_id: str = ""
    league_name: str = ""
    season: int = 2026
    week: int = 1

    # Owner Information
    owner_name: str = ""
    owner_team_name: str = ""

    # Team Information
    roster: List[Dict] = field(default_factory=list)
    starters: List[Dict] = field(default_factory=list)
    bench: List[str] = field(default_factory=list)

    # Opponent
    opponent_name: str = ""
    opponent_roster: List[Dict] = field(default_factory=list)

    # League Information
    standings: List[Dict] = field(default_factory=list)
    waiver_order: Optional[int] = None
    faab_remaining: Optional[int] = None

    # Intelligence
    injuries: List[Dict] = field(default_factory=list)
    weather_alerts: List[Dict] = field(default_factory=list)
    news: List[Dict] = field(default_factory=list)
    transactions: List[Dict] = field(default_factory=list)

    def roster_size(self):
        return len(self.roster)

    def injury_count(self):
        return len(self.injuries)

    def summary(self):
        return {
            "League": self.league_name,
            "Owner": self.owner_name,
            "Week": self.week,
            "Roster Size": self.roster_size(),
            "Injuries": self.injury_count(),
            "Waiver Position": self.waiver_order,
            "FAAB": self.faab_remaining,
        }
    def waiver_metric_label(self):
        if self.faab_remaining is not None:
            return "FAAB Remaining"
        return "Waiver Position"
    
    def waiver_metric_value(self):
        if self.faab_remaining is not None:
            return f"${self.faab_remaining}"
        return self.waiver_order