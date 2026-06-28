from dataclasses import dataclass, field
from typing import List


@dataclass
class Executive:
    name: str
    title: str
    mission: str
    signature_phrase: str

    personality: List[str] = field(default_factory=list)
    responsibilities: List[str] = field(default_factory=list)
    data_sources: List[str] = field(default_factory=list)
    reports: List[str] = field(default_factory=list)

    def introduce(self):
        print(f"{self.title}: {self.name}")
        print(self.signature_phrase)
        print()
        print(self.mission)