import socket
from io import BytesIO
from PIL import ImageGrab
# from time import sleep

import websockets
import win32api
import threading
import asyncio
import json
import pyautogui as pya

import select
import os

# host = '103.14.48.141'
host = 'websocket-demo.site'
data_max = 1024

def screen():
    img_buffer = BytesIO()
    ImageGrab.grab().save(img_buffer, 'JPEG', quality=20)
    img_buffer.seek(0)
    data = b'--frame\r\n'+b'Content-Type: image/jpg\r\n\r\n' + img_buffer.read() + b'\r\n\r\n'
    return data

async def send_screen():
    while True:
        try:
            async with websockets.connect('ws://'+host+':9999') as websocket:
                while True:
                    try:
                        await websocket.send(screen())
                    except:
                        break
        except:
            pass

def recv_mouse():
    port = 6666
    client_ = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_.sendto(b'connect-mouse',(host,port))
    while True:
        try:
            ready = select.select([client_],[],[],2)
            if ready[0]:
                mouse,address = client_.recvfrom(data_max)
                # print(mouse)
                mouse = json.loads(mouse.decode('utf-8'))
                mouse_type = mouse['type']
                if mouse_type == 'move':
                    x,y = int(mouse['x'])-1, int(mouse['y'])-1
                    win32api.SetCursorPos((x,y))
                elif mouse_type == 'click':
                    x,y = int(mouse['x'])-1, int(mouse['y'])-1
                    pya.click(x,y)
                elif mouse_type == 'right-click':
                    pya.rightClick()
                elif mouse_type == 'scroll':
                    scroll_direction = mouse['scrollDirection']
                    if scroll_direction == 'up':
                        pya.scroll(100)
                    else:
                        pya.scroll(-100)
                elif mouse_type == 'scroll-mobile':
                    scroll_direction = mouse['scrollDirection']
                    if scroll_direction == 'up':
                        pya.scroll(400)
                    else:
                        pya.scroll(-400)
                elif mouse_type == 'press':
                    pya.mouseDown()
                elif mouse_type == 'release':
                    pya.mouseUp()
                ##### keydown
                elif mouse_type == 'keydown':
                    key = mouse['key'].lower()
                    if key == 'control':
                        key = 'ctrl'
                    if key == 'meta':
                        key = 'win'
                    if 'right' in key:
                        key = 'right'
                    if 'left' in key:
                        key = 'left'
                    if 'up' in key:
                        key = 'up'
                    if 'down' in key:
                        key = 'down'
                    pya.press(key)

                elif mouse_type == 'multi-keydown':
                    key1 = mouse['key1'].lower()
                    key2 = mouse['key2'].lower()
                    if key1 == 'control':
                        key1 = 'ctrl'
                    if key2 == 'control':
                        key2 = 'ctrl'
                    if key1 == 'meta':
                        key1 = 'win'
                    if key2 == 'meta':
                        key2 = 'win'
                    if 'right' in key1:
                        key1 = 'right'
                    if 'right' in key2:
                        key2 = 'right'
                    if 'left' in key1:
                        key1 = 'left'
                    if 'left' in key2:
                        key2 = 'left'
                    if 'up' in key1:
                        key1 = 'up'
                    if 'up' in key2:
                        key2 = 'up'
                    if 'down' in key1:
                        key1 = 'down'
                    if 'down' in key2:
                        key2 = 'down'
                    if key1 in ['ctrl','win','alt','shift']:
                        pya.hotkey(key1,key2)
                    else:
                        pya.press(key2)
                elif mouse_type == 'cmd':
                    cmd = mouse['cmd']
                    os.system(cmd)
            else:
                client_.sendto(b'no-connect-mouse',(host,port))
        except:
            # print("except")
            pass

t1 = threading.Thread(target=recv_mouse)
t1.start()
asyncio.get_event_loop().run_until_complete(send_screen())