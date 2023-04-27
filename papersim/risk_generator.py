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
    def __init__(self, risks, num_modules, device='cpu'):
        self.device = device

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

        self.probabilities = th.tensor(probabilities, dtype=th.float64)
        self.impacts = th.tensor(impacts, dtype=th.float64)
        self.delays = th.tensor(delays, dtype=th.int32)
        self.module_assignment = th.tensor(module_assignment, dtype=th.int32)
        self.cooldown = th.zeros_like(self.delays, dtype=th.int32)

        self.risk_impact_tensor = th.zeros_like(self.probabilities, dtype=th.float64)

    def step(self):

        probability_tensor = self.probabilities.to(self.device)
        impact_tensor = self.impacts.to(self.device)
        delay_tensor = self.delays.to(self.device)
        cooldown_tensor = self.cooldown.to(self.device)

        event_tensor = th.where(probability_tensor > th.rand(probability_tensor.shape).to(self.device), 1, 0).to(self.device)

        risk_impact_tensor = th.where((((event_tensor > 0) & (cooldown_tensor == 0)) | (cooldown_tensor > 0)), impact_tensor, 0)
        cooldown_tensor = th.where((event_tensor > 0) & (cooldown_tensor == 0), delay_tensor, cooldown_tensor - 1)

        cooldown_tensor = th.where(cooldown_tensor < 0, 0, cooldown_tensor)
        self.cooldown = cooldown_tensor

        self.risk_impact_tensor = risk_impact_tensor
        return risk_impact_tensor

    def get_cap_i(self, i):
        return th.min(th.ones_like(self.risk_impact_tensor) - self.risk_impact_tensor.mul(th.flatten(self.module_assignment[:, i])))