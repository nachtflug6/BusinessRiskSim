from events import generate_risk_events
from disruptions import *

import timeit


def bundle_disruptions(event_tensor: th.Tensor, params: list, device='cpu'):
    output_shape = (4, *event_tensor.shape)
    output_tensor = th.zeros(size=output_shape)

    for i in range(4):
        match params[i]['disruption_type']:
            case 'u':
                output_tensor[i] = u_disruption(event_tensor, params[i]['low'], params[i]['interval'], device=device)
            case 'v':
                output_tensor[i] = v_disruption(event_tensor, params[i]['low'], params[i]['interval'], device=device)

    return output_tensor


class Risk:
    def __init__(self, name, description, probability, params: list):
        self.name = name
        self.description = description
        self.probability = probability
        self.params = params

    def evaluate_risk(self, shape, device='cpu'):
        risk_events = generate_risk_events(self.probability, shape, device=device)
        tensors = bundle_disruptions(risk_events, self.params, device=device)

        return tensors


params = [
    {'disruption_type': 'u', 'low': 0.2, 'interval': 2},
    {'disruption_type': 'v', 'low': 0.3, 'interval': (2, 2)},
    {'disruption_type': 'u', 'low': 0.4, 'interval': 2},
    {'disruption_type': 'v', 'low': 0.5, 'interval': (2, 2)},
]

start = timeit.default_timer()

#Your statements here



ris = Risk('huhu', 'huhu', 0.1, params)



print(ris.evaluate_risk((100, 1000000)).shape)

stop = timeit.default_timer()

print('Time: ', stop - start)
