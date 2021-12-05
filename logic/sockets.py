import asyncio
import websockets
import json

async def hello(websocket, path):
    name = await websocket.recv()

    if name == 'send':
        print('Should send order here')
        await websocket.send(json.dumps({"evt": "algo", "payload": {"hello": "world"}}))
        return

# Mandar trigger de events con
# websocket.send(json.dumps(dict))
# donde dict 
# { type: "evtname", payload: {}}
#
#

def server():
    start_server = websockets.serve(hello, "localhost", 8765)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()