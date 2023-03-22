from .product import Product

class Module:
    def __init__(self, name, risks, product: Product, suppliers=[], output_step=1000, output_warehouse_max=None):

        assert product.match_to_suppliers(suppliers)
        self.name = name
        self.risks = risks
        self.product = product
        self.suppliers = suppliers
        self.parts_step = output_step
        self.output_warehouse_max = output_warehouse_max
        self.input_warehouse_stock = 0
        self.input_warehouse_stock = 0
        self.risks = risks
        self.capacity = 1
        self.capacities = []

    # def produce(self):
    #
    #
    #     current_capacity = get_risk_capacities(self.risks)
    #     self.capacities.append(current_capacity)
    #
    #     output_stock = self.parts_step * current_capacity
    #
    #     return output_stock