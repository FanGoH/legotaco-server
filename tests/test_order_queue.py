import unittest

from logic.order_queue import OrderQueue

PRIORITY = 2
ORDER = 5

class TestOrderQueue(unittest.TestCase):

    def test_add_order(self):
        order_queue = OrderQueue()
        order_queue.put(PRIORITY, ORDER)
        self.assertEqual(ORDER, order_queue.get(PRIORITY))

    def test_get_order_invalid_priority(self):
        order_queue = OrderQueue()
        self.assertIsNone(order_queue.get(PRIORITY))

    def test_get_order_empty_priority(self):
        order_queue = OrderQueue()
        order_queue.put(PRIORITY, ORDER)
        order_queue.get(PRIORITY)
        self.assertIsNone(order_queue.get(PRIORITY))
