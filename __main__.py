from queue import SimpleQueue
from logic.sockets import server

class PriorityQueue:
 def __init__(self):
    self.newOrder =SimpleQueue()
    self.PreviosulyWorkedOrders=SimpleQueue()
    self.PausedOrder=SimpleQueue()

def RoundRobin():
    pass
    #implement Round Robin

def Taqueria():
    pass

server()