from dataclasses import dataclass
from typing import Dict, List
from logic.order import Order
from logic.order_queue import OrderQueue
from logic.round_robin import Scheduler

from logic.taquero import Taquero, TaqueroConfig
from logic.filling import Filling

@dataclass
class GenericTaquero:
    taquero: Taquero
    fillings: Dict[str, Filling]
    fillings_list: List[Filling]
    quesadillas: Filling
    config: TaqueroConfig

@dataclass
class GeneratedScheduler:
    scheduler: Scheduler
    elements: List[Order]
    queue: OrderQueue

