import torch as th
import pandas as pd


class RiskGen:
    def __init__(self, risks: pd.DataFrame, batch_size=10, parallel_runs=10, device='cpu'):
        self.risks = risks
        num_risks = len(risks.index)
        self.num_risks = len(risks.index)
        self.batch_size = batch_size
        self.device = device
        print(risks['reduction'].values)
        self.probability_tensor = th.from_numpy(risks['probability'].values).repeat(parallel_runs, batch_size, 1).to(device)
        print(th.from_numpy(risks['reduction'].values))
        self.reduction_tensor = th.from_numpy(risks['reduction'].values).repeat(parallel_runs, 1).to(device)
        print(self.reduction_tensor)
        self.delay_tensor = th.from_numpy(risks['recover_time'].values).repeat(parallel_runs, 1).to(device)
        self.cooldown_tensor = th.zeros_like(self.delay_tensor).to(device)

    def get_risk_tensor(self):

        device = self.device
        batch_size = self.batch_size
        probability_tensor = self.probability_tensor
        cooldown_tensor = self.cooldown_tensor
        reduction_tensor = self.reduction_tensor

        event_tensor = th.where(probability_tensor > th.rand(probability_tensor.shape).to(device), 1, 0)
        risk_impact_tensor = th.zeros_like(event_tensor).to(device)

        for i in range(batch_size):
            risk_impact_tensor[:, i, :] = \
                th.where((((event_tensor[:, i, :] > 0) & (cooldown_tensor == 0)) | (cooldown_tensor > 0)), reduction_tensor, 0)
            cooldown_tensor = th.where((event_tensor[:, i, :] > 0) & (cooldown_tensor == 0), self.delay_tensor,
                                        cooldown_tensor - 1)
            cooldown_tensor = th.where(cooldown_tensor < 0, 0, cooldown_tensor)

        self.cooldown_tensor = cooldown_tensor

        return risk_impact_tensor

    def get_module_assignment_vec(self):
        pass




# device = 'cuda' if th.cuda.is_available() else 'cpu'
# print(device)
#
# def test():
#
#     num_risks = 6
#     batch_size = 20
#     parallel_runs = 1
#     num_batches = 1000
#
#
#
#     probability_tensor = th.rand(1, 1, num_risks) / 10
#     probability_tensor.to(device)
#     # countdown_tensor = th.ones_like(probability_tensor) * 10
#
#
#     countdown_tensor = th.zeros(parallel_runs, num_risks).to(device)
#     repair_tensor = th.randint(5, 6, countdown_tensor.shape).to(device)
#
#
#
#     for k in range(num_batches):
#         new_probability_tensor = probability_tensor.repeat(parallel_runs, batch_size, 1).to(device)
#         event_tensor = th.where(new_probability_tensor > th.rand(new_probability_tensor.shape).to(device), 1, 0).to(device)
#         new_event_tensor = th.zeros_like(event_tensor).to(device)
#
#         for i in range(batch_size):
#
#             new_event_tensor[:, i, :] = th.where((((event_tensor[:, i, :] > 0) & (countdown_tensor == 0)) | (countdown_tensor > 0)), 1, 0)
#             countdown_tensor = th.where((event_tensor[:, i, :] > 0) & (countdown_tensor == 0), repair_tensor, countdown_tensor - 1)
#             countdown_tensor = th.where(countdown_tensor < 0, 0, countdown_tensor)
#
#     print(new_event_tensor)

