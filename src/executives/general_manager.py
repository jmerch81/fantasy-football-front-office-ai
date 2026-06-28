from src.executives.executive import Executive


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