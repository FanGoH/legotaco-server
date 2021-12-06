import random
import copy
from datetime import datetime
import simplejson as json


def generate_tacos():
    tacos = []
    type = ["taco", "quesadilla"]
    meat = ["asada", "adobada", "suadero", "tripa", "cabeza"]
    fillings = ["cebolla", "cilantro", "salsa", "guacamole"]
    for x in range(5):
        taco = {
            "datetime": str(datetime.now()),
            "request_id": x,
            "status": "open",
            "orden": [],
            "response":[]
        }
        for y in range(random.randrange(5)):
            tp =random.choice(type)
            taco["orden"].append(
                {
                    "part_id": "{0}-{1}".format(x, y),
                    "type": tp ,
                    "meat": random.choice(meat),
                    "status": "open",
                    "quantity": random.randrange(50) if tp =='taco' else random.randrange(5),
                    "ingredients": []
                }
            )
            local_fillings = copy.deepcopy(fillings)
            for z in range(random.randrange(len(local_fillings))):
                ind_filling = random.choice(local_fillings)
                taco["orden"][y]["ingredients"].append(ind_filling)
                local_fillings.remove(ind_filling)

        tacos.append(taco)

    tacos_file = open("tacos.json", "w")
    tacos_file.write(json.dumps(tacos))
    tacos_file.close()


generate_tacos()
