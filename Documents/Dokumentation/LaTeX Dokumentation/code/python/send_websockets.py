async def con(data: list) -> None:
    async with websockets.connect('ws://192.168.4.1/ws') as websocket:
        for i in data: # Durchgang aller Textnachrichten in einer Liste
            await websocket.send(i) # Verschicken von den Textnachrichten
