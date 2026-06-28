from src.brain.recommendation import Recommendation


class ExecutiveBrain:

    def create_recommendation(
        self,
        executive,
        recommendation,
        justification,
        evidence,
        confidence,
        risks,
        departments,
    ):

        return Recommendation(
            executive=executive,
            recommendation=recommendation,
            justification=justification,
            evidence=evidence,
            confidence=confidence,
            risks=risks,
            departments_consulted=departments,
        )