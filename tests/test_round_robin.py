import unittest
from threading import Lock, Thread
from time import sleep

from logic.round_robin import RoundRobin

ELEMENTS = [1,2,3,4,5]
# LOCK = Lock()

N_ROUNDS = 3


class TestRoundRobin(unittest.TestCase):
    def test_work_on_next(self):
        round_robin = RoundRobin(ELEMENTS,  lambda i, j: i, Lock())
        
        def worker(element, i):
            return element
        for i in range(len(ELEMENTS) * 3):
            result = round_robin.work_on_next(worker)
            self.assertEquals(result, ELEMENTS[i%len(ELEMENTS)])

    def test_work_on_same(self):
        round_robin = RoundRobin(ELEMENTS, lambda i, j: i, Lock())
        running = True
        def worker(element, i):
            while running:
                continue
            return element
        
        threads = []
        for _ in ELEMENTS:
            thread = Thread(target=round_robin.work_on_next, args=(worker, ))
            threads.append(thread)
            thread.start()
        self.assertRaises(Exception, lambda:round_robin.work_on_next(worker))
        running = False
    
    def test_completed_job_gets_replaced(self):
        replacer = lambda i: -1
        round_robin = RoundRobin(ELEMENTS, replacer, Lock())

        round_robin.complete_job(0)
        for _ in range(len(ELEMENTS)):
            round_robin.work_on_next(lambda i, j: i)
        def worker(element, i):
            self.assertEqual(element, -1)
        round_robin.work_on_next(worker)

            
