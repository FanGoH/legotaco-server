import unittest
from random import randint

from src.round_robin import RoundRobin

class TestRoundRobin(unittest.TestCase):
    N_JOBS = 20

    def test_next_job_circular(self):
        jobs = [randint(0, 1E10) for v in range(self.N_JOBS)]
        round_robin = RoundRobin(jobs)

        for job in [*jobs, *jobs, *jobs]: # Perform three laps
            self.assertEqual(job, round_robin.next_job())

    def test_complete_job_replaces_current_job(self):
        NEW_JOB = 1E5

        jobs = list(range(10))
        replaced = list(range(10))
        replaced[5] = NEW_JOB

        round_robin = RoundRobin(jobs)
        for _ in range(5):
            round_robin.next_job()
        round_robin.complete_job(NEW_JOB)

        for old_job, new_job in zip(jobs, replaced):
            self.assertEqual(old_job, new_job)