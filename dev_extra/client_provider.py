import socketio
import requests
from tkinter import Tk
from UserManager import User_Manager
user = User_Manager()
class client:
    global sio
    sio = socketio.Client()
    def __init__(self, ip, port):
        sio.connect(f"http://{ip}:{port}")
    
    @staticmethod
    @sio.event
    def connect():
        print("Conectado al servidor!")
        sio.emit('Server-M', True)

    @staticmethod
    @sio.event
    def disconnect():
        sio.emit('Server-M', False)

    @sio.on('Client-Request')
    def get_data(url):
        r = requests.get(url, cookies=user.jar).text
        sio.emit('Server-Data', [url, r])

if __name__ == "__main__":
    c1 = client("181.47.52.5", 8080)
    