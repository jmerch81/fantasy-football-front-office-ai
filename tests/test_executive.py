from src.executives.general_manager import GeneralManager

gm = GeneralManager()

recommendation = gm.evaluate_roster()

print()

print("=" * 60)

print("GENERAL MANAGER REPORT")

print("=" * 60)

print(recommendation.summary())

print()

print("JUSTIFICATION")

print(recommendation.justification)

print()

print("EVIDENCE")

for item in recommendation.evidence:
    print(f"• {item}")

print()

print("RISKS")

for risk in recommendation.risks:
    print(f"• {risk}")