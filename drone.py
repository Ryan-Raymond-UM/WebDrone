from websockets.asyncio.client import connect
import aiortc
import aiortc.contrib.media
from av import VideoFrame
from fractions import Fraction
import time
import asyncio
import json
import picamera2

class PiCamera(aiortc.VideoStreamTrack):
    def __init__(self):
        super().__init__()
        self.picam = picamera2.Picamera2()
        self.picam.start()
    async def recv(self):
        frame = self.picam.capture_array()[:, :, :3]
        video_frame = VideoFrame.from_ndarray(frame, format="rgb24")
        video_frame.pts = time.time_ns() // 1000
        video_frame.time_base = Fraction(1, 1_000_000)

        return video_frame

player = None
data_channel = None
peer_connection = None
websocket = None
video_track = PiCamera()

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
    print(await video_track.recv())
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
    #player = aiortc.contrib.media.MediaPlayer('udp://localhost:5555')
    #player = aiortc.contrib.media.MediaPlayer('video.mp4')
    #video_track = player.video
    #peer_connection.addTrack(video_track) # Commenting this line prevents error

    @peer_connection.on('datachannel')
    def ondatachannel(new_data_channel):
        global data_channel
        
        data_channel = new_data_channel

        @data_channel.on('message')
        def onmessage(message):
            print(f'New Message: {message}')
    
    async with connect('ws://CF-54-3-4a96b566:8765/drone') as websocket:
        while True:
            message = await websocket.recv()
            await message_handler(message)


asyncio.run(main())
