import threading

class RoundRobin:
    i = 0
    elements = []
    working = {}

    def __init__(self, elements: list, job_replacer: function[int], lock: threading.Lock):
        self.elements = elements
        self.replacer = job_replacer
        self.lock = lock

    def work_on_next(self, worker):
        # an instance of RoundRobin can be used buy multiple Workers at the same time
        # it should not be possible to work on the same job at the same time
        # tracking working jobs is necesary
            # we don't want to pollute the calling scope
            # our option is to use a callback function that works over the object
        self.lock.acquire()
        
        self.lock.release()
        return

    def complete_job(self):
        self.elements[self.i] = self.replacer(self.i)

