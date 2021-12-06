
from threading import Lock
from typing import List
from time import sleep

from logic.filling import Filling
from logic.round_robin import RoundRobin
from logic.config import SPEEDUP
#porque ese List en lugar de list?
# a, es que es un tipo en lugar de una lista
#l barto
#porque divides?
# para decir llene tanto de esto * tiempo 8)
# y porque no lo calcular mejor(?)
# nose
# yakedo el cahalan 8)

times = {
    "cebolla":10/200, 
    "cilantro":10/200, 
    "salsa":15/150, 
    "guacamole":20/100,
    "tortilla": 5/50 # uy, no tome en cuenta las tortillas en el taquero 8)
    # igual, solo es cambiar una cosita facil
}

class Chalan:
    def __init__(self, containers: List[Filling], lock: Lock):
        self.scheduler = RoundRobin(
            containers,
            None,
            lock
        )
        self.lock = lock

    def work(self):
        return self.scheduler.work_on_next(lambda filling, _: self.fill_filling(filling))
    
    def fill_filling(self, filling: Filling):
        self.lock.acquire()
        to_fill = filling.max - filling.available
        time = to_fill * times.get(filling.name, 0)
        self.lock.release()

        if to_fill == 0:
            return
        sleep(time * SPEEDUP)

        self.lock.acquire()
        filling.available += to_fill
        self.lock.release()
        return to_fill, time