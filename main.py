from queue import SimpleQueue
from threading import Lock, Thread
from time import sleep
from logic.chalan import Chalan
from logic.config import SPEEDUP
from logic.data_classes import GeneratedScheduler, GenericTaquero
from logic.filling import Filling
from logic.master_scheduler import MasterScheduler
from logic.quesadillero import QuesadillaJob, Quesadillero
from logic.round_robin import RoundRobin
from logic.taquero import Taquero, TaqueroConfig
from logic.order_queue import OrderQueue

lock = Lock()


def generate_default_fillings():
    filling_list = [
        Filling(max_=200, name="cebolla"),
        Filling(max_=200, name="cilantro"),
        Filling(max_=150, name="salsa"),
        Filling(max_=100, name="guacamole"),
        Filling(max_=50, name="tortilla"),
    ]
    filling = {filling.name: filling for filling in filling_list}
    return filling, filling_list

def generate_default_quesadilla_stack():
    return Filling(max_=5, name="quesadilla", available=5)

def generate_generic_taquero(name, types, scheduler, send_to_master_queue):
    fillings, fillings_list = generate_default_fillings()
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
        "fillings_list": fillings_list,
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
        # print(f"A taquero completed an order, replacing with {index}")
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
        sleep(1 * SPEEDUP)

if __name__ == "__main__":
    scheduler_adobada = generate_scheduler()
    scheduler_asada = generate_scheduler()
    scheduler_tripa = generate_scheduler()

    master_scheduler = MasterScheduler({
        "asada": scheduler_asada.queue,
        "suadero": scheduler_asada.queue,
        "tripa": scheduler_tripa.queue,
        "cabeza": scheduler_tripa.queue,
        "adobada": scheduler_adobada.queue,
    }, lock)

    taquero_adobada = generate_generic_taquero(
        name="Taquero adobada", 
        types=["adobada"], 
        scheduler=scheduler_adobada.scheduler,
        send_to_master_queue=lambda order: master_scheduler.return_order(order, scheduler_adobada.queue)
    )
    
    taquero_asada_1 = generate_generic_taquero(
        name="Taquero asada y suadero 1", 
        types=["asada", "suadero"], 
        scheduler=scheduler_asada.scheduler,
        send_to_master_queue=lambda order: master_scheduler.return_order(order, scheduler_asada.queue)
    )
    taquero_asada_2 = generate_generic_taquero(
        name="Taquero asada y suadero 2", 
        types=["asada", "suadero"], 
        scheduler=scheduler_asada.scheduler,
        send_to_master_queue=lambda order: master_scheduler.return_order(order, scheduler_asada.queue)
    )

    taquero_tripa = generate_generic_taquero(
        name="Taquero tripa y cabeza", 
        types=["tripa", "cabeza"], 
        scheduler=scheduler_tripa.scheduler,
        send_to_master_queue=lambda order: master_scheduler.return_order(order, scheduler_tripa.queue)
    )

    chalan_adobada_asada = Chalan([*taquero_adobada.fillings_list, *taquero_asada_1.fillings_list], lock)
    chalan_tripa_asada = Chalan([*taquero_tripa.fillings_list, *taquero_asada_2.fillings_list], lock)

    quesadillero = Quesadillero(
        scheduler=RoundRobin(
            elements=[
                QuesadillaJob(quesadilla_stack=taquero_adobada.quesadillas, type="hola :)"),
                QuesadillaJob(quesadilla_stack=taquero_asada_1.quesadillas, type="hola :)"),
                QuesadillaJob(quesadilla_stack=taquero_asada_2.quesadillas, type="hola :)"),
                QuesadillaJob(quesadilla_stack=taquero_tripa.quesadillas, type="hola :)"),
            ],
            job_replacer=None,
            lock=lock
        ),
        lock=lock
    )




    taquero_adobada_thread = Thread(target=put_taquero_to_work, args=(taquero_adobada.taquero,))
    taquero_asada_1_thread = Thread(target=put_taquero_to_work, args=(taquero_asada_1.taquero,))
    taquero_asada_2_thread = Thread(target=put_taquero_to_work, args=(taquero_asada_2.taquero,))
    taquero_tripa_thread = Thread(target=put_taquero_to_work, args=(taquero_tripa.taquero,))

    chalan_adobada_asada_thread = Thread(target=put_taquero_to_work, args=(chalan_adobada_asada,))
    chalan_tripa_asada_thread = Thread(target=put_taquero_to_work, args=(chalan_tripa_asada,))

    quesadillero_thread = Thread(target=put_taquero_to_work, args=(quesadillero,))
    
    taquero_adobada_thread.start()
    taquero_asada_1_thread.start()
    taquero_asada_2_thread.start()
    taquero_tripa_thread.start()
    
    chalan_adobada_asada_thread.start()
    chalan_tripa_asada_thread.start()

    quesadillero_thread.start()

    

    while True:
        print("Master tick")
        master_scheduler.tick()
