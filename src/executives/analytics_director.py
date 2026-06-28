from src.executives.executive import Executive
from src.brain.executive_brain import ExecutiveBrain

class AnalyticsDirector(Executive):

    def __init__(self):
        super().__init__(
            name="Dr. Maya Chen",
            title="Director of Analytics",
            mission="Use data, models, projections, and simulations to support evidence-based decisions.",
            signature_phrase="The numbers indicate..."
        )

        self.personality = [
            "Data-Driven",
            "Objective",
            "Precise",
            "Skeptical"
        ]

        self.brain = ExecutiveBrain()

    def make_recommendation(self):
        return self.brain.create_recommendation(
            executive=self.title,
            recommendation="Target players with strong opportunity share and improving usage trends.",
            justification="Opportunity-based metrics are more predictive than single-week fantasy point totals.",
            evidence=[
                "Usage trends stabilize faster than touchdowns.",
                "Targets and carries are stronger indicators than box score spikes.",
                "Projected opportunity has higher signal than recent fantasy points alone."
            ],
            confidence=0.90,
            risks=[
                "Usage trends can change quickly after injuries or role changes."
            ],
            departments=[
                "Scouting",
                "General Manager",
                "Head Coach"
            ],
        )