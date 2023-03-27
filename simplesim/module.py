from .product import Product

class Module:
    def __init__(self, name: str, product: str, part_capacity=1000):

        self.name = name
        self.product = product
        self.suppliers = {}
        self.risks = []
        self.parts_step = part_capacity
        self.capacity = 1
        self.capacities = []

    def add_risk(self, risk_name):

        self.risks.append(risk_name)

    def add_supplier(self, supplier_name: str, product_name: str):

        if product_name in self.suppliers:
            self.suppliers[product_name].append(supplier_name)
        else:
            self.suppliers[product_name] = [supplier_name]







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