from src.executives.executive import Executive
from src.brain.executive_brain import ExecutiveBrain

class ScoutingDirector(Executive):

    def __init__(self):
        super().__init__(
            name="Jordan Blake",
            title="Director of Scouting",
            mission="Identify sleepers, breakout candidates, undervalued players, and future roster upside.",
            signature_phrase="From our scouting reports..."
        )

        self.personality = [
            "Optimistic",
            "Upside-Focused",
            "Aggressive",
            "Creative"
        ]

        self.brain = ExecutiveBrain()

    def make_recommendation(self):
        return self.brain.create_recommendation(
            executive=self.title,
            recommendation="Reserve one bench spot for a high-upside breakout candidate.",
            justification="Championship teams often separate themselves by identifying breakout players before the market reacts.",
            evidence=[
                "Bench depth allows calculated upside swings.",
                "Early breakout identification creates waiver advantage.",
                "Scouting profile favors opportunity growth."
            ],
            confidence=0.79,
            risks=[
                "Upside players may provide limited short-term production."
            ],
            departments=[
                "General Manager",
                "Analytics"
            ],
        )