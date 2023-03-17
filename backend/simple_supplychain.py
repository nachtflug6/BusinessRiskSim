class SimpleSupplychain:
    def __init__(self, companies):
        self.companies = companies

    def simulate(self, input_production):
        for company in self.companies:
            output_production = company.simulate(input_production)
            input_production = output_production
        return output_production



