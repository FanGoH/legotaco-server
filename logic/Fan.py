
from dataclasses import dataclass
from threading import Thread
import threading
from time import sleep

SPEEDUP = 0



@dataclass
class FanConfig:
    Tacos: int
    TimeToTrigger:int
    TImeOn:int


class Fan:
    def __init__(self,config:FanConfig):
        self.number_ons = 0
        self.config = config
        self.turnedOn = False

    def Launch(self):
        # Thread(target=self.watcher, args=()).start()÷
        return

    def addTacos(self,number:int = 1):
        self.config.Tacos +=number
        if self.config.Tacos  >= self.config.TimeToTrigger and not self.turnedOn:
            self.config.Tacos -= self.config.TimeToTrigger # 8_
            Thread(target=self.TurnFan,args=()).start()

    # def watcher(self):
    #     while True:
            
    #         if(self.config.Tacos % self.config.TimeToTrigger == 0 and self.config.Tacos):

    #             print("UWU")
    #             l = Thread(target=self.TurnFan,args=())
    #             l.start()
    #             l.join()

    def TurnFan(self):
        print("ventilando")
        self.turnedOn = True
        sleep(self.TimeOn)
        self.turnedOn = False
    


        

