async def con_get(data: list) -> list:
    end_data = []
    async with websockets.connect('ws://192.168.4.1/ws') as websocket:
        for i in data:
            await websocket.send(i)
            end_data.append(str(await websocket.recv()))
    return end_data
