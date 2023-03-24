

class Product:
    def __init__(self, name: str):
        # for preproduct in preproducts:
        #     assert type(preproduct) == tuple
        #     assert len(preproduct) == 2
        #     assert type(preproduct[0]) == Product
        #     assert type(preproduct[1]) == int

        self.name = name
        self.preproducts = []

    def add_preproduct(self, preproduct):
        assert type(preproduct) == PreProduct
        self.preproducts.append(preproduct)


class PreProduct:
    def __init__(self, product: Product, num: int):
        product = product
        num = num

    # def match_to_suppliers(self, suppliers: [Module]):
    #     preproducts = []
    #
    #     for preproduct in self.preproducts:
    #         if preproduct[0] not in preproducts:
    #             preproducts.append(preproduct[0])
    #
    #     suppliers_product = []
    #
    #     for supplier in suppliers:
    #         if supplier.product not in suppliers_product:
    #             suppliers_product.append(suppliers_product)
    #
    #     if set(preproducts) == set(suppliers_product):
    #         return True
    #     else:
    #         return False
