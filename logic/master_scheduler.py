from typing import Dict, List

from logic.order_queue import OrderQueue


class MasterScheduler:
    def __init__(self, taco_queues: Dict[str, OrderQueue]):
        self.queues = taco_queues
        self.queue_types = self.get_types_of_queues(taco_queues)
        self.returns_queue = OrderQueue()

        # Approximates all the tacos that are remaining
        # Does not take in account prepared tacos of orders that have not been notified to the master scheduler
        self.max_remaining: Dict[str, int] = {type:0 for type in taco_queues}

    def get_types_of_queues(self, queues_by_type: Dict[str, OrderQueue]):
        # this algorithm should convert a:
        # Dict[str, OrderQueue] to Dict[OrderQueue, List[str]]
        types_by_queue: Dict[OrderQueue, List[str]] = {}
        for [type, queue] in queues_by_type.items():
            # because queue is OrderQueue and python compares those by reference
            # it is not necessary to do fancy tricks
            if not queue in types_by_queue:
                types_by_queue[queue] = []
            types_by_queue[queue].append(type)


    def tick():
        pass