import threading
from typing import Callable


class RoundRobin:
    i = -1
    elements = []
    working = {}

    def __init__(self, elements: list, job_replacer: Callable, lock: threading.Lock):
        self.elements = elements
        self.replacer = job_replacer
        self.lock = lock

    def work_on_next(self, worker):
        # an instance of RoundRobin can be used buy multiple Workers at the same time
        # it should not be possible to work on the same job at the same time
        # tracking working jobs is necesary
        # we don't want to pollute the calling scope
        # our option is to use a callback function that works over the object

        # Before releasing the lock, we mark the element as being worked on
        # Avoids a context switch that can reschedule the same job
        try:
            self.lock.acquire()  # No context switching here, critical section
            self.i = self._find_next_available_index()
            self.working[self.i] = True

            element = self._get_current_element()
        except Exception as error:
            raise error
        finally:  # lock cleanup
            self.lock.release()

        # the worker needs to be called outside the lock
        # -> allows multiple elements to be worked on at the same time
        result = worker(element)

        # Finished working on the element
        # Acquiring a lock is not necessary because this is the only instance using the resource
        self.working[self.i] = False
        return result

    def _find_next_available_index(self):
        starting_index = (self.i + 1) % len(self.elements)
        next_index = starting_index

        while self.working.get(next_index, False):
            next_index = (self.i + 1) % len(self.elements)
            # If all the elements have been checked, and every one of them is being worked on,
            # We raise an exception to avoid deadlocking everything
            if starting_index == next_index:
                raise Exception("Every element is being worked on")
        return next_index

    def _get_current_element(self):
        return self.elements[self.i]

    def complete_job(self):
        self.elements[self.i] = self.replacer(self.i)
