import unittest

from logic.order import Order

test_object = {
    "orden": [
        {
            "part_id": "1-0",
            "type": "taco",
            "meat": "suadero",
            "status": "open",
            "quantity": 29,
            "ingredients": [
                "salsa",
                "cilantro",
                "cebolla"
            ]
        },
        {
            "part_id": "1-0",
            "type": "taco",
            "meat": "suadero",
            "status": "open",
            "quantity": 29,
            "ingredients": [
                "salsa",
                "cilantro",
                "cebolla"
            ]
        },
        {
            "part_id": "1-0",
            "type": "taco",
            "meat": "suadero",
            "status": "open",
            "quantity": 29,
            "ingredients": [
                "salsa",
                "cilantro",
                "cebolla"
            ]
        },
        {
            "part_id": "1-0",
            "type": "taco",
            "meat": "suadero",
            "status": "open",
            "quantity": 29,
            "ingredients": [
                "salsa",
                "cilantro",
                "cebolla"
            ]
        },
    ],
    "response": []
}


class TestOrder(unittest.TestCase):
    def test_classificate_orders_by_meat_on_creation(self):
        order = Order(test_object)
        type_ = "suadero"
        self.assertEqual(len(order.sub_orders[type_]), len(
            list(filter(lambda t: t["meat"] == type_, test_object["orden"]))))

    def test_get_remaining_orders_of_type_all_remaining(self):
        order = Order(test_object)
        type_ = "suadero"
        self.assertEqual(
            len(list(filter(lambda t: t["meat"]
                == type_, test_object["orden"]))),
            len(list(order.get_remaining_parts_of_type(type_)))
        )

    def test_get_remaining_orders_of_type_some_remaining(self):
        COMPLETED = 2
        type_ = "suadero"

        order = Order(test_object)
        for _ in range(COMPLETED):
            list(order.get_remaining_parts_of_type(type_))[0].quantity = 0

        self.assertEqual(
            len(list(filter(lambda t: t["meat"] ==
                type_, test_object["orden"]))) - COMPLETED,
            len(list(order.get_remaining_parts_of_type(type_)))
        )

    def test_get_remaining_orders_of_type_zero_remaining(self):
        type_ = "suadero"

        order = Order(test_object)
        for _ in list(order.get_remaining_parts_of_type(type_)):
            list(order.get_remaining_parts_of_type(type_))[0].quantity = 0

        self.assertEqual(
            0,
            len(list(order.get_remaining_parts_of_type(type_)))
        )
