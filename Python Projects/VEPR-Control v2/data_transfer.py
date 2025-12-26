import websockets

allow_send = False

async def con(data: list) -> None:
    if not allow_send:
        return
    async with websockets.connect("ws://192.168.4.1/ws") as websocket:
        for i in data:
            await websocket.send(i)

async def con_get(data: list) -> list:
    if not allow_send:
        return []
    end_data = []
    async with websockets.connect("ws://192.168.4.1/ws") as websocket:
        for i in data:
            await websocket.send(i)
            end_data.append(str(await websocket.recv()))
    return end_data