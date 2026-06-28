from src.executives.president import President
from src.executives.general_manager import GeneralManager
from src.executives.head_coach import HeadCoach
from src.executives.analytics_director import AnalyticsDirector
from src.executives.scouting_director import ScoutingDirector
from src.executives.medical_director import MedicalDirector
from src.executives.football_intelligence import FootballIntelligenceDirector
from src.meetings.executive_meeting import ExecutiveMeeting


president = President()

attendees = [
    GeneralManager(),
    HeadCoach(),
    AnalyticsDirector(),
    ScoutingDirector(),
    MedicalDirector(),
    FootballIntelligenceDirector(),
]

meeting = ExecutiveMeeting(
    meeting_name="Tuesday Executive Meeting",
    president=president,
    attendees=attendees
)

print("=" * 60)
print(meeting.call_to_order())
print("=" * 60)

reports = meeting.collect_reports()

for report in reports:
    print()
    print(report.summary())

print()
print("=" * 60)
print("PRESIDENT'S SUMMARY")
print("=" * 60)
print(meeting.summarize_meeting())

print()
print(meeting.adjourn())