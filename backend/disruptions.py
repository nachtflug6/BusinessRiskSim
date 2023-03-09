import torch as th


def u_disruption(event_tensor: th.Tensor, low: float, interval: int, device='cpu', negative=False):
    negative_low = 1 - low
    event_shape = event_tensor.shape
    output_shape = (event_shape[0], event_shape[1] + interval)

    if negative:
        output_tensor = th.zeros(size=output_shape, dtype=th.float64, device=device)
        slide_tensor = event_tensor * negative_low
        for i in range(interval):
            output_tensor[:, i:-(interval - i)] += slide_tensor

    else:
        output_tensor = th.ones(size=output_shape, dtype=th.float64, device=device)
        slide_tensor = event_tensor * negative_low
        for i in range(interval):
            output_tensor[:, i:-(interval - i)] -= slide_tensor

    output_tensor = output_tensor[:, :-interval]
    output_tensor = th.where(output_tensor < 0, 0, output_tensor)
    return output_tensor


def v_disruption(event_tensor: th.Tensor, low: float, interval: tuple, device='cpu', negative=False):

    negative_low = 1 - low
    event_shape = event_tensor.shape
    down_interval = interval[0]
    up_interval = interval[1]
    interval = down_interval + up_interval + 1
    output_shape = (event_shape[0], event_shape[1] + interval)

    down_step = negative_low / down_interval
    up_step = negative_low / up_interval

    if negative:
        output_tensor = th.zeros(size=output_shape, dtype=th.float64, device=device)
        slide_tensor = th.zeros_like(event_tensor, dtype=th.float64)
        for i in range(interval):
            if i < down_interval:
                slide_tensor += down_step * event_tensor
            else:
                slide_tensor -= up_step * event_tensor

            output_tensor[:, i:-(interval - i)] += slide_tensor

    else:
        output_tensor = th.ones(size=output_shape, dtype=th.float64, device=device)
        slide_tensor = th.zeros_like(event_tensor, dtype=th.float64)
        for i in range(interval):
            if i < down_interval:
                slide_tensor -= down_step * event_tensor
            else:
                slide_tensor += up_step * event_tensor

            output_tensor[:, i:-(interval - i)] += slide_tensor

    output_tensor = output_tensor[:, down_interval:-(up_interval + 1)]
    output_tensor = th.where(output_tensor < 0, 0, output_tensor)
    return output_tensor
