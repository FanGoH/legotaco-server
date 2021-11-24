from queue import SimpleQueue
from threading import Lock
from logic.filling import Filling
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

def generate_order_replacer(queue):
    # priority mapping
    # 0 - New Order
    # 1 - Order from Taquero
    # 2 - Only Quesasdillas
    priorities = [0, 0, 1, 1, 2]
    pass

adobada_fillings = generate_default_fillings
adobada_config = TaqueroConfig(
    name="Taquero Adobada",
    types=["adobada"],
    fillings=adobada_fillings,
    lock=Lock,
    send_to_master=send_to_master_queue
)

adobada_queue = OrderQueue()
