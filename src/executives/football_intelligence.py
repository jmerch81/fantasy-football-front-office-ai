from src.executives.executive import Executive
from src.brain.executive_brain import ExecutiveBrain

class FootballIntelligenceDirector(Executive):

    def __init__(self):
        super().__init__(
            name="Ethan Brooks",
            title="Football Intelligence Director",
            mission="Analyze external football context including weather, stadium conditions, travel, schedule, and game environment.",
            signature_phrase="Current external conditions suggest..."
        )

        self.personality = [
            "Observational",
            "Context-Aware",
            "Calm",
            "Detail-Focused"
        ]

        self.brain = ExecutiveBrain()

    def make_recommendation(self):
        return self.brain.create_recommendation(
            executive=self.title,
            recommendation="Monitor weather and game environment before finalizing lineup decisions.",
            justification="External conditions can materially affect passing volume, kicking reliability, and scoring environments.",
            evidence=[
                "High wind can reduce passing efficiency.",
                "Heavy rain can increase rushing volume.",
                "Indoor games generally reduce weather-related volatility."
            ],
            confidence=0.82,
            risks=[
                "Weather forecasts can shift close to kickoff."
            ],
            departments=[
                "Head Coach",
                "Analytics",
                "Medical"
            ],
        )