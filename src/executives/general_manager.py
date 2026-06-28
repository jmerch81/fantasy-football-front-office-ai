from src.executives.executive import Executive
from src.brain.executive_brain import ExecutiveBrain


class GeneralManager(Executive):

    def __init__(self):
        super().__init__(
            name="Alex Morgan",
            title="General Manager",
            mission="Build a championship roster through strategic player acquisition, roster construction, and long-term planning.",
            signature_phrase="From a roster construction standpoint..."
        )

        self.personality = [
            "Strategic",
            "Patient",
            "Executive",
            "Risk Aware"
        ]

        self.brain = ExecutiveBrain()

    def evaluate_roster(self):
        return self.brain.create_recommendation(
            executive=self.title,
            recommendation="Acquire additional running back depth.",
            justification="Roster lacks reliable depth behind RB1.",
            evidence=[
                "Current RB depth is below league average.",
                "Upcoming bye weeks reduce flexibility.",
                "Waiver wire contains multiple upside players."
            ],
            confidence=0.91,
            risks=[
                "May require dropping a developmental player."
            ],
            departments=[
                "Analytics",
                "Scouting",
                "Head Coach"
            ],
        )

    def make_recommendation(self):
        return self.evaluate_roster()