from src.executives.executive import Executive
from src.brain.executive_brain import ExecutiveBrain

class HeadCoach(Executive):

    def __init__(self):
        super().__init__(
            name="Marcus Reed",
            title="Head Coach",
            mission="Win the current week through optimal lineup decisions and matchup planning.",
            signature_phrase="For this week's matchup..."
        )

        self.personality = [
            "Competitive",
            "Practical",
            "Short-Term Focused",
            "Direct"
        ]

        self.brain = ExecutiveBrain()

    def make_recommendation(self):
        return self.brain.create_recommendation(
            executive=self.title,
            recommendation="Prioritize players with stable weekly volume.",
            justification="The current matchup favors reliable touches over high-variance upside plays.",
            evidence=[
                "Opponent projects as a close matchup.",
                "Stable-volume players reduce lineup volatility.",
                "Flex position requires safer floor this week."
            ],
            confidence=0.84,
            risks=[
                "May reduce lineup ceiling if a boom player hits."
            ],
            departments=[
                "Analytics",
                "General Manager",
                "Medical"
            ],
        )