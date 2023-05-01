import torch as th


class SimModule:
    def __init__(self, idx, product_idx):
        self.idx = idx
        self.product_idx = product_idx


class ProductionModule(SimModule):
    def __init__(self, idx, product_idx, prod_mod_idx, product_vec, max_capacity):
        SimModule.__init__(self, idx, product_idx)
        self.prod_mod_idx = prod_mod_idx
        self.max_capacity = max_capacity
        self.current_capacity = 1
        self.product_vec = product_vec

        self.corrected_prod_vec = th.where(self.product_vec > 0, self.product_vec, th.iinfo(th.int32).max)

        if th.sum(product_vec) > 0:
            self.origin_mod = False
        else:
            self.origin_mod = True

    def process(self, inventory_tensor, production_tensor, device):

        self.product_vec = self.product_vec.to(device)
        output_inventory_tensor = inventory_tensor
        output_production_tensor = production_tensor
        current_capacity = int(th.floor(self.max_capacity * self.current_capacity))

        if self.origin_mod:
            num_produced = current_capacity
            output_inventory_tensor[1, self.prod_mod_idx, self.product_idx] += num_produced
            output_production_tensor[0, self.prod_mod_idx] = num_produced

        else:
            current_vec = output_inventory_tensor[0, self.prod_mod_idx, :]
            current_inventory = th.min(th.where(self.product_vec > 0, current_vec.to(device) // self.corrected_prod_vec.to(device), th.iinfo(th.int32).max))
            num_produced = min(current_inventory, current_capacity)
            output_inventory_tensor[0, self.prod_mod_idx, :] -= self.product_vec * num_produced
            output_inventory_tensor[1, self.prod_mod_idx, self.product_idx] += num_produced
            output_production_tensor[0, self.prod_mod_idx] = num_produced

        return output_inventory_tensor, production_tensor


class TransportModule:
    def __init__(self, idx, product_idx, trans_mod_idx, input_mod_idx, output_mod_idx, max_capacity):
        SimModule.__init__(self, idx, product_idx)
        self.idx = idx
        self.trans_mod_idx = trans_mod_idx
        self.input_mod_idx = input_mod_idx
        self.output_mod_idx = output_mod_idx
        self.max_capacity = max_capacity
        self.current_capacity = 1

    def process(self, inventory_tensor, transport_tensor, device):
        output_inventory_tensor = inventory_tensor
        output_transport_tensor = transport_tensor
        current_inventory = output_inventory_tensor[1, self.input_mod_idx, self.product_idx]
        num_transport = min(int(th.floor(self.max_capacity * self.current_capacity)), current_inventory)
        output_inventory_tensor[0, self.output_mod_idx, self.product_idx] += num_transport
        output_inventory_tensor[1, self.input_mod_idx, self.product_idx] -= num_transport
        output_transport_tensor[0, self.trans_mod_idx] = num_transport

        return output_inventory_tensor, output_transport_tensor
