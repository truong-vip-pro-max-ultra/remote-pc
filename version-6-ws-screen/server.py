from flask import Flask, Response, render_template
from io import BytesIO
from PIL import ImageGrab
import socket
import threading
from time import sleep

import asyncio
import websockets
import select

# host = '103.14.48.141'
host = 'websocket-demo.site'

data_screen = b''
data_max = 1024


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/feed')
def video_feed():
    return Response(thread_gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

async def gen_screen(websocket, path):
    global data_screen
    try:
        async for message in websocket:
            data_screen = message
    except:
        pass
def thread_gen():
    global data_screen
    while True:
        yield(data_screen)


############ mouse

server_mouse = ''
address_mouse = ''
async def handle_client(websocket, path):
    global server_mouse
    global address_mouse
    try:
        async for message in websocket:
            # print("Received:", message)
            try:
                server_mouse.sendto(message.encode('utf-8'),address_mouse)
            except:
                pass
    except:
        pass

def set_server_mouse():
    global server_mouse
    global address_mouse
    port = 6666
    server_ = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_.bind((host, port))
    while True:
        ready = select.select([server_],[],[],2)
        if ready[0]:
            message_connected ,address_ = server_.recvfrom(data_max)
            # print(message_connected)
            server_mouse = server_
            address_mouse = address_
            break
def reset_server_mouse():
    global server_mouse
    global address_mouse
    while True:
        try:
            message_connected ,address_ = server_mouse.recvfrom(data_max)
            if message_connected == b'connect-mouse':
                address_mouse = address_
        except:
            pass

###
def thread_run_host():
    app.run(host='0.0.0.0', port=80)



start_server_screen = websockets.serve(gen_screen, host, 9999)
start_server_control = websockets.serve(handle_client, host, 12345)
async def start_servers():
    await start_server_screen
    await start_server_control

if __name__ == '__main__':
    t1 = threading.Thread(target=thread_run_host)
    t1.start()

    set_server_mouse()

    t2 = threading.Thread(target=reset_server_mouse)
    t2.start()

    asyncio.get_event_loop().run_until_complete(start_servers())
    asyncio.get_event_loop().run_forever()
    
