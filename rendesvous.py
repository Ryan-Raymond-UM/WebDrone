from websockets.sync.server import serve

websockets = {'control': None, 'drone': None}
peers = {'control': 'drone', 'drone': 'control'}

def handler(websocket):
    name = websocket.request.path[1:]
    print(f'New Websockets connection, name: {name}')
    if name not in websockets.keys():
        print(f'Ignoring because {name} is not a valid name')
        return
    if websockets[name]:
        print(f'Closing old connection for {name} and replacing with new one')
        websockets[name].close()
    websockets[name] = websocket
    for message in websocket:
        print(f'New Message: "{message}"')
        if websockets[peers[name]]:
            print(f'Relaying message to {peers[name]}')
            websockets[peers[name]].send(message)
        else:
            print(f'Ignoring message because {peers[name]} is not connected')

with serve(handler, '0.0.0.0', 8765) as server:
    server.serve_forever()
