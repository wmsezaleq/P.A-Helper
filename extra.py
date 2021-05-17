from tkinter import Tk, Button, Entry, Label
import tkinter.font as font
from selenium import webdriver
import gspread
from UserManager import User_Manager
from oauth2client.service_account import ServiceAccountCredentials
import threading
import time
import requests

class mainForm:
    def accept(self):
        payload = {}
        with open("data/data", "r") as file:
            payload = eval(file.read())
        with open("data/data", "w") as file:
            payload["ip"] = self.ip.get()
            payload["port"] = self.port.get()
            file.write(str(payload))

        self.form.destroy()
        self.form.quit()

    def __init__(self):
        w = 600
        h = 250
        # Seteo objetos
        self.form = Tk()
        labelip = Label(self.form, text = "IP: ")
        labelport = Label(self.form, text = "Puerto: ")
        self.ip = Entry(self.form)
        self.port = Entry(self.form)
        accept_button = Button(self.form, command = self.accept, text = "Aceptar y continuar")
        myFont = font.Font(size=30)
        
        # Posicionamiento en el grid
        labelip.grid(row=0, column=0, padx=10)
        self.ip.grid(row=0, column=1)
        
        labelport.grid(row=1, column=0, padx = 10)
        self.port.grid(row=1, column=1)

        accept_button.grid(row=2, column=0, columnspan=2, pady=10)

        # Configuracion
        self.form.title("Configuracion server")
        def avoid():
            pass
        self.form.protocol("WM_DELETE_WINDOW", avoid)
        accept_button.config(width="20")
        accept_button['font'] = myFont
        labelport['font'] = myFont
        labelip['font'] = myFont
        self.ip['font'] = myFont
        self.port['font'] = myFont
        try:
            with open("data/data", "r") as file:
                data = eval(file.read())
                self.ip.insert(0, data['ip'])
                self.port.insert(0, data['port'])
        except:
            self.ip.insert(0, "0.0.0.0")
            self.port.insert(0, "5000")
        
        
        ws = self.form.winfo_screenwidth()
        hs = self.form.winfo_screenheight()
        x = (ws / 2) - (w / 2)
        y = (hs / 2) - (h / 2)
        self.form.geometry('%dx%d+%d+%d' % (w, h, x, y))

    def start(self):
        self.form.mainloop()

from time import sleep
def buscador():
    Acc = User_Manager()
    Acc.login()
    with open("data/data", "r") as file:
        data = {}
        try:
            data = eval(file.read())
        except:
            pass
    data['cookies'] = requests.utils.dict_from_cookiejar(Acc.jar)
    with open("data/data", "w") as file:
        file.write(str(data))


