from dataclasses import dataclass
import functools
from threading import Lock
from time import sleep
import time
import timeit
from typing import Callable

from logic.filling import Filling
from logic.order import Order
from logic.round_robin import Scheduler


QUANTUM = 5

BASE_TACO_TIME = 1
FILLING_TIME = 0.5

SPEEDUP = 0  # 1 second equals 0 seconds 8)

MAIN_PRODUCT_BASE_TIME = {
    "taco": 1,
    "quesadilla": 0,
}


@dataclass
class TaqueroConfig:
    name: str
    types: list[str]
    fillings: dict[str, Filling]
    quesadillas: Filling
    scheduler: Scheduler
    lock: Lock
    send_to_master: Callable[[Order, ], None]


class Taquero:

    def __init__(self, config: TaqueroConfig):
        self.name = config.name
        self.types = config.types
        self.fillings = config.fillings
        self.quesadillas = config.quesadillas
        self.scheduler = config.scheduler
        self.send_to_master = config.send_to_master
        self.lock = config.lock

    def work(self):
        self.scheduler.work_on_next(
            lambda order, handle: self.work_on_order(order, handle))

    def work_on_order(self, order: Order, handle: int):
        if not order:
            return
        
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
                self.lock.release()
                continue

            if not self.enough_ingredients(tacos, amount):
                work_performed.append({
                    "amount": 0,
                    "messages": "Not enough fillings",
                })
                self.lock.release()
                break
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
        self.send_to_master(order)
        self.scheduler.complete_job(handle)
        self.lock.release()

    def is_order_complete(self, order):
        return len(self.get_order_todo(order)) == 0

    def get_order_todo(self, order):
        raw_todo = map(
            lambda type: order.get_remaining_parts_of_type(type), self.types)
        todo = functools.reduce(lambda p, c: [*p, *c], raw_todo, [])
        return todo

    def enough_ingredients(self, tacos, amount):
        for filling in tacos.ingredients:
            if self.fillings[filling].available < amount:
                return False
        return True

    def use_ingredients(self, tacos, amount):
        if tacos.type == "quesadilla":
            self.quesadillas.available -= amount
        for filling in tacos.ingredients:
            self.fillings[filling].available -= amount
