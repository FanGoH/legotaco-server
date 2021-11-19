from queue import Queue
from typing import Dict

class OrderQueue:
    queues: Dict[int, Queue] = {}

    def put(self, priority: int, order):
        if priority not in self.queues:
            self.queues[priority] = Queue()
        self.queues[priority].put(order)

    def get(self, priority: int):
        if priority not in self.queues:
            return None
        if self.queues[priority].empty():
            return None
        return self.queues[priority].get()
