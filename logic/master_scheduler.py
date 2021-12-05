from queue import Queue
from threading import Lock
from typing import Dict, List
from logic.SQSManager import SQSManager
from logic.master_helpers.order_helper import OrderRemaining
from logic.master_helpers.queue_tracker import QueueTracker
from logic.order import Order

from logic.order_queue import OrderQueue

sqs_manager = SQSManager(
    ["https://sqs.us-east-1.amazonaws.com/292274580527/sqs_cc106_team_1"],
    ["https://sqs.us-east-1.amazonaws.com/292274580527/sqs_cc106_team_1_response"]
)


class MasterScheduler:
    def __init__(self, taco_queues: Dict[str, OrderQueue], lock:Lock):
        self.queues = taco_queues
        self.queue_types = self.get_types_of_queues(taco_queues)
        self.returns_queue = Queue()

        self.queue_trackers = {queue: QueueTracker(meats) for queue, meats in self.queue_types.items()}

        self.estimated_queue_wait = {queue: 0 for queue in set(taco_queues.values())}

        self.meat_types = taco_queues.keys()

        self.lock = lock

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
        return types_by_queue

    # When a taquero cannot do anything else on an order, it comes to here
    # :)
    def return_order(self, order: Order, queue: OrderQueue):
        self.queue_trackers[queue].remove_order(order)
        self.returns_queue.put(order)

    def complete_order(self, order):
        sqs_manager.complete_Order(order)

    def load_order(self):
        order = sqs_manager.getOrder()
        return order

    def __get_next_order(self):
        order = None
        priority = None
        # evental consistency is good enough
        if self.returns_queue.qsize() > 0:
            # when there is a "finished order" to be rescheduled

            # this is the only consumer of the queue, 
            # we expect this to not raise any exception
            order: Order = self.returns_queue.get_nowait()
            priority = 1
        else:
            # when we need to grab a new order from the sqs
            order: Order = self.load_order()
            priority = 0
        return order, priority
    
    def __get_remaining_for_order_per_queue(self, order: Order):
        remaining: Dict[OrderQueue, OrderRemaining] = {}
        for queue, meats in self.queue_types.items():
            if queue not in remaining:
                remaining[queue] = OrderRemaining()
            for meat in meats:
                remaining[queue].taco += order.get_amount_remaining_of_type(meat, "taco")
                remaining[queue].quesadilla += order.get_amount_remaining_of_type(meat, "quesadilla")
        return {queue:remaining for queue, remaining in remaining.items() if remaining.quesadilla > 0 and remaining.taco > 0}

    def __find_suitable_queue(self, order: Order):
        remaining = self.__get_remaining_for_order_per_queue(order)

        min_taco_remaining = 1E100
        min_queue = None
        # find the order that has the least amount of tacos scheduled
        for queue, order_remaining in remaining.items():
            # if the order has no tacos to be prepared for this queue
            # just continue
            if order_remaining.taco == 0:
                continue

            tracker = self.queue_trackers[queue]
            queue_remaining = tracker.count_remaining()
            if queue_remaining.taco < min_taco_remaining:
                min_queue = queue
                min_taco_remaining = queue_remaining.taco
        return min_queue

    def __find_quesadilla_queue(self, order: Order):
        order_remaining = self.__get_remaining_for_order_per_queue(order)

        for queue, remaining in order_remaining.items():
            if remaining.quesadilla > 0:
                return queue


    def tick(self):
        order, priority = self.__get_next_order()

        # There are no orders to be assigned
        if not order:
            return
        
        if order.is_completed():
            self.complete_order(order)
            return

        destination_queue = self.__find_suitable_queue(order)

        # the order only has quesadillas
        if destination_queue is None:
            destination_queue = self.__find_quesadilla_queue(order)
            priority = 2 # Priority 2 is quesadilla order
            return
        
        destination_queue.put(priority, order)
        
        # done