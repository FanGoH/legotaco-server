from queue import SimpleQueue
from threading import Lock
from logic.filling import Filling
from logic.order import Order
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
        name="Taquero Adobada",
        types=["adobada"],
        fillings=fillings,
        quesadillas=quesadillas,
        lock=Lock,
        send_to_master=send_to_master_queue,
        scheduler=scheduler,
    )
    taquero = Taquero(config)
    return taquero, fillings, quesadillas, config

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
