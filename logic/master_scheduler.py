from queue import Queue
from threading import Lock
from typing import Dict, List
from logic.SQSManager import SQSManager
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

        self.estimated_queue_wait = {queue: 0 for queue in set(taco_queues.items())}
        self.order_history = {}

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

    # When an order is "finished" from a taquero it is returned to here
    def return_order(self, order: Order, meat):
        # A type of order can only have 1 assigned queue
        queue = self.queue_types[meat]
        
        # We know that the order was worked on by some amount
        # And that it belongs to a certain queue
        # If the amount remaining before entering the queue is known
        # and the current amount remaining is also known
        # updating the estimated remaining items in the queue consists of
        # total -= (current - prev)
        prev = self.order_history[order].get(queue, 0)
        current = order.get_amount_remaining_of_type(type_=meat, class_="taco") # ???
        delta = current - prev
        self.estimated_queue_wait[queue] -= delta

        self.order_history[order][queue] = current

    def complete_order(self, order):
        del self.order_history[order]
        sqs_manager.complete_Order(order)

    def load_order(self):
        order = sqs_manager.getOrder()
        self.order_history[order] = {}
        return order

    def tick(self):
        priority = 0
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

        if not order:
            return

        # uh uh uh uh uh uh uh uh
        amount_by_type = { meat: order.get_amount_remaining_of_type(meat, "taco") for meat in self.meat_types}
        # find minimum kiwi
        min_queue = None
        min_amount = 1E100
        min_type = None
        for meat in self.meat_types:
            if amount_by_type[meat] <= 0:
                continue

            queue = self.queues[meat]
            queued_amount = self.estimated_queue_wait[queue]
            if queued_amount < min_amount:
                min_amount = queued_amount 
                min_type = meat
                min_queue = queue
        
        if not min_queue:
            # the order only has quesadillas remaining
            for meat in self.meat_types: 
                if order.get_amount_of_quesadillas(meat) > 0:
                    self.queues[meat].put(2, order)
                    return
            # the order is completed
            self.complete_order(order)
            return

        # update the order
        # i am not sure if just adding works
        # assumes that the turn works on all the elements of the queue
        self.estimated_queue_wait[min_queue] += amount_by_type[min_type]
        self.order_history[order][min_queue] = amount_by_type[min_type]
        min_queue.put(priority, order)

