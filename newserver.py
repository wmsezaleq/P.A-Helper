from flask import Flask, render_template, request
from flask_socketio import SocketIO
from engineio.async_drivers import gevent
from threading import Thread
import webbrowser
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
    cliente = request.sid
    x = Thread(Server.)


class Server:
    def __init__(self, data):
        self.jar = data[0] # CookieJar para los requests con WMS
        self.IP = data[1]
        self.PORT = data[2]

    @staticmethod
    def buscarLugar(sector, piso, calle, *cliente):
        cliente = "___" # Cliente dummy
        # Si la busqueda de lugar proviene de un cliente...
        if args:
            cliente = cliente[0] # Se declara al cliente

        
    def start(self):
        IP = ""
        if self.IP == "0.0.0.0":
            IP = socket.gethostbyname(socket.gethostname())
        else:
            IP = self.IP
        webbrowser.get().open(f"http://{IP}:{self.PORT}/")
        webbrowser.get().open(f"http://{IP}:{self.PORT}/TL")
        io.run(flask_app, host=self.IP, port=self.PORT)

if __name__ == "__main__":
    server = Server()
    server.start()