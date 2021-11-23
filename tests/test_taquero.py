from threading import Lock
import unittest
from logic.filling import Filling
from logic.order import Order
from logic.round_robin import RoundRobin

from logic.taquero import Taquero, TaqueroConfig

import jsons

from test_order import test_object

lock = Lock()

class TestTaquero(unittest.TestCase):
    
    def generate_taquero_config(self, scheduler):
        return TaqueroConfig(
            "Taquero Juan",
            ["asada", "suadero"],
            {
                "salsa": Filling(1E100),
                "cilantro": Filling(1E100),
                "cebolla": Filling(1E100)
            },
            scheduler,
            lock,
            lambda order: order
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
    
    def test_work_on_order(self):
        scheduler = self.generate_scheduler()
        taquero_config = self.generate_taquero_config(scheduler)
        taquero = Taquero(taquero_config)

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
        scheduler = self.generate_scheduler()
        taquero_config = self.generate_taquero_config(scheduler)
        taquero = Taquero(taquero_config)

        remaining = list(scheduler.elements[0].get_remaining_parts_of_type("suadero"))
        while remaining[0].quantity >= 5:
            taquero.work()
            remaining = list(scheduler.elements[0].get_remaining_parts_of_type("suadero"))

        self.assertEquals(remaining[0].quantity, 4) 
        taquero.work() # finishes the current element at index 0, works 1 on the next
        remaining = list(scheduler.elements[0].get_remaining_parts_of_type("suadero"))
        self.assertEquals(remaining[0].quantity, 28)

    def test_work_log_generated(self):
        scheduler = self.generate_scheduler()
        taquero_config = self.generate_taquero_config(scheduler)
        taquero = Taquero(taquero_config)

        OPERATIONS = 10
        for v in range(OPERATIONS):
            taquero.work()
        
        order = scheduler.elements[0]
        print(jsons.dumps(order))
        self.assertEquals(len(order.raw_order["response"]), OPERATIONS)
        