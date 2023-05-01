import torch as th
import numpy as np


class Risk:
    def __init__(self, probability, impact, delay, exposed_modules, global_effect=False):
        self.probability = probability
        self.impact = impact
        self.delay = delay
        self.exposed_modules = exposed_modules
        self.global_effect = global_effect


class RiskGen:
    def __init__(self, risks, num_modules, num_runs, device='cpu'):
        self.device = device
        self.num_runs = num_runs
        self.num_modules = num_modules

        probabilities = []
        impacts = []
        delays = []
        module_assignment = []

        for risk in risks:
            if risk.global_effect:
                probabilities.append(risk.probability)
                impacts.append(risk.impact)
                delays.append(risk.delay)
                risk_assignment_vec = np.zeros(num_modules)
                for exposed_module in risk.exposed_modules:
                    risk_assignment_vec[exposed_module] = 1
                module_assignment.append(risk_assignment_vec)
            else:
                for exposed_module in risk.exposed_modules:
                    probabilities.append(risk.probability)
                    impacts.append(risk.impact)
                    delays.append(risk.delay)
                    risk_assignment_vec = np.zeros(num_modules)
                    risk_assignment_vec[exposed_module] = 1
                    module_assignment.append(risk_assignment_vec)

        self.original_probabilities = th.tensor(np.array(probabilities), dtype=th.float64).repeat(num_runs, 1).to(device)
        self.num_risks = len(probabilities)
        self.probabilities = self.original_probabilities
        self.impacts = th.tensor(np.array(impacts), dtype=th.float64).repeat(num_runs, 1).to(device)
        self.delays = th.tensor(np.array(delays), dtype=th.int32).repeat(num_runs, 1).to(device)
        self.cooldown = th.zeros_like(self.delays, dtype=th.int32).to(device)
        self.module_assignment = th.tensor(np.array(module_assignment), dtype=th.int32).to(device)
        self.risk_impact_tensor = th.zeros_like(self.probabilities, dtype=th.float64).to(device)

    def step(self):

        probability_tensor = self.probabilities
        impact_tensor = self.impacts
        delay_tensor = self.delays
        cooldown_tensor = self.cooldown

        event_tensor = th.where(probability_tensor > th.rand(probability_tensor.shape).to(self.device), 1, 0).to(self.device)

        risk_impact_tensor = th.where((((event_tensor > 0) & (cooldown_tensor == 0)) | (cooldown_tensor > 0)), impact_tensor, 0)
        cooldown_tensor = th.where((event_tensor > 0) & (cooldown_tensor == 0), delay_tensor, cooldown_tensor - 1)

        cooldown_tensor = th.where(cooldown_tensor < 0, 0, cooldown_tensor)
        self.cooldown = cooldown_tensor

        self.risk_impact_tensor = risk_impact_tensor
        return risk_impact_tensor

    def get_cap(self):

        risk_impact_tensor = self.risk_impact_tensor.repeat(self.num_modules, 1, 1).swapaxes(1, 2).swapaxes(0, 2)
        module_assignment = self.module_assignment.unsqueeze(0)

        output = risk_impact_tensor.mul(module_assignment)
        output = th.max(output, axis=1).values
        output = th.ones_like(output) - output
        return output

    def reduce_risk_i(self, i, factor=0.1):
        multiplier = th.ones_like(self.original_probabilities)
        multiplier[i] = 1 - factor
        self.probabilities = self.original_probabilities * multiplier

