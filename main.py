from types import SimpleNamespace
from queue import SimpleQueue
from threading import Lock
from logic.data_classes import GeneratedScheduler, GenericTaquero
from logic.filling import Filling
from logic.order import Order
from logic.round_robin import RoundRobin
from logic.taquero import Taquero, TaqueroConfig
from logic.order_queue import OrderQueue

master_queue = SimpleQueue()
lock = Lock()

def send_to_master_queue(order):
    master_queue.put(order)

def generate_default_fillings():
    return [
        Filling(max_=200, name="cebolla"),
        Filling(max_=200, name="cilantro"),
        Filling(max_=150, name="salsa"),
        Filling(max_=100, name="guacamole"),
        Filling(max_=50, name="tortilla"),
    ]

def generate_default_quesadilla_stack():
    return Filling(max_=5, name="quesadilla", available=5)

def generate_generic_taquero(name, types, scheduler):
    fillings = generate_default_fillings()
    quesadillas = generate_default_quesadilla_stack()
    config = TaqueroConfig(
        name=name,
        types=types,
        fillings=fillings,
        quesadillas=quesadillas,
        lock=lock,
        send_to_master=send_to_master_queue,
        scheduler=scheduler,
    )
    taquero = Taquero(config)
    return GenericTaquero(**{
        "taquero": taquero, 
        "fillings": fillings, 
        "quesadillas": quesadillas, 
        "config": config,
    })

def generate_order_replacer(queue: OrderQueue):
    # priority mapping
    # 0 - New Order
    # 1 - Order from Taquero
    # 2 - Only Quesasdillas
    priorities = [0, 0, 1, 1, 2]
    def order_replacer(index):
        nonlocal priorities
        nonlocal queue
        return queue.get(priority=priorities[index])

    return order_replacer

def generate_scheduler():
    elements = [None for _ in range(5)]
    queue = OrderQueue()
    replacer = generate_order_replacer(queue=queue)
    scheduler = RoundRobin(elements=elements, job_replacer=replacer, lock=lock)
    return  GeneratedScheduler(**{
        "scheduler": scheduler,
        "elements": elements,
        "queue": queue,
    })

if __name__ == "__main__":
    scheduler_adobada = generate_scheduler()
    taquero_adobada = generate_generic_taquero("Taquero adobada", ["adobada"], scheduler=scheduler_adobada.scheduler)
    print(scheduler_adobada.scheduler)