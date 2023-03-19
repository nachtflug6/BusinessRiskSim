from .events import generate_risk_events
from .disruptions import *

import timeit

def get_disruptions(event_tensor: th.Tensor, params: list, device='cpu'):
    num_disruptions = len(params)
    output_tensor = th.zeros_like(event_tensor)

    for i in range(num_disruptions):
        match params[i]['disruption_type']:
            case 'u':
                output_tensor[i] = u_disruption(event_tensor[i], params[i]['low'], params[i]['interval'], device=device)
            case 'v':
                output_tensor[i] = v_disruption(event_tensor[i], params[i]['low'], params[i]['interval'], device=device)

    return output_tensor


class Risk:
    def __init__(self, risk_params: dict):
        self.name = risk_params['name']
        self.description = risk_params['description']
        self.probability = risk_params['probability']
        self.num_propagating_values = len(risk_params['disruptions'])
        self.params = risk_params['disruptions']

    def evaluate_risk(self, shape, device='cpu'):
        risk_events = generate_risk_events(self.probability, shape, device=device)
        tensors = get_disruptions(risk_events, self.params, device=device)

        return tensors

    def display(self, shape, device='cpu'):
        assert len(shape) == 2
        shape = (self.num_propagating_values, *shape)
        event_tensor = th.zeros(shape)
        event_tensor[:, :, 3] = 1
        tensors = get_disruptions(event_tensor, self.params, device=device)
        return tensors




