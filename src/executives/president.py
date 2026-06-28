from src.executives.executive import Executive
from src.brain.executive_brain import ExecutiveBrain

class President(Executive):

    def __init__(self):
        super().__init__(
            name="Evelyn Cross",
            title="President of Football Operations",
            mission="Coordinate the executive staff, resolve disagreements, and deliver final recommendations to the Owner.",
            signature_phrase="After reviewing all departments..."
        )

        self.personality = [
            "Calm",
            "Strategic",
            "Objective",
            "Executive"
        ]

        self.brain = ExecutiveBrain()

    def make_recommendation(self):
        return self.brain.create_recommendation(
            executive=self.title,
            recommendation="Prioritize roster depth before the next waiver deadline.",
            justification="Multiple departments identified depth as the most important short-term risk.",
            evidence=[
                "General Manager flagged RB depth.",
                "Head Coach needs more weekly flexibility.",
                "Analytics projects improved win probability with stronger bench options."
            ],
            confidence=0.88,
            risks=[
                "May require sacrificing upside at another position."
            ],
            departments=[
                "General Manager",
                "Head Coach",
                "Analytics"
            ],
        )