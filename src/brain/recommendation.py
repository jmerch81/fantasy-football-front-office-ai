from dataclasses import dataclass
from typing import List


@dataclass
class Recommendation:
    executive: str
    recommendation: str
    justification: str
    evidence: List[str]
    confidence: float
    risks: List[str]
    departments_consulted: List[str]

    def summary(self):

        return (
            f"{self.executive}\n"
            f"Recommendation: {self.recommendation}\n"
            f"Confidence: {self.confidence:.0%}"
        )