import collections
from typing import Deque, Dict, List

from logic.master_helpers.order_helper import OrderRemaining
from logic.order import Order

# The queue tracker is only accessed by one thread
class QueueTracker:
    def __init__(self, meats):
        self.meats = meats
        # The deque interface is similar to the one for a linked_list
        # Change later?
        self.orders: Dict[str, Order]= {}

    # Complexity O(n * k) -> good enough it is at max O(2n)
    def count_remaining(self):
        remaining = OrderRemaining()
        for order in self.orders.keys():
            for meat in self.meats:
                remaining.taco += order.get_amount_remaining_of_type(meat, "taco")
                remaining.quesadilla += order.get_amount_remaining_of_type(meat, "quesadilla")
        return remaining

        
    def add_order(self, order):
        self.orders[order] = True
        pass

    def remove_order(self, order):
        if order not in self.orders:
            return
        del self.orders[order]