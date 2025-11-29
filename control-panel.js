var ws_connection = null;
var rtc_connection = null;
var data_channel = null;

function websocket_message_handler(event) {
    const message = JSON.parse(event.data);
    console.log(message);
    switch (message.type) {
        case 'answer':
            rtc_connection.setRemoteDescription(message);
            break;
    }
}

function connect_websocket() {
    console.log('Establishing websocket connection');
    ws_connection = new WebSocket('ws://localhost:8765/control');
    ws_connection.onmessage = websocket_message_handler;
    ws_connection.onopen = connect_webrtc;
}

function handle_ice_candidate(event) {
    console.log(event.candidate);
    if (rtc_connection.iceGatheringState == 'complete') {
        console.log(rtc_connection.localDescription);
        ws_connection.send(JSON.stringify(rtc_connection.localDescription));
    }
}

function track_handler(event) {
    const track = event.streams[0];
    document.querySelector('video').srcObject = track;
}

async function connect_webrtc() {
    console.log('Creating WebRTC Peer Connection');
    const config = {iceServers: [{urls: 'stun:stun.l.google.com:19302'}]};
    rtc_connection = new RTCPeerConnection(config);
    rtc_connection.onicecandidate = handle_ice_candidate;
    rtc_connection.ondatachannel = console.log;
    rtc_connection.ontrack = track_handler;
    rtc_connection.onconnectionstatechange = console.log;
    rtc_connection.addTransceiver('video', { direction: 'recvonly' });
    data_channel = rtc_connection.createDataChannel('data');
    const offer = await rtc_connection.createOffer();
    await rtc_connection.setLocalDescription(offer);
}

async function main(event) {
    console.log('Starting main function');
    connect_websocket();
}

window.onload = main;
