from src.decision_center.decision_center import DecisionCenter


decision_center = DecisionCenter()

president_report = decision_center.get_president_recommendation()
top_report = decision_center.get_top_recommendation()

print("PRESIDENT REPORT")
print(president_report.summary())

print()
print("TOP EXECUTIVE RECOMMENDATION")
print(top_report.summary())