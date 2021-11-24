from threading import Lock
import unittest

from logic.chalan import Chalan, times
from logic.filling import Filling

lock = Lock()

class TestChalan(unittest.TestCase):
    def test_chalan_round_robin(self):
        extreme_fillings = [
            Filling(max_=10, available=0, name="cebolla"),
            Filling(max_=10, available=0, name="cilantro"),
            Filling(max_=10, available=0, name="salsa"),
            Filling(max_=10, available=0, name="guacamole"),
            Filling(max_=10, available=0, name="tortilla"),
            Filling(max_=20, available=0, name="cebolla"),
            Filling(max_=20, available=0, name="cilantro"),
            Filling(max_=20, available=0, name="salsa"),
            Filling(max_=20, available=0, name="guacamole"),
            Filling(max_=20, available=0, name="tortilla"),
        ]
        chalan = Chalan(extreme_fillings, lock)

        for filling in extreme_fillings:
            amount, time = chalan.work()
            self.assertEqual(amount, filling.max)
            self.assertEqual(filling.available, filling.max)
            self.assertEqual(time, times[filling.name] * amount)
            