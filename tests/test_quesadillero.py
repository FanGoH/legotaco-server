from threading import Lock
import unittest
from logic.filling import Filling

from logic.quesadillero import QuesadillaJob, Quesadillero
from logic.round_robin import RoundRobin

lock = Lock()

class TestQuesadillero(unittest.TestCase):

    def test_quesadillero_schedule_making(self):
        asada_job = QuesadillaJob(
            quesadilla_stack=Filling(5, available=0),
            type="asada"
        )
        adobada_job = QuesadillaJob(
            quesadilla_stack=Filling(5, available=0),
            type="adobada"
        )
        carnitas_job = QuesadillaJob(
            quesadilla_stack=Filling(5, available=0),
            type="carnitas"
        )
        ### No le se a los tests
        # a metete la extension de python test explorer
        # y te vas al este que parece tubo de ensayo
        # el proyecto ya esta configurado, entonces deberian de salirte ahi
        # No jalan en  liveshare
        # te pide permisos o algo asi? o que
        # quedise?
        scheduler = RoundRobin(
            [asada_job, adobada_job, carnitas_job],
            None,
            lock
        )

        quesadillero = Quesadillero(scheduler=scheduler, lock=lock)

        quesadillero.work()
        self.assertEqual(asada_job.quesadilla_stack.available, 1)
        self.assertEqual(adobada_job.quesadilla_stack.available, 0)

        quesadillero.work()
        self.assertEqual(asada_job.quesadilla_stack.available, 1)
        self.assertEqual(adobada_job.quesadilla_stack.available, 1)

        quesadillero.work()
        quesadillero.work()
        self.assertEqual(asada_job.quesadilla_stack.available, 2)
        self.assertEqual(adobada_job.quesadilla_stack.available, 1)