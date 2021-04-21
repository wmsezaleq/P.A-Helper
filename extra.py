from tkinter import Tk, Button, Entry, Label
import tkinter.font as font
from selenium import webdriver
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import threading
import time

class mainForm:
    def accept(self):
        payload = {}
        with open("data", "r") as file:
            payload = eval(file.read())
        with open("data", "w") as file:
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
            with open("data", "r") as file:
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
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--user-agent="Mozilla/5.0 (Windows Phone 10.0; Android 4.2.1; Microsoft; Lumia 640 XL LTE) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Mobile Safari/537.36 Edge/12.10166"')
    driver = webdriver.Chrome(chrome_options=chrome_options)

    driver.get("https://www.mercadolibre.com/jms/mla/lgz/login?platform_id=ML&go=https%3A%2F%2Fwms.mercadolibre.com.ar%2F&loginType=explicit")
    sleep(5)
    while driver.current_url != "https://wms.mercadolibre.com.ar/":
        sleep(0.5)

    with open("data", "r") as file:
        data = {}
        try:
            data = eval(file.read())
        except:
            pass
    data['cookies'] = driver.get_cookies()
    with open("data", "w") as file:
        file.write(str(data))
    driver.close()


class SpreadDoc:
    client = 0
    def __init__(self):
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('server_credentials.json', scope)

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
                with open("pos","w") as file:
                    file.write(str(list(set(self.pos_inexistentes))))
            else:
                self.__checked = False
    def __init__(self):
        self.pos_volumen = self.__get_volumen([60.0, 42.0, 45.0])
        self.reset()
        with open("pos","r") as file:
            self.pos_inexistentes = eval(file.read())
        x = threading.Thread(target=self.__watchdog, daemon=True)
        x.start()
    def __del__(self):
        print("Guardando data...")
        with open("pos","w") as file:
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

    def add(self, data):
        if type(data) == str:
            data = [data, 100, 0]
        direccion = data[0][:4]
        if direccion[:2] == "RK":
            direccion = data[0][:3] + data[0][13:][:2]
        self.pos[data[0]] = [data[1], data[2]]


        if int(data[0][5:8]) != 26 or int(data[0][5:8]) != 27:
            if direccion in self.totalpos_disponibles and ((data[2] < 4 and direccion[:2] == "MZ") or (data[2] == 0 and direccion[:2] == "RK")):
                self.totalpos_disponibles[direccion] += 1
            elif ((data[2] < 4 and direccion[:2] == "MZ") or (data[2] == 0 and direccion[:2] == "RK")):
                self.totalpos_disponibles[direccion] = 1
            elif direccion in self.totalpos_ocupadas:
                self.totalpos_ocupadas[direccion] += 1
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
            direccion = dire[:4]
            data = self.pos[dire]
            if dire[:2] == "RK":
                direccion = dire[:3] + dire[13:][:2]
            if int(dire[5:8]) != 26 or int(dire[5:8]) != 27:
                if direccion in self.totalpos_disponibles and ((data[1] < 4 and direccion[:2] == "MZ") or (data[1] == 0 and direccion[:2] == "RK")):
                    self.totalpos_disponibles[direccion] += 1
                elif ((data[1] < 4 and direccion[:2] == "MZ") or (data[1] == 0 and direccion[:2] == "RK")):
                    self.totalpos_disponibles[direccion] = 1
                elif direccion in self.totalpos_ocupadas:
                    self.totalpos_ocupadas[direccion] += 1
                else:
                    self.totalpos_ocupadas[direccion] = 1
    def get_free_percentage(self, obj_volumen):
        pos_volumen = self.pos_volumen
        pos_volumen -= obj_volumen
        return round((pos_volumen * 100) / self.pos_volumen,2)

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