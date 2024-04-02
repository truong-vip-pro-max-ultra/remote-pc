from flask import Flask, Response, render_template,request
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

# data_screen = b''

data_screen = {}

data_max = 1024


list_client_screen = {}


app = Flask(__name__)

@app.route('/')
def index():
    ip = request.args.get('ip')
    if ip != None:
        return render_template('multi.html',ip = ip)
    else:
        return ''

@app.route('/feed')
def video_feed():
    ip = request.args.get('ip')
    if ip!=None:
        return Response(thread_gen(ip), mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        return ''

async def gen_screen(websocket, path):
    global data_screen
    address_string = websocket.remote_address[0]+':'+str(websocket.remote_address[1])
    print(address_string)
    try:
        async for message in websocket:
            data_screen[address_string] = message
    except:
        pass
def thread_gen(address_string):
    global data_screen
    while True:
        try:
            yield(data_screen[address_string])
        except:
            break


############ mouse

server_mouse = {}
address_mouse = {}
async def handle_client(websocket, path):
    global server_mouse
    global address_mouse
    try:
        async for message in websocket:
            # print("Received:", message)
            try:
                address_string , message_ = message.split('|||||')
                server_mouse.sendto(message_.encode('utf-8'),address_mouse[address_string])
            except Exception as e:
                print(e)
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
            address_string = address_[0]+':'+str(address_[1])
            print(address_string)
            server_mouse = server_
            address_mouse[address_string] = address_
            break
def reset_server_mouse():
    global server_mouse
    global address_mouse
    while True:
        try:
            message_connected ,address_ = server_mouse.recvfrom(data_max)
            if message_connected == b'connect-mouse':
                print(address_)
                address_string = address_[0]+':'+str(address_[1])
                address_mouse[address_string] = address_
        except Exception as e:
            print(e)
            pass

###
def thread_run_host():
    app.run(host='0.0.0.0', port=99)



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
    
