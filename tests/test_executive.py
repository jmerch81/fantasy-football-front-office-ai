from src.executives.president import President
from src.executives.general_manager import GeneralManager
from src.executives.head_coach import HeadCoach
from src.executives.analytics_director import AnalyticsDirector
from src.executives.scouting_director import ScoutingDirector
from src.executives.medical_director import MedicalDirector
from src.executives.football_intelligence import FootballIntelligenceDirector


executives = [
    President(),
    GeneralManager(),
    HeadCoach(),
    AnalyticsDirector(),
    ScoutingDirector(),
    MedicalDirector(),
    FootballIntelligenceDirector(),
]

for executive in executives:
    recommendation = executive.make_recommendation()

    print()
    print("=" * 60)
    print(f"{executive.title.upper()} REPORT")
    print("=" * 60)
    print(recommendation.summary())
    print()
    print("JUSTIFICATION")
    print(recommendation.justification)