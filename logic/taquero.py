from dataclasses import dataclass
import functools
from threading import Lock, Thread
from time import sleep
import time
from typing import Callable, Dict, List
from logic.Fan import FanConfig,Fan
from logic.filling import Filling
from logic.order import Order, SubOrder
from logic.round_robin import Scheduler
from logic.config import SPEEDUP
import jsons
import json

QUANTUM = 5

BASE_TACO_TIME = 1
FILLING_TIME = 0.5

# 1 second equals 0 seconds 8)

MAIN_PRODUCT_BASE_TIME = {
    "taco": 1,
    "quesadilla": 0,
}


@dataclass
class TaqueroConfig:
    name: str
    types: List[str]
    fillings: Dict[str, Filling]
    quesadillas: Filling
    scheduler: Scheduler
    lock: Lock
    send_to_master: Callable[[Order, ], None]


Fanconfig = FanConfig
Fanconfig.Tacos = 0
Fanconfig.TImeOn = 60
Fanconfig.TimeToTrigger = 600

class Taquero:

    def __init__(self, config: TaqueroConfig):
        self.name = config.name
        self.types = config.types
        self.fillings = config.fillings
        self.quesadillas = config.quesadillas
        self.scheduler = config.scheduler
        self.send_to_master = config.send_to_master
        self.lock = config.lock
        self.Fan = Fan(Fanconfig)
        self.amountPrepared = 0
        self.resting = False
        self.TimesRested = 0
        self.Fan.Launch()

    def work(self):
        self.scheduler.work_on_next(
            lambda order, handle: self.work_on_order(order, handle))

    def work_on_order(self, order: Order, handle: int):
        if not order: # just complete the non existent order to repopulate the scheduler
            self.complete_order(order, handle)
            # print(f"{self.name} - No order to work :(")
            return

        # print(f"{self.name} - I am working on order", jsons.dumps(order))

        if(self.amountPrepared // 100 > self.TimesRested):
            self.TimesRested += 1
            self.resting = True
            sleep(3 * SPEEDUP)
            self.resting  =False
        
        remaining_quantum = QUANTUM
        work_performed = []

        todo = self.get_order_todo(order)
        start = time.time()
        for tacos in todo:
            if remaining_quantum == 0:
                break
            # and order may only be worked by one thread at the same time
            # this is in case of scaling or something
            self.lock.acquire()
            amount = tacos.quantity if tacos.quantity < remaining_quantum else remaining_quantum
            
            if tacos.type == 'quesadilla' and amount > self.quesadillas.available:
                amount = self.quesadillas.available
            if tacos.type == 'taco' and amount > self.fillings["tortilla"].available:
                amount = self.fillings["tortilla"].available

            if not self.enough_ingredients(tacos, amount) or amount == 0:
                # work_performed.append({
                #     "amount": 0,
                #     "messages": "Not enough fillings",
                # })
                self.lock.release()
                continue
            remaining_quantum -= amount
            tacos.quantity -= amount  # -= is not threadsafe

            self.use_ingredients(tacos, amount)
            self.lock.release()

            prep_time = self.calculate_preparation_time(tacos, amount)
            
            work_performed.append({
                "amount": amount,
                "fillings": tacos.ingredients,
                "type": tacos.type,
                "meat": tacos.meat,
                "prep_time": prep_time,
            })
            
            sleep(prep_time * SPEEDUP)

            self.Fan.addTacos(amount)
            self.amountPrepared += amount

        end = time.time()

        work_log = {
            "who": self.name,
            "when": time.time(),
            "what": work_performed,
            "time": end-start,
        }

        order.log_work(work_log)
        if self.is_order_complete(order):
            self.complete_order(order, handle)

    def calculate_preparation_time(self, tacos, amount):
        base_time = MAIN_PRODUCT_BASE_TIME[tacos.type] * amount
        fillings_time = FILLING_TIME * len(tacos.ingredients) * amount
        return base_time + fillings_time

    def complete_order(self, order, handle):
        self.lock.acquire()
        # yes
        if order is not None:
            self.send_to_master(order)
        self.scheduler.complete_job(handle)
        self.lock.release()

    def is_order_complete(self, order):
        return len(self.get_order_todo(order)) == 0

    def get_order_todo(self, order):
        raw_todo = map(lambda type: order.get_remaining_parts_of_type(type), self.types)
        todo = functools.reduce(lambda p, c: [*p, *c], raw_todo, [])

        taco_parts = filter(lambda todo_: todo_.type == "taco", todo)
        quesadilla_parts = filter(lambda todo_: todo_.type == "quesadilla", todo)
        todo = [*taco_parts, *quesadilla_parts]

        print(f"{self.name} - this is what i have to do: ", todo)
        return todo

    def enough_ingredients(self, tacos, amount):
        for filling in tacos.ingredients:
            if self.fillings[filling].available < amount:
                return False
        return True

    def use_ingredients(self, tacos, amount):
        if tacos.type == "quesadilla":
            self.quesadillas.available -= amount
        if tacos.type == "taco":
            self.fillings["tortilla"].available -= amount
        for filling in tacos.ingredients:
            self.fillings[filling].available -= amount

    def performLog(self):
        f = open(f"{self.name}.json", 'w')
        data =  json.load(f)
        datas = jsons.dumps(self)
        data.append(datas)
        json.dump(data,f)

    def log_action(self, event_name, action_log):
        f = open(f"output/taquero-{self.name}.json", 'w')
        data =  json.load(f)
        if not event_name in data:
            data[event_name] = []
        data[event_name].append(action_log)
        json.dump(data,f)
        f.close()
