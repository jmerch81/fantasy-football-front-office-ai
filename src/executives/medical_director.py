from src.executives.executive import Executive
from src.brain.executive_brain import ExecutiveBrain

class MedicalDirector(Executive):

    def __init__(self):
        super().__init__(
            name="Dr. Sofia Ramirez",
            title="Sports Medicine Director",
            mission="Evaluate player availability, injury risk, workload concerns, and health-related roster decisions.",
            signature_phrase="From a health perspective..."
        )

        self.personality = [
            "Cautious",
            "Risk-Averse",
            "Detail-Oriented",
            "Protective"
        ]

        self.brain = ExecutiveBrain()

    def make_recommendation(self):
        return self.brain.create_recommendation(
            executive=self.title,
            recommendation="Avoid relying on players carrying elevated injury risk unless alternatives are weak.",
            justification="Availability is a critical part of weekly lineup reliability.",
            evidence=[
                "Injured players carry higher volatility.",
                "Limited practice participation can signal reduced workload.",
                "Reinjury risk can affect both weekly output and long-term roster stability."
            ],
            confidence=0.86,
            risks=[
                "Could miss upside if a questionable player performs well."
            ],
            departments=[
                "Head Coach",
                "General Manager",
                "Football Intelligence"
            ],
        )