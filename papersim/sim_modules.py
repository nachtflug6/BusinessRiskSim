import torch as th

class Module:
    def __init__(self, mod_idx, prod_idx, prod_vec, max_capacity):

        self.prod_vec = prod_vec
        self.corrected_prod_vec = th.where(self.prod_vec > 0, self.prod_vec, th.iinfo(th.int32).max)

        if th.sum(prod_vec) > 0:
            self.origin_mod = False
        else:
            self.origin_mod = True

        self.mod_idx = mod_idx
        self.prod_idx = prod_idx
        self.max_capacity = max_capacity
        self.current_capacity = 1

    def process(self, input_tensor):

        output_tensor = input_tensor
        current_capacity = int(th.floor(self.max_capacity * self.current_capacity))
        if self.origin_mod:
            output_tensor[1, self.mod_idx, self.prod_idx] += current_capacity
            num_produced = current_capacity
        else:
            current_vec = output_tensor[0, self.mod_idx, :]
            current_inventory = th.min(th.where(self.prod_vec > 0, current_vec // self.corrected_prod_vec, th.iinfo(th.int32).max))
            num_produced = min(current_inventory, current_capacity)
            output_tensor[0, self.mod_idx, :] -= self.prod_vec * num_produced
            output_tensor[1, self.mod_idx, self.prod_idx] += num_produced

        return output_tensor, num_produced


class Transition:
    def __init__(self, idx, input_mod_idx, output_mod_idx, prod_idx, max_capacity):
            self.idx = idx
            self.input_mod_idx = input_mod_idx
            self.output_mod_idx = output_mod_idx
            self.prod_idx = prod_idx
            self.max_capacity = max_capacity
            self.current_capacity = 1

    def process(self, input_tensor):
        output_tensor = input_tensor
        current_inventory = output_tensor[1, self.input_mod_idx, self.prod_idx]
        num_transport = min(int(th.floor(self.max_capacity * self.current_capacity)), current_inventory)
        output_tensor[0, self.output_mod_idx, self.prod_idx] += num_transport
        output_tensor[1, self.input_mod_idx, self.prod_idx] -= num_transport

        return output_tensor