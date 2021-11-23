

# There are 4 different types of fillings
# Each filling takes 0.5 seconds to be applied
# Therefore, the worst case for filling one quesadilla is 2 seconds
# Making one quesadilla takes 20 seconds

# The works case for making one taco is 3 seconds
# Using a quantum of 5, the worst amount of time before reading the
    # Quesadilla queue if one item is in there is 15 seconds

# Assuming that an order of 5 quesadillas is in the Quesadilla queue
    # And that one order with 15 seconds remaining is being worked on
# The first quesadilla will be used at T=17

# Therefore, if the stack is full when checked, that stack won't require
    # another quesadilla after 20 seconds
    # This only holds true when T < 20


# The quesadillero needs to know the amount of quesadilla orders that are
    # ready to be fullfilled in the queue

# The quesadillero can only be idle if there is no more quesadilla orders to be prepared
    # Where idle is doing round robin over the taquero's quesadilla stacks

# !!! THIS SCHEDULER IS NOT MULTITHREADED -> THERE IS ONLY ONE QUESADILLERO
from typing import Any, Callable
from logic.order import Order
from logic.round_robin import Scheduler

from enum import Enum

class ACTIONS(Enum):
    ORDER = 1
    IDLE = 2

class QuesadilleroScheduler:
    # The quesadillero scheduler will have 
    # one scheduler for orders 
    # and one quesadilla stacks
    def __init__(self, order_scheduler: Scheduler, stack_scheduler: Scheduler):
        self.order_scheduler = order_scheduler
        self.stack_scheduler = stack_scheduler
        pass

    def work_on_next(self, worker: Callable[[str, Any, int]]):
        # First we need to check if our order scheduler has an available order
        worked = False
        result = None
        for _ in range(self.order_scheduler.get_max_elements()):
            def inner_worker(order, handle):
                nonlocal worked
                if not order: # Order is none if there is no available
                    return
                worked = True
                return worker(ACTIONS.ORDER, order, handle)
            result = self.order_scheduler.work_on_next(inner_worker)

            if worked:
                break

        if worked:
            return result

        # If there was nothing available to work on, we default to the idle state
        def stack_worker(stack, handle):
            return worker(ACTIONS.IDLE, stack, handle)
        return self.stack_scheduler.work_on_next(stack_worker)

        
    def complete_job(self, handle, action: ACTIONS):
        if action == ACTIONS.ORDER:
            self.order_scheduler.complete_job(handle)
        # You cannot complete an IDLE job


class Quesadillero:
    def __init__(
        self,

    ):
        pass

