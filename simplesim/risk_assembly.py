class RiskAssembly:
    def __init__(self, risk_list):
        self.risk_list = risk_list

    def get_risk_capacities(self, risks):
        if type(risks) is list:
            capacity = 1
            for risk in risks:
                risk_capacity = self.get_risk_capacities(risk)
                if risk_capacity < capacity:
                    capacity = risk_capacity

        elif type(risks) is tuple:
            capacity = 0
            for risk in risks:
                capacity += self.get_risk_capacities(risk)
            capacity /= len(risks)

        else:
            capacity = risks.evaluate()

        return capacity
