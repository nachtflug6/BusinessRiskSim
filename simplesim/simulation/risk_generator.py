import torch as th
import pandas as pd


class RiskGen:
    def __init__(self, risks, batch_size, parallel_runs):
        self.risks = risks
        self.batch_size = batch_size


        print(risks)
        self.probability_tensor = th.tensor(risks['probability'].values).repeat(parallel_runs, batch_size, 1)
        self.reduction_tensor = th.tensor(risks['reduction'].values)
        self.delay_tensor = th.tensor(risks['delay'].values)


        self.remaining_delay = th.zeros_like(self.probability_tensor)


        print(self.probability_tensor)


    def get_risk_vector(self):
        return th.where(self.probability_tensor >= th.rand(self.probability_tensor.shape), 1, 0)

    def get_module_assignment_vec(self):
        pass


device = 'cuda' if th.cuda.is_available() else 'cpu'
print(device)

def test():

    num_risks = 6
    batch_size = 20
    parallel_runs = 1
    num_batches = 1000



    probability_tensor = th.rand(1, 1, num_risks) / 10
    probability_tensor.to(device)
    # countdown_tensor = th.ones_like(probability_tensor) * 10


    countdown_tensor = th.zeros(parallel_runs, num_risks).to(device)
    repair_tensor = th.randint(5, 6, countdown_tensor.shape).to(device)



    for k in range(num_batches):
        new_probability_tensor = probability_tensor.repeat(parallel_runs, batch_size, 1).to(device)
        event_tensor = th.where(new_probability_tensor > th.rand(new_probability_tensor.shape).to(device), 1, 0).to(device)
        new_event_tensor = th.zeros_like(event_tensor).to(device)

        for i in range(batch_size):

            new_event_tensor[:, i, :] = th.where((((event_tensor[:, i, :] > 0) & (countdown_tensor == 0)) | (countdown_tensor > 0)), 1, 0)
            countdown_tensor = th.where((event_tensor[:, i, :] > 0) & (countdown_tensor == 0), repair_tensor, countdown_tensor - 1)
            countdown_tensor = th.where(countdown_tensor < 0, 0, countdown_tensor)

    print(new_event_tensor)

