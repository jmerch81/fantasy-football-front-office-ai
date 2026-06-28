from datetime import datetime
from typing import List


class ExecutiveMeeting:

    def __init__(self, meeting_name: str, president, attendees: List):
        self.meeting_name = meeting_name
        self.president = president
        self.attendees = attendees
        self.recommendations = []
        self.created_at = datetime.now()

    def call_to_order(self):
        return (
            f"{self.meeting_name}\n\n"
            f"{self.president.name}, {self.president.title}, has called the meeting to order."
        )

    def collect_reports(self):
        self.recommendations = []

        for executive in self.attendees:
            recommendation = executive.make_recommendation()
            self.recommendations.append(recommendation)

        return self.recommendations

    def summarize_meeting(self):
        if not self.recommendations:
            self.collect_reports()

        top_recommendation = max(
            self.recommendations,
            key=lambda recommendation: recommendation.confidence
        )

        return (
            "After reviewing all departments, the strongest recommendation is:\n\n"
            f"{top_recommendation.recommendation}\n\n"
            f"Submitted by: {top_recommendation.executive}\n"
            f"Confidence: {top_recommendation.confidence:.0%}"
        )

    def adjourn(self):
        return "Meeting adjourned. Final recommendations are ready for Owner review."