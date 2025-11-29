from websockets.asyncio.client import connect
import aiortc
import aiortc.contrib.media
import asyncio
import json

player = None
data_channel = None
peer_connection = None
websocket = None
video_track = None

async def message_handler(message):
    message = json.loads(message)
    match message['type']:
        case 'offer':
            await offer_handler(message)
        case _:
            print(message)

async def offer_handler(offer):
    global peer_connection, websocket, video_track

    peer_connection.addTrack(video_track)
    sessionDescription = aiortc.RTCSessionDescription(offer['sdp'], offer['type'])
    await peer_connection.setRemoteDescription(sessionDescription);
    answer = await peer_connection.createAnswer()
    print(answer)
    await peer_connection.setLocalDescription(answer)
    params = {'type': answer.type, 'sdp': answer.sdp}
    await websocket.send(json.dumps(params))

async def main():
    global peer_connection, websocket, video_track, player

    peer_connection = aiortc.RTCPeerConnection()
    player = aiortc.contrib.media.MediaPlayer('video.mp4')
    video_track = player.video
    #peer_connection.addTrack(video_track) # Commenting this line prevents error

    @peer_connection.on('datachannel')
    def ondatachannel(new_data_channel):
        global data_channel
        
        data_channel = new_data_channel

        @data_channel.on('message')
        def onmessage(message):
            print(f'New Message: {message}')
    
    async with connect('ws://localhost:8765/drone') as websocket:
        while True:
            message = await websocket.recv()
            await message_handler(message)


asyncio.run(main())
