import unittest
from threading import Lock
from logic.order import Order

from main import generate_generic_taquero, generate_scheduler

SENTINEL_ORDER = {
    "sentinel": True,
    "orden": [
        {
            "part_id": "1-0",
            "type": "quesadilla",
            "meat": "suadero",
            "status": "open",
            "quantity": 27,
            "ingredients": [
                    "salsa",
            ]
        },
    ],
    "response": []
}


def create_sentinel_order(sentinel_value):
    base = {
        "sentinel": sentinel_value,
        "orden": [
            {
                "part_id": "1-0",
                "type": "quesadilla",
                "meat": "suadero",
                "status": "open",
                "quantity": 25,
                "ingredients": [
                    "salsa",
                ]
            },
        ],
        "response": []
    }

    return Order(base)


lock = Lock()


PRIORITIES = [0, 0, 1, 1, 2]
class TestGenerateScheduler(unittest.TestCase):
    def test_add_orders(self):
        scheduler = generate_scheduler()
        taquero = generate_generic_taquero(
            name="Taquero Test",
            types=["carnitas"],
            scheduler=scheduler.scheduler,
        )

        # Fill the queue with sentinel values
        for i, p in enumerate(PRIORITIES):
            scheduler.queue.put(
                priority=p, order=create_sentinel_order((i, p)))

        for i, p in enumerate(PRIORITIES):
            taquero.taquero.work()
            # Verify that the priority and index of the sentinel is the same
            # as the one of the inserted elements
            # Assumes that the taquero works in roundrobing
            self.assertEqual(
                scheduler.elements[i].raw_order["sentinel"], (i, p))
    
    def test_shared_scheduler(self):
        scheduler = generate_scheduler()
        taquero_1 = generate_generic_taquero(
            name="Taquero Test 1",
            types=["carnitas"],
            scheduler=scheduler.scheduler,
        )
        taquero_2 = generate_generic_taquero(
            name="Taquero Test 2",
            types=["carnitas no"],
            scheduler=scheduler.scheduler,
        )

        for i, p in enumerate([*PRIORITIES, *PRIORITIES]):
            scheduler.queue.put(
                priority=p, order=create_sentinel_order((i, p)))

        taquero_1.taquero.work()
        taquero_2.taquero.work()
        taquero_1.taquero.work()
        taquero_1.taquero.work()
        taquero_2.taquero.work()

        for i, p in enumerate(PRIORITIES):
            # Verify that the priority and index of the sentinel is the same
            # as the one of the inserted elements
            # Assumes that the taquero works in roundrobing
            self.assertEqual(
                scheduler.elements[i].raw_order["sentinel"], (i, p))
