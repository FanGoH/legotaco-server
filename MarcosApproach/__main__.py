from threading import Thread
from time import sleep, time
import json
from queue import SimpleQueue
import os

quantum = 5
times={
    "cebolla":10, "cilantro":10, "salsa":15, "guacamole":20,"tortillas": 5
}
maximos ={
    "cebolla":200, "cilantro":200, "salsa":150, "guacamole":100, "tortillas":50
}
def Taquero(queue:SimpleQueue,meats,tortillas,quesadillas,Fillings):
    while True:
        if(not queue.empty()):
            datos = queue.get()
            ordenes = datos['orden']
            no = datos['request_id']
            print(f"Atendiento Orden : {no}")
            i =0
            time = 0
            for element in ordenes:
                time = 0
                if(i==quantum):
                    break
            
                if (element['meat'] not in meats) or element['status']=='closed':
                    continue
                qty =0
                
                
                
                if(element['quantity']>quantum):
                    if(element['type']=="quesadilla" ):
                        qs = quesadillas['quesadillas']
                        if (qs <element['quantity']):
                            if qs==0:
                                #print("No quesadillas, waiting for more, skipping order until there is a quesadilla")
                                continue
                            #print(f"Not enough Quesadillas, preparing only {qs}")
                            qty = qs
                        else:
                            qty = element['quantity']
                    
                    
                
                    else:
                        if(tortillas['tortillas']==0):
                            #print("No hay tortillas['tortillas'] pasando a la siguiente orden")
                            continue
        
                        if (tortillas['tortillas'] >element['quantity']):
                            qty = quantum
                        ts = tortillas['tortillas']
                        if(ts < element['quantity']):
                
                            qty = quantum    
                        time+=qty
                    i+=qty
                
                
                elif (element['quantity']<= quantum):
                    if(element['type']=="quesadilla" ):
                        qs = quesadillas['quesadillas']
                        if (qs <element['quantity']):
                            if qs==0:
                                #print("No quesadillas, waiting for more, skipping order until there is a quesadilla")
                                continue
                            #print(f"Not enough Quesadillas, preparing only {qs}")
                            qty = qs
                        else:
                            qty = element['quantity']
                            print(qty)
                    
                
                
                    else:
                        if(tortillas['tortillas']==0):
                            print("No hay tortillas pasando a la siguiente orden")
                            continue
                        ts = tortillas['tortillas']
                        if (tortillas['tortillas'] > element['quantity']):
                            qty = element ['quantity']
                        
                        if(ts < element['quantity']):
                            
                            qty = ts
                            print("--------------ts ------------" ,ts, qty,"------------------------ ")    
                        time+=qty
                    
                    i+= qty
                    
                print("")
                print(element)
                if(element['type']=='quesadilla'):
                    quesadillas['quesadillas']-=qty
                else:
                    tortillas['tortillas']-=qty
                for ingredient in element['ingredients']:
                    Fillings[ingredient] -= qty 
                    time += qty * 0.5
                element['quantity']-=qty
                
                if(element['quantity']==0):
                    element['status'] ='closed'
                print(f"Se han preparado {qty} elementos de la orden" )
            
            
                sleep(time)
            #print(f"terminado depues de {time}")
            correspondientes = []
            for elem in ordenes:
                if(elem['status']=="open" and elem['meat'] in meats):
                    correspondientes.append(elem)
            if(len(correspondientes)>0):
                queue.put(datos)
            

def Chalan(ObservablesFills,ObservableTortilla ):
    while True:
        for fills in ObservablesFills:
            for elem in fills:
                if(fills[elem]!=maximos[elem]):
                    cantidadALLenar = maximos[elem]-fills[elem]
                    tiempo = (cantidadALLenar / maximos[elem]) * times[elem]
                    print(f"Llenando {elem}, durara {tiempo} segundos")
                    sleep(tiempo)
                    fills[elem]+=cantidadALLenar
            
        for elem in ObservableTortilla:
            if elem['tortillas'] < maximos['tortillas']:
                cantidadALLenar = maximos['tortillas']-elem['tortillas']
                tiempo = (cantidadALLenar / maximos['tortillas']) * times['tortillas']
                print(f"Llenando Tortillas, se tardara {tiempo} segundos")
                sleep(tiempo)
                elem['tortillas']+=cantidadALLenar

def Quesadillero(stocks):
    while True:
        for i in stocks:
            if(i['quesadillas']<5):
                sleep(20)
                i['quesadillas']+=1
                print("Quesadilla Preparada")
                    
                
            
        

datos = open('tacos.json','r')
datos = json.load(datos)

if __name__=="__main__":
    
    #datos = open('tacos.json','r')
    ##datos = json.load(datos)
    orden = datos[0]
    type = ["taco", "quesadilla"]
    meat = ["asada", "adobada", "suadero", "tripa", "cabeza"]
    fillings = ["cebolla", "cilantro", "salsa", "guacamole"]
    
    
    queue = SimpleQueue()
    for i in datos:
        queue.put(i)
    
    quesadillas = {"quesadillas":5}
    tortillas ={"tortillas":50}
    Fillings = {
        "cebolla":100, "cilantro":100, "salsa":100, "guacamole":100,
        
    }
    start = time()
    p = Thread(target=Taquero, args=(queue,['asada'],tortillas,quesadillas,Fillings))
    p.start()
    j = Thread(target=Chalan,args=([Fillings],[tortillas],))
    j.start()
    k = Thread (target=Quesadillero, args=([quesadillas],) )
    k.start()
    
    while(True):
        
        sleep(3)
        print(Fillings,tortillas,quesadillas)
        
        

        
        
        