from typing import Dict, List
#    {
#             "part_id": "1-0",
#             "type": "taco",
#             "meat": "suadero",
#             "status": "open",
#             "quantity": 29,
#             "ingredients": [
#                 "salsa",
#                 "cilantro",
#                 "cebolla"
#             ]
#         }


class SubOrder:
    def __init__(self, data):
        self.type = data["type"]
        self.meat = data["meat"]
        self.quantity = data["quantity"]
        self.ingredients = data["ingredients"]
    pass


# {
#     "datetime": "2021-09-14 16:15:55.421246",
#     "request_id": 1,
#     "status": "open",
#     "orden": [
#         {
#             "part_id": "1-0",
#             "type": "taco",
#             "meat": "suadero",
#             "status": "open",
#             "quantity": 29,
#             "ingredients": [
#                 "salsa",
#                 "cilantro",
#                 "cebolla"
#             ]
#         }
#     ],
#     "response": [
#         {
#             "who": "asignador",
#             "when": "2021-09-14 16:15:55.421215",
#             "what": "what",
#             "time": "123" // mili segundos
#         },
#         {
#             "who": "taqueroa asada",
#             "when": "2021-09-14 16:15:55.421215",
#             "what": "what",
#             "time": "123" // mili segundos
#         }
#     ]
# }


class Order:
    def __init__(self, raw_order, index_queue=0):
        self.raw_order = raw_order
        self.index = index_queue
        self.sub_orders: Dict[str, SubOrder] = {}
        for sub_order in raw_order["orden"]:
            meat_type = sub_order["meat"]
            if meat_type not in self.sub_orders:
                self.sub_orders[meat_type] = []
            self.sub_orders[meat_type].append(SubOrder(sub_order))

    def is_completed(self):
        total = 0
        for sub_orders in self.sub_orders.values():
            for sub_order in sub_orders:
                total += sub_order.quantity
        return total == 0

    def get_sub_orders_of_type(self, type_) -> List[SubOrder]:
        return self.sub_orders.get(type_, [])

    def get_remaining_parts_of_type(self, type_):
        return list(filter(lambda o: o.quantity > 0, self.get_sub_orders_of_type(type_)))

    def get_amount_remaining_of_type(self, type_, class_="taco"):
        return sum(map(lambda o: o.quantity, filter(lambda o: o.type == class_, self.get_remaining_parts_of_type(type_))))

    # {
    #     "who": "asignador",
    #     "when": "2021-09-14 16:15:55.421215",
    #     "what": "what",
    #     "time": "123" // mili segundos
    # },
    def log_work(self, log):
        self.raw_order["response"].append(log)

    def get_handle(self):
        return self.raw_order['handle']

    def get_amount_of_quesadillas(self, type):
        return sum(
            map(
                lambda o: o.quantity,
                filter(lambda o: o.type == "quesadilla",
                       self.get_sub_orders_of_type(type))
            )
        )
