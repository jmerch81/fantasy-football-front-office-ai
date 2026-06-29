from src.executives.president import President
from src.executives.general_manager import GeneralManager
from src.executives.head_coach import HeadCoach
from src.executives.analytics_director import AnalyticsDirector
from src.executives.scouting_director import ScoutingDirector
from src.executives.medical_director import MedicalDirector
from src.executives.football_intelligence import FootballIntelligenceDirector


class FrontOffice:

    def __init__(self):
        self.president = President()

        self.executives = [
            GeneralManager(),
            HeadCoach(),
            AnalyticsDirector(),
            ScoutingDirector(),
            MedicalDirector(),
            FootballIntelligenceDirector(),
        ]