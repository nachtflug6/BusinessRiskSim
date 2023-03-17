class Company:
    def __init__(self, risks):
        self.risks = risks
        self.inputs = []
        self.outputs = []

    def simulate(self, input_production):
        output_production = self.risks(input_production)
        self.inputs.append(input_production)
        self.outputs.append(output_production)
        return output_production



