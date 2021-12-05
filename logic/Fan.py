
from dataclasses import dataclass
from threading import Thread
import threading
from time import sleep


@dataclass
class FanConfig:
    Tacos: int
    TimeToTrigger:int
    TImeOn:int


class Fan:
    def __init__(self,config:FanConfig):
        self.config = config
        self.turnedOn = False


    def Launch(self):
         pass
         Thread(target=self.watcher, args=()).start()

    def addTacos(self,number:int = 1):
        if(not self.turnedOn):
            self.config.Tacos +=number


    def watcher(self):
        while True:
            if(self.config.Tacos % self.config.TimeToTrigger == 0 and self.config.Tacos):
                l = Thread(target=self.TurnFan,args=())
                l.start()
                l.join()

    def TurnFan(self):
        self.turnedOn = True
        sleep(self.TimeOn)
        self.turnedOn = False
    


        

