import unittest
from threading import Lock, Thread
from time import sleep

from logic.round_robin import RoundRobin

ELEMENTS = [1,2,3,4,5]
JOB_REPLACER = lambda i: ELEMENTS[i] # idk
LOCK = Lock()

N_ROUNDS = 3


class TestRoundRobin(unittest.TestCase):
    def test_work_on_next(self):
        round_robin = RoundRobin(ELEMENTS, JOB_REPLACER, LOCK)
        
        def worker(element):
            return element
        for i in range(len(ELEMENTS) * 3):
            result = round_robin.work_on_next(worker)
            self.assertEquals(result, ELEMENTS[i%len(ELEMENTS)])

    def test_work_on_same(self):
        round_robin = RoundRobin(ELEMENTS, JOB_REPLACER, LOCK)
        
        def worker(element):
            sleep(1)
            return element
        
        threads = []
        for _ in ELEMENTS:
            thread = Thread(target=round_robin.work_on_next, args=(worker, ))
            threads.append(thread)
            thread.start()
        self.assertRaises(Exception, lambda:round_robin.work_on_next(worker))
    
    
        
        
        

            
