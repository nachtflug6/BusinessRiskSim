from .product import Product

class Module:
    def __init__(self, name, risks, product: Product, suppliers=[], output_step=1000, output_warehouse_max=None):

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


        # preproducts = []
        #
        # for preproduct in product.preproducts:
        #     if preproduct[0] not in preproducts:
        #         preproducts.append(preproduct[0])
        #
        # suppliers_product = []
        #
        # for supplier in suppliers:
        #     if supplier.product not in suppliers_product:
        #         suppliers_product.append(suppliers_product)
        #
        # if set(preproducts) == set(suppliers_product):
        #     return True
        # else:
        #     return False





    # def produce(self):
    #
    #
    #     current_capacity = get_risk_capacities(self.risks)
    #     self.capacities.append(current_capacity)
    #
    #     output_stock = self.parts_step * current_capacity
    #
    #     return output_stock