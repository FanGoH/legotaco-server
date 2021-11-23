from threading import Lock
import unittest
from logic.filling import Filling
from logic.order import Order, SubOrder
from logic.round_robin import RoundRobin

from logic.taquero import Taquero, TaqueroConfig

import jsons

from test_order import test_object

lock = Lock()

class TestTaquero(unittest.TestCase):
    
    def generate_taquero_config(self, scheduler):
        return TaqueroConfig(
            name="Taquero Juan",
            types=["asada", "suadero"],
            fillings={
                "salsa": Filling(1E100),
                "cilantro": Filling(1E100),
                "cebolla": Filling(1E100)
            },
            scheduler=scheduler,
            lock=lock,
            send_to_master=lambda order: order
        )

    def generate_sample_order(self):
        return Order(test_object)

    def generate_scheduler(self):
        def replacer(i):
            return self.generate_sample_order()

        return RoundRobin(
            [self.generate_sample_order()],
            replacer,
            lock
        )

    def generate_default_taquero(self, return_subproducts=False):
        scheduler = self.generate_scheduler()
        taquero_config = self.generate_taquero_config(scheduler)
        taquero = Taquero(taquero_config)
        if return_subproducts:
            return taquero, taquero_config, scheduler
        return taquero
    
    def test_work_on_order(self):
        taquero, _, scheduler = self.generate_default_taquero(True)

        taquero.work()
        remaining = list(scheduler.elements[0].get_remaining_parts_of_type("suadero"))

        # The starting amount is 29, we worked 1 QUANTUM = 5
        self.assertEquals(remaining[0].quantity, 24)
        self.assertEquals(remaining[1].quantity, 29)

        taquero.work()
        remaining = list(scheduler.elements[0].get_remaining_parts_of_type("suadero"))

        self.assertEquals(remaining[0].quantity, 19)
        self.assertEquals(remaining[1].quantity, 29)

    def test_work_on_order_finish_sub_order(self):
        taquero, _, scheduler = self.generate_default_taquero(True)

        remaining = list(scheduler.elements[0].get_remaining_parts_of_type("suadero"))
        while remaining[0].quantity >= 5:
            taquero.work()
            remaining = list(scheduler.elements[0].get_remaining_parts_of_type("suadero"))

        self.assertEquals(remaining[0].quantity, 4) 
        taquero.work() # finishes the current element at index 0, works 1 on the next
        remaining = list(scheduler.elements[0].get_remaining_parts_of_type("suadero"))
        self.assertEquals(remaining[0].quantity, 28)

    def test_work_log_generated(self):
        taquero, _, scheduler = self.generate_default_taquero(True)
        OPERATIONS = 10
        for _ in range(OPERATIONS):
            taquero.work()
        
        order = scheduler.elements[0]
        print(jsons.dumps(order))
        self.assertEquals(len(order.raw_order["response"]), OPERATIONS)

    def test_calculate_prep_time(self):
        taquero = self.generate_default_taquero()
        tacos = SubOrder({
            "type": "taco",
            "ingredients": ["cebolla", "salsa"],
            "meat": "suadero",
            "quantity": 1,
        })
        self.assertEquals(taquero.calculate_preparation_time(tacos, 10), 1 * 10 + (0.5 + 0.5) * 10)
        
        tacos = SubOrder({
            "type": "quesadilla",
            "ingredients": ["cebolla", "salsa"],
            "meat": "suadero",
            "quantity": 1,
        })
        self.assertEquals(taquero.calculate_preparation_time(tacos, 10), 20 * 10 + (0.5 + 0.5) * 10)

        tacos = SubOrder({
            "type": "quesadilla",
            "ingredients": ["cebolla", "salsa"],
            "meat": "suadero",
            "quantity": 1,
        })
        self.assertEquals(taquero.calculate_preparation_time(tacos, 0), 0)

        tacos = SubOrder({
            "type": "quesadilla",
            "ingredients": [],
            "meat": "suadero",
            "quantity": 1,
        })
        self.assertEquals(taquero.calculate_preparation_time(tacos, 10), 20 * 10)
        pass
        