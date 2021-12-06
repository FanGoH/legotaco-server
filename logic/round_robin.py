import threading
from typing import Any, Callable

class Scheduler:
    def complete_job(self, handle):
        pass
    def get_max_elements(self) -> int:
        pass
    def work_on_next(self, work: Callable[[Any, int], Any]):
        pass


class RoundRobin(Scheduler):

    def __init__(self, elements: list, job_replacer: Callable, lock: threading.Lock):
        self.elements = elements
        self.replacer = job_replacer
        self.lock = lock

        self.i = -1
        self.working = {}

    def work_on_next(self, work):
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
            i = self.i
            self.working[i] = True

            element = self._get_current_element()
        except Exception as error:
            self.working[i] = False
            raise error
        finally:
            self.lock.release()

        # the worker needs to be called outside the lock
        # -> allows multiple elements to be worked on at the same time
        result = work(element, i)

        # Finished working on the element
        # Acquiring a lock is not necessary because this is the only instance using the resource
        
        self.working[i] = False
        return result

    def _find_next_available_index(self):
        starting_index = (self.i + 1) % len(self.elements)
        next_index = starting_index

        while self.working.get(next_index, False):
            next_index = (next_index + 1) % len(self.elements)
            # If all the elements have been checked, and every one of them is being worked on,
            # We raise an exception to avoid deadlocking everything
            if starting_index == next_index:
                raise Exception("Every element is being worked on")
        return next_index

    def _get_current_element(self):
        return self.elements[self.i]

    def get_max_elements(self):
        return len(self.elements)

    def complete_job(self, handle):
        self.elements[handle] = self.replacer(handle)
