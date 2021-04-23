from flask import Flask, render_template, request
from flask_socketio import SocketIO
from engineio.async_drivers import gevent
import os
os.environ["GEVENT_SUPPORT"] = 'True'

flask_app = Flask(__name__)
io = SocketIO(flask_app) # Aplicacion general
@flask_app.route('/')
def main_root():
    return render_template("MLSearcher.html")

@flask_app.route('/TL')
def TL_root():
    return render_template("TL.html")

@io.on('pedir')
def func(msg):
    


class Server:
    def __init__(self, data):
        self.jar = data[0] # CookieJar para los requests con WMS
        self.IP = data[1]
        self.PORT = data[2]

    def start(self):
        io.run(flask_app, host=self.IP, port=self.PORT)

if __name__ == "__main__":
    server = Server()
    server.start()