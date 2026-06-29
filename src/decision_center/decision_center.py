from src.executives.front_office import FrontOffice


class DecisionCenter:

    def __init__(self):
        self.front_office = FrontOffice()

    def collect_executive_reports(self):
        reports = []

        for executive in self.front_office.executives:
            reports.append(executive.make_recommendation())

        return reports

    def get_president_recommendation(self):
        return self.front_office.president.make_recommendation()

    def get_top_recommendation(self):
        reports = self.collect_executive_reports()

        return max(
            reports,
            key=lambda report: report.confidence
        )