class SpreadDoc:
    client = 0
    def __init__(self):
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('data/server_credentials.json', scope)

        self.spreadsheet = gspread.authorize(creds).open('QR & ERROR POS.')
    def append_MELI(self, data):
        if type(data[0]) == str:
            self.spreadsheet.values_append(
                "MELI sin cubing",
                params={'valueInputOption': 'RAW',
                "insertDataOption" : "INSERT_ROWS"}, 
                body={'values': [data]}
            )
        else:
            self.spreadsheet.values_append(
                "MELI sin cubing",
                params={'valueInputOption': 'RAW',
                "insertDataOption" : "INSERT_ROWS"}, 
                body={'values': data}
            )
        self.spreadsheet.values_append(
            "MELI sin cubing!F1",
            params={'valueInputOption': 'USER_ENTERED'}, 
            body={'values':[["=UNIQUE(A:A)"]]}
        )
        
        info = self.spreadsheet.worksheet('MELI sin cubing').get("F:F")
        self.spreadsheet.values_clear("MELI sin cubing!A:A")
        self.spreadsheet.values_append(
            "MELI sin cubing!A1",
            params={'valueInputOption': 'RAW'}, 
            body={'values': info}
        )
        self.spreadsheet.values_clear("MELI sin cubing!F:F")
    def append_qr(self, data):
        if len(data) == 1:
            self.spreadsheet.values_append(
                "Reportes QR",
                params={'valueInputOption': 'RAW',
                "insertDataOption" : "INSERT_ROWS"}, 
                body={'values': [data]}
            )
        else:
            self.spreadsheet.values_append(
                "Reportes QR",
                params={'valueInputOption': 'RAW',
                "insertDataOption" : "INSERT_ROWS"}, 
                body={'values': data}
            )
        self.spreadsheet.values_append(
            "Reportes QR!F1",
            params={'valueInputOption': 'USER_ENTERED'}, 
            body={'values':[["=UNIQUE(A:B)"]]}
        )
        
        info = self.spreadsheet.worksheet('Reportes QR').get("F:G")
        self.spreadsheet.values_clear("Reportes QR!A:B")
        self.spreadsheet.values_append(
            "Reportes QR!A1",
            params={'valueInputOption': 'RAW'}, 
            body={'values': info}
        )
        self.spreadsheet.values_clear("Reportes QR!F:G")


    def append_err(self, data):
        if type(data[0]) == str:
            self.spreadsheet.values_append(
                "Reportes errores",
                params={'valueInputOption': 'RAW',
                "insertDataOption" : "INSERT_ S"}, 
                body={'values': [data]}
            )
        else:
            self.spreadsheet.values_append(
                "Reportes errores",
                params={'valueInputOption': 'RAW',
                "insertDataOption" : "INSERT_ROWS"}, 
                body={'values': data}
            )
        self.spreadsheet.values_append(
            "Reportes errores!F1",
            params={'valueInputOption': 'USER_ENTERED'}, 
            body={'values':[["=UNIQUE(A:B)"]]}
        )
        
        info = self.spreadsheet.worksheet('Reportes errores').get("F:G")
        self.spreadsheet.values_clear("Reportes errores!A:B")
        self.spreadsheet.values_append(
            "Reportes errores!A1",
            params={'valueInputOption': 'RAW'}, 
            body={'values': info}
        )
        self.spreadsheet.values_clear("Reportes errores!F:G")

from datetime import datetime

class MELI:
    sz = []
    cant = 0
    code = ""
