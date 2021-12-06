from dataclasses import dataclass
from threading import Lock
from time import sleep
from logic.filling import Filling
from logic.round_robin import Scheduler

from logic.config import SPEEDUP

@dataclass
class QuesadillaJob:
    quesadilla_stack: Filling
    type: str


class Quesadillero:
    def __init__(
        self,
        scheduler: Scheduler,
        lock: Lock
    ):
        self.scheduler = scheduler
        self.lock = lock

    def work(self):
        self.scheduler.work_on_next(lambda job, _: self.make_quesadillas(job))

    def make_quesadillas(self, quesadilla_job: QuesadillaJob):
        amount = quesadilla_job.quesadilla_stack.available
        if amount >= quesadilla_job.quesadilla_stack.max:
            return
        
        sleep(20 * SPEEDUP)

        self.lock.acquire()
        quesadilla_job.quesadilla_stack.available += 1
        self.lock.release()











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


# class QuesadillaQueue:
#     def __init__(self):
#         self.queue = SimpleQueue()
#         self.queued_amount = 0
#         pass

#     def get(self):
#         order, amount = self.queue.get_nowait()  # mejor
#         return (order, amount)
    
#     # remember, after completing a set of quesadillas subtrac the remaining from here
#     def complete(self, amount):
#         self.queued_amount -= amount

#     def put(self, order, amount):
#         self.queued_amount += amount
#         self.queue.put((order, amount))

#     def get_quesadillas_amount(self):
#         return self.queued_amount


# class QuesadilleroScheduler:
#     # The quesadillero scheduler will have
#     # one scheduler for orders
#     # and one quesadilla stacks
#     def __init__(self, order_scheduler: Scheduler, stack_scheduler: Scheduler):
#         self.order_scheduler = order_scheduler
#         self.stack_scheduler = stack_scheduler
#         pass

#     def work_on_next(self, worker: Callable[[QuesadillaJob, int]]):
#         # First we need to check if our order scheduler has an available order
#         worked = False
#         result = None
#         for _ in range(self.order_scheduler.get_max_elements()):
#             def inner_worker(quesadilla_job, handle):
#                 nonlocal worked
#                 if not quesadilla_job:  # Order is none if there is no available
#                     return
#                 worked = True
#                 return worker(quesadilla_job, handle)
#             result = self.order_scheduler.work_on_next(inner_worker)

#             if worked:
#                 break

#         if worked:
#             return result

#         # If there was nothing available to work on, we default to the idle state
#         def stack_worker(quesadilla_job, handle):
#             return worker(quesadilla_job, handle)
#         return self.stack_scheduler.work_on_next(stack_worker)

#     # this may only receive handles for the order_scheduler
#     def complete_job(self, handle):
#         self.order_scheduler.complete_job(handle)

