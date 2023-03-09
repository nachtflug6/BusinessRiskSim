import torch as th


def generate_risk_events(p: float, instance_interval: tuple, device='cpu'):
    event_tensor = th.rand(instance_interval).to(device)
    event_tensor = th.where(event_tensor < p, 1, 0)
    return event_tensor