class metrica:
    pos = {}
    totalpos_disponibles = {}
    totalpos_ocupadas = {}
    reporte_error = []
    reporte_qr = []
    reporte_meli = []
    pos_inexistentes = []
    __checked = False

    def __watchdog(self):
        while True:
            time.sleep(5)
            if not self.__checked and self.pos_inexistentes:
                with open("data/pos","w") as file:
                    file.write(str(list(set(self.pos_inexistentes))))
            else:
                self.__checked = False
    def __init__(self):
        self.posMZ_volumen = self.__get_volumen([60.0, 42.0, 45.0])
        self.posRS_volumen = self.__get_volumen([60.0, 42.0*5, 45.0])

        self.reset()
        with open("data/pos","r") as file:
            self.pos_inexistentes = eval(file.read())
        x = threading.Thread(target=self.__watchdog, daemon=True)
        x.start()
    def __del__(self):
        print("Guardando data...")
        with open("data/pos","w") as file:
            file.write(str(list(set(self.pos_inexistentes))))
    def add_pos(self, pos):
        self.pos_inexistentes.append(pos)
        self.__checked = True

    def add_error(self, pos):
        now = datetime.now()
        self.reporte_error.append([pos, now.strftime("%d/%m/%Y %H:%M")])

    def add_qr(self, pos):
        now = datetime.now()
        self.reporte_qr.append([pos, now.strftime("%d/%m/%Y %H:%M")])

    def add_meli(self, pos):
        self.reporte_meli.append([pos])

    # Funcion para añadir las posiciones a la metrica y sumar a las posiciones disponibles/ocupadas
    def add(self, data):
        # Si la data es igual a una string (posicion de RK)
        if type(data) == str:
            # Se toma como el espacio vacio
            data = [data, 100, 0]
        direccion = None
        # Si la direccion es de MZ o RS y las calles son de 28 para arriba (nuevo Mezzanine)
        if (data[0][:2] == "MZ" or data[0][:2] == "RS") and int(data[0][5:8]) > 27:
            # se declara la key como MZ2-piso
            direccion = "MZ2-" + data[0][3]
        else:
            direccion = data[0][:4]
        # En caso de que sea RK, se declara la key como RK-nivel
        if direccion[:2] == "RK":
            direccion = data[0][:3] + data[0][13:][:2]
        # El diccionario en la key posicion recibida es igual a un array [volumen, cant.melis]
        self.pos[data[0]] = [data[1], data[2]]

        # Si las calles son distintas de 26 o 27 (NIP no cuentan para la cant. de lugar disponible)
        if int(data[0][5:8]) != 26 or int(data[0][5:8]) != 27:
            # Si la key (Sector-piso) esta en el diccionario y MZ o RS tienen menor a 4 melis o RK tiene 0 melis...
            if direccion in self.totalpos_disponibles and ((direccion[:2] == "MZ" or direccion[:2] == "RS") and data[2] < 4 or (data[2] == 0 and direccion[:2] == "RK")):
                # Se suma el valor que ya este en con 1
                self.totalpos_disponibles[direccion] += 1
            # Si la key (sector-psio) no esta en el diccionario y se cumple la misma condicion
            elif ((data[2] < 4 and (direccion[:2] == "MZ" or direccion[:2] == "RS")) or (data[2] == 0 and direccion[:2] == "RK")):
                # Se declara la key y el numero 1 (inicio)
                self.totalpos_disponibles[direccion] = 1
            # Sino, si existe la direccion en el diccionario ocupado
            elif direccion in self.totalpos_ocupadas:
                self.totalpos_ocupadas[direccion] += 1
            # Si no exist en el diccionario, crea la nueva key y le asigna valor 1
            else:
                self.totalpos_ocupadas[direccion] = 1

    def get_disponible(self, piso):
        if piso in self.totalpos_disponibles:
            return self.totalpos_disponibles[piso]
        else:
            return 0
    def get_ocupada(self, piso):
        if piso in self.totalpos_ocupadas:
            return self.totalpos_ocupadas[piso]
        else:
            return 0
    def reset(self):
        self.pos.clear()
        self.totalpos_ocupadas.clear()
        self.totalpos_disponibles.clear()
    def __get_volumen(self, sz):
        i = 1
        for s in sz:
            i *= s
        return i
    def update(self):
        for dire in self.pos:
            data = self.pos[dire]
            direccion = None
            if (dire[:2] == "MZ" or dire[:2] == "RS") and int(dire[5:8]) > 27:
                # se declara la key como MZ2-piso
                direccion = "MZ2-" + dire[3]
            else:
                direccion = dire[:4]
            if dire[:2] == "RK":
                direccion = dire[:3] + dire[13:][:2]
            # Si las calles son distintas de 26 o 27 (NIP no cuentan para la cant. de lugar disponible)
            if int(dire[5:8]) != 26 or int(dire[5:8]) != 27:
                # Si la key (Sector-piso) esta en el diccionario y MZ o RS tienen menor a 4 melis o RK tiene 0 melis...
                if direccion in self.totalpos_disponibles and ((direccion[:2] == "MZ" or direccion[:2] == "RS") and data[1] < 4 or (data[1] == 0 and direccion[:2] == "RK")):
                    # Se suma el valor que ya este en con 1
                    self.totalpos_disponibles[direccion] += 1
                # Si la key (sector-psio) no esta en el diccionario y se cumple la misma condicion
                elif ((data[1] < 4 and (direccion[:2] == "MZ" or direccion[:2] == "RS")) or (data[1] == 0 and direccion[:2] == "RK")):
                    # Se declara la key y el numero 1 (inicio)
                    self.totalpos_disponibles[direccion] = 1
                # Sino, si existe la direccion en el diccionario ocupado
                elif direccion in self.totalpos_ocupadas:
                    self.totalpos_ocupadas[direccion] += 1
                # Si no exist en el diccionario, crea la nueva key y le asigna valor 1
                else:
                    self.totalpos_ocupadas[direccion] = 1
    def get_free_percentage(self, obj_volumen, sector):
        pos_volumen = None
        if sector == "RS":
            pos_volumen = self.posRS_volumen
        else:
            pos_volumen = self.posMZ_volumen
        resta = pos_volumen - obj_volumen
        return round((resta * 100) / pos_volumen,2)

def string_zero(num):
    data = ""
    if num < 10:
        data = "00" + str(num)
    elif num < 100:
        data = "0" + str(num)
    else:
        data = str(num)
    return data
if __name__ == '__main__':
    m = metrica()
    m.add_pos("MZ-0-001-002-01-01")
    del m