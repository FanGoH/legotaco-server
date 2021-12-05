from queue import SimpleQueue
from threading import Lock, Thread
from logic.chalan import Chalan
from logic.data_classes import GeneratedScheduler, GenericTaquero
from logic.filling import Filling
from logic.master_scheduler import MasterScheduler
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


def put_taquero_to_work(taquero):
    while True:
        taquero.work()

if __name__ == "__main__":
    scheduler_adobada = generate_scheduler()
    taquero_adobada = generate_generic_taquero(
        name="Taquero adobada", 
        types=["adobada"], 
        scheduler=scheduler_adobada.scheduler
    )
    
    scheduler_asada = generate_scheduler()
    taquero_asada_1 = generate_generic_taquero(
        name="Taquero asada y suadero 1", 
        types=["asada", "suadero"], 
        scheduler=scheduler_asada.scheduler
    )
    taquero_asada_2 = generate_generic_taquero(
        name="Taquero asada y suadero 2", 
        types=["asada", "suadero"], 
        scheduler=scheduler_asada.scheduler
    )

    scheduler_tripa = generate_scheduler()
    taquero_tripa = generate_generic_taquero(
        name="Taquero tripa y cabeza", 
        types=["tripa", "cabeza"], 
        scheduler=scheduler_tripa.scheduler
    )

    chalan_adobada_asada = Chalan([taquero_adobada.fillings, taquero_asada_1.fillings], lock)
    chalan_tripa_asada = Chalan([taquero_tripa.fillings, taquero_asada_2.fillings], lock)

    master_scheduler = MasterScheduler({
        "asada": scheduler_asada.queue,
        "suadero": scheduler_asada.queue,
        "tripa": scheduler_tripa.queue,
        "cabeza": scheduler_tripa.queue,
        "adobada": scheduler_adobada.queue,
    }, lock)

    taquero_adobada_thread = Thread(target=put_taquero_to_work, args=(taquero_adobada,))
    taquero_asada_1_thread = Thread(target=put_taquero_to_work, args=(taquero_asada_1,))
    taquero_asada_2_thread = Thread(target=put_taquero_to_work, args=(taquero_asada_2,))
    taquero_tripa_thread = Thread(target=put_taquero_to_work, args=(taquero_tripa,))

    taquero_adobada_thread.start()
    taquero_asada_1_thread.start()
    taquero_asada_2_thread.start()
    taquero_tripa_thread.start()
    

    while True:
        print("Working :)")
        master_scheduler.tick()
