from flask import Flask, render_template, request
from flask_socketio import SocketIO
from bs4 import BeautifulSoup, SoupStrainer
from engineio.async_drivers import gevent
import socket
from io import StringIO
from extra import mainForm, buscador, SpreadDoc, metrica
import webbrowser
import threading
import time
import requests
import csv
from random import random, randint
from datetime import datetime
import traceback
app = Flask(__name__)
socketio = SocketIO(app)
cookies = {}
hilos = {}
cache = {}
cliente_esperando = {}
cliente_actuales = {}
cliente_TL = []
pos_inexistente = []

jar = requests.cookies.RequestsCookieJar()


Metrica = metrica()
doc = SpreadDoc()
import os
os.environ["GEVENT_SUPPORT"] = 'True'
total_tiempo = 0
MESSAGE_TL = ""

def contador(sector):
    for i in range(10 * 60):
        if sector in cliente_esperando:
            for cliente in cliente_esperando[sector]:
                socketio.emit('contador', 'Actualizado hace {} minutos, proxima actualizacion en {}'.format(int(i/60), 10-int(i/60)), room=cliente)
        time.sleep(1)
    if sector in cliente_esperando:
        for cliente in cliente_esperando[sector]:
            socketio.emit('contador', 'Presione buscar para volver a actualizar', room=cliente)

def string_zero(num):
    data = ""
    if num < 10:
        data = "00" + str(num)
    elif num < 100:
        data = "0" + str(num)
    else:
        data = str(num)
    return data
def scrapMELI(dire):
    row = ""
    try:
        req_text = requests.get("https://wms.mercadolibre.com.ar/api/reports/skus/export/INVENTORIES?inventory_id={}&fields=inventory_id%2Cwidth_value%2Clength_value%2Cheight_value".format(dire), cookies=jar).text
        file_data = StringIO(req_text)
        data = csv.reader(file_data, delimiter=',')
        volumen = 0

        for row in data:
            if len(row) == 0:
                return scrapMELI(dire)
            if row[1] == "Ancho":
                continue

            volumen = float(row[1]) * float(row[2]) * float(row[3])
            return volumen            
        if volumen == 0:
            return scrapMELI(dire)
    except Exception as e:
        if len(row) != 4:
            return scrapMELI(dire)
        Metrica.add_meli(dire)
    return 0
def scraper(start_dir, end_dir):
    data_total = {}
    sector = start_dir[:8]
    def worker(row):
        try:
            if row[0][:4] in ("NA-9", "NI-9"):
                row[0] = "RK-0" + row[0][4:]
            elif row[0][:2] == "HV" or row[0][:2] == "NA" or row[0][:2] == "NI" or row[0][:2] == "DI" or row[0][:2] == "DM":
                row[0] = "MZ" + row[0][2:]
            if row[0] in data_total:
                data_total[row[0]][0] += 1
                if row[0][:2] == "MZ":
                    data_total[row[0]][1] += (scrapMELI(row[1]) * int(row[2]))
                else:
                    data_total[row[0]][1] += 1
            else:
                if row[0][:2] == "MZ":
                    data_total[row[0]] = [1, scrapMELI(row[1]) * int(row[2])]
                else:
                    data_total[row[0]] = [1, 0]

        except Exception as e:
            # print("{}: {}".format(row[4], e.args[0]))
            if row[0] in data_total:
                    data_total[row[0]][0] += 1
            else:
                data_total[row[0]] = [1, 0]
    print("Buscando desde {} ---> {}".format(start_dir, end_dir))
    file_data = StringIO(requests.get("https://wms.mercadolibre.com.ar/api/reports/address/export/SKUS/{}/{}?fields=address_id%2Cinventory_id%2Ctotal".format(start_dir, end_dir), cookies=jar).text)
    totalidad = csv.reader(file_data, delimiter=',')
    old_pos = ""
    actual_pos = ""
    threads = []
    mini_workers = {}
    def miniworker(threads, direccion):
        t = threads
        for x in t:
            x.start()
            x.join()
        try:
            if direccion[:4] in ("NA-9", "NI-9"):
                direccion = "RK-0" + direccion[4:]
            elif direccion[:2] == "HV" or direccion[:2] == "NA" or direccion[:2] == "NI" or direccion[:2] == "DI" or direccion[:2] == "DM":
                direccion = "MZ" + direccion[2:]
            

            cantidad = data_total[direccion][0]
            volumen = data_total[direccion][1]
            Metrica.add([direccion, Metrica.get_free_percentage(volumen), cantidad])
            d =  Metrica.pos[direccion]
            if (cantidad != -1 and cantidad < 4 and direccion[:2] == "MZ") or (cantidad == 0 and direccion[:2] == "RK"):
                if sector in cliente_actuales:
                    socketio.emit('data', [direccion,d[1], d[0]], room=cliente_actuales[sector])
                if sector in cliente_esperando:
                    for waitingclient in cliente_esperando[sector]: 
                        socketio.emit('data', [direccion,d[1], d[0]], room=waitingclient)

                if sector not in cache:
                    cache[sector] = []

                cache[sector].append((direccion,d[1], d[0]))
            def foo(sector, posiciones):
                total = {}
                for pos in posiciones:
                    total[pos] = 0
                for pos in posiciones:
                    num = Metrica.get_disponible(pos)
                    total[pos] += num
                    sector[0][pos] = num
                sector.append(total)
                # Obtengo las posiciones ocupadas por piso [MZ]
                sector.append({})
                for pos in posiciones:
                    total[pos] = 0
                for pos in posiciones:
                    num = Metrica.get_ocupada(pos)
                    total[pos] += num
                    sector[2][pos] = num
                sector.append(total)
                
            MZ = [{}]
            RK = [{}]
            foo(MZ, ("MZ-0", "MZ-1", "MZ-2", "MZ-3"))
            foo(RK, ("RK-02","RK-03","RK-04","RK-05","RK-06"))

            for waitingclient in cliente_TL:
                socketio.emit("TL-message", MESSAGE_TL, room=waitingclient)
                socketio.emit('TL-update', [direccion, d[0], d[1], MZ, RK], room=waitingclient)
        except Exception as e:
            # print("miniworker {}: {}".format(direccion, e.args[0]))
            print("POSIBLE ERROR DE CONEXION... REINICIE EL SERVIDOR.")
    for row in totalidad:
        if row == []:
            scraper(start_dir, end_dir)
            return
        try:
            if row[0] == "Address":
                continue    
            actual_pos = row[0]
            if actual_pos[:2] == "RK" and actual_pos[13:][:2] == "01":
                continue
            if old_pos == "":
                old_pos = actual_pos
            elif old_pos != actual_pos:
                i = threading.Thread(target=miniworker, args=(tuple(threads), old_pos), daemon=True)
                mini_workers[old_pos] = i
                mini_workers[old_pos].start()
                threads = []
                old_pos = actual_pos
            x = threading.Thread(target=worker, args=(row,), daemon=True)
            threads.append(x)

        except:
            pass
            # print("ROW: {}".format(row))
    if threads:
        i = threading.Thread(target=miniworker, args=(tuple(threads), old_pos), daemon=True)
        mini_workers[old_pos] = i
        mini_workers[old_pos].start()
    for key in mini_workers:
        mini_workers[key].join()
    def doit(direccion):
        totalidad = ""
        piso = int(direccion[3])
        calle = int(direccion[5:][:3])
        modulo = int(direccion[9:][:3])
        
        
        if (direccion[:2] == "MZ") and (direccion in Metrica.pos_inexistentes or  direccion[9:] == "033-03-05" or direccion[9:] == "047-03-05" or \
            (
                calle == 1 and (modulo % 2 == 1 or modulo == 22 or modulo == 24)
            ) or \
            (
                calle == 2 and (modulo == 1 or modulo == 3 or modulo == 21 or modulo == 23)
            ) or \
            (
                calle == 4 and (modulo > 58 and modulo % 2 == 1)
            ) or \
            (
                calle == 5 and (modulo == 83 or modulo == 85)
            ) or \
            (
                #Calle con escalera 
                (calle == 8 or calle == 17 or calle == 26) and (modulo == 2 or modulo == 4 or modulo == 20 or modulo == 22 or modulo == 24 or modulo == 58 or modulo == 60 or modulo == 62 or modulo == 84 or modulo == 86)
            ) or \
            (
                #Calle con escalera 
                (calle == 9 or calle == 18 or calle == 27) and (modulo == 1 or modulo == 3 or modulo == 21 or modulo == 23 or modulo == 57 or modulo == 59 or modulo == 61  or modulo == 83 or modulo == 85)
            ) or \
            (
                (calle == 18) and (modulo == 19 or modulo == 35)
            ) or \
            (
                (calle == 9) and (modulo == 19 or modulo == 35 or modulo == 73)
            ) or \
            (
                (calle == 8) and (modulo == 74)
            ) or \
            (
                (calle == 26) and (modulo == 20 or modulo == 74)
            ) or \
            (
                (piso == 1) and (modulo == 36 or modulo == 74)
            ) or\
            ( 
                (piso >= 1) and \
                    (
                        calle == 5 and (modulo == 20 or modulo == 22 or modulo == 62 or modulo == 64)
                    ) or \
                    (
                        calle == 6 and (modulo == 19 or modulo == 21 or modulo == 61 or modulo == 63 )
                    ) or \
                    (
                        calle == 12 and (modulo == 20 or modulo == 22)
                    ) or \
                    (
                        calle == 13 and (modulo == 19 or modulo == 21 or modulo == 62 or modulo == 64)
                    ) or \
                    (
                        calle == 14 and (modulo == 61 or modulo == 63)
                    ) or \
                    (
                        calle == 17 and (modulo == 73)
                    ) or \
                    (
                        calle == 21 and (modulo == 22 or modulo == 20 or modulo == 62 or modulo == 64)
                    ) or \
                    (
                        calle == 22 and (modulo == 21 or modulo == 19 or modulo == 61 or modulo == 63)
                    )
            ) or \
            (
                piso == 2 and (modulo <= 8)
            )
        ):
            totalidad = []
        elif (direccion[:2] == "RK" and (direccion in Metrica.pos_inexistentes)):
            totalidad = []
        else:
            file_data = StringIO(requests.get("https://wms.mercadolibre.com.ar/api/reports/address/export/SKUS/{}/{}?fields=address_id".format(direccion, direccion), cookies=jar).text)
            totalidad = csv.reader(file_data, delimiter=',')
        for row in totalidad:
            try:
                if row[0] == "Address":
                    _direccion = direccion
                    if direccion[:4] in ("NA-9","NI-9"):
                        direccion = "RK-0" + direccion[4:]
                    elif direccion[:2] in ("NA", "NI"):
                        direccion = "MZ" + direccion[2:]
                    data_total[direccion] = [0, 0]
                    cantidad = data_total[direccion][0]
                    volumen = data_total[direccion][1]
                    Metrica.add([direccion, Metrica.get_free_percentage(volumen), cantidad])
                    d =  Metrica.pos[direccion]
                    if cantidad != -1 and cantidad < 4:
                        if sector in cliente_actuales:
                            if _direccion[:4] in ("NA-9","NI-9"):
                                socketio.emit('data', [_direccion,d[1], d[0]], room=cliente_actuales[sector])
                            else:
                                socketio.emit('data', [direccion,d[1], d[0]], room=cliente_actuales[sector])

                        if sector in cliente_esperando:
                            for waitingclient in cliente_esperando[sector]: 
                                if _direccion[:4] in ("NA-9","NI-9"):
                                    socketio.emit('data', [_direccion,d[1], d[0]], room=waitingclient)
                                else:
                                    socketio.emit('data', [direccion,d[1], d[0]], room=waitingclient)

                        if sector not in cache:
                            cache[sector] = []  

                        cache[sector].append((direccion,d[1], d[0]))
                    def foo(sector, posiciones):
                        total = {}
                        for pos in posiciones:
                            total[pos] = 0
                        for pos in posiciones:
                            num = Metrica.get_disponible(pos)
                            total[pos] += num
                            sector[0][pos] = num
                        sector.append(total)
                        # Obtengo las posiciones ocupadas por piso [MZ]
                        sector.append({})
                        for pos in posiciones:
                            total[pos] = 0
                        for pos in posiciones:
                            num = Metrica.get_ocupada(pos)
                            total[pos] += num
                            sector[2][pos] = num
                        sector.append(total)
                    MZ = [{}]
                    RK = [{}]
                    foo(MZ, ("MZ-0", "MZ-1", "MZ-2", "MZ-3"))
                    foo(RK,("RK-02","RK-03","RK-04","RK-05","RK-06"))

                    for waitingclient in cliente_TL:
                        socketio.emit("TL-message", MESSAGE_TL, room=waitingclient)
                        socketio.emit('TL-update', [direccion, d[0], d[1], MZ, RK], room=waitingclient)
                else:
                    if direccion[:8] != "RK-0-017":
                        Metrica.add_pos(direccion)
            except Exception as e:
                del file_data
                del totalidad
                doit(direccion)
                break
    threads_ = []
    if start_dir[:2] == "MZ" or (start_dir[:2] in ("NA", "NI") and start_dir[:4] not in ("NA-9", "NI-9")):
        for modulo in range(int(start_dir[9:][:3]), int(end_dir[9:][:3])+1):
            for nivel in range(4):
                if int(start_dir[3]) == 2 and modulo <= 8 and (nivel+1 == 2 or nivel+1 == 3):
                    for pos in range(4):
                        for lvl in (1, 5):
                            direccion = sector + "-" + string_zero(modulo) + "-0{}-{}{}".format(nivel+1, lvl, pos+1)
                            if direccion not in data_total:
                                x = threading.Thread(target=doit, args=(direccion,))
                                threads_.append(x)
                    for pos in (1, 2):
                        for lvl in (2, 3, 4):
                            direccion = sector + "-" + string_zero(modulo) + "-0{}-{}{}".format(nivel+1, lvl, pos)
                            if direccion not in data_total:
                                x = threading.Thread(target=doit, args=(direccion,))
                                threads_.append(x)
                            
                for pos in range(5):
                    direccion = sector + "-" + string_zero(modulo) + "-0{}-0{}".format(nivel+1, pos+1)
                    if direccion not in data_total:
                        x = threading.Thread(target=doit, args=(direccion,))
                        threads_.append(x)
    elif start_dir[:2] == "RK" or start_dir[:4] in ("NA-9", "NI-9"):
        for modulo in range(int(start_dir[9:][:3]), int(end_dir[9:][:3])+1):
            for nivel in range(1, 6):
                for pos in range(2):    
                    direccion = sector + "-" + string_zero(modulo) + "-0{}-0{}".format(nivel+1, pos+1)
                    if direccion not in data_total:
                        x = threading.Thread(target=doit, args=(direccion,))
                        threads_.append(x)

    if start_dir[:4] in ("NA-9","NI-9"):
        sector = "RK-0-017"
    for x in threads_:
        x.start()
    for x in threads_:
        x.join()

import locale
locale.setlocale(locale.LC_ALL, "")

def buscarLugar(sec, piso, calle, *args):
    llego = len(args)
    cliente = "__"
    sector = "{}-{}-{}".format(sec, piso, string_zero(calle))
    def foo():
        
        
        
        total_modulo = 62
        if "SI" not in sector:
            x = threading.Thread(target=contador, daemon=True, args=(sector,))
            print("Iniciando hilo")
            x.start()
            hilos[sector] = x
            cache[sector] = []
        if llego:
            cliente = args[0]
            cliente_actuales[sector] = cliente
            socketio.emit('contador', 'Buscando...', room=cliente)

        if sec == "MZ":
            if piso <= 1:
                total_modulo = 86
            if (piso == 0) and (calle == 26):
                start_dir = "NA-0-026-001-01-01"
                end_dir = "NA-0-026-038-04-05"
                scraper(start_dir, end_dir)
                start_dir = "NI-0-026-039-01-01"
                end_dir = "NI-0-026-061-04-05"
                scraper(start_dir, end_dir)
                start_dir = "NA-0-026-063-01-01"
                end_dir = "NA-0-026-085-04-05"
                scraper(start_dir, end_dir)
            elif piso == 0 and calle == 27:
                pass
            # elif piso == 0 and calle == 27:
            #     start_dir = "DM-0-027-025-01-01"
            #     end_dir = "DM-0-027-055-04-05"
            #     scraper(start_dir, end_dir)
            #     start_dir = "DI-0-027-063-01-01"
            #     end_dir = "DI-0-027-081-04-05"
            #     scraper(start_dir, end_dir)
            elif piso == 1 and calle == 26:
                start_dir = "NA-1-026-001-01-01"
                end_dir = "NA-1-026-019-04-05"
                scraper(start_dir, end_dir)
                start_dir = "NI-1-026-021-01-01"
                end_dir = "NI-1-026-061-04-05"
                scraper(start_dir, end_dir)
            elif piso == 1 and calle == 27:
                start_dir = "NA-1-027-005-01-01"
                end_dir = "NA-1-027-017-04-05"
                scraper(start_dir, end_dir)
                start_dir = "NI-1-027-025-01-01"
                end_dir = "NI-1-027-055-04-05"
                scraper(start_dir, end_dir)
                # start_dir = "DI-1-027-063-01-01"
                # end_dir = "DI-1-027-077-04-05"
                # scraper(start_dir, end_dir)
            elif (piso == 2 or piso == 3) and calle == 27:
                pass

            else:
                start_dir = ""
                end_dir = ""
                if (calle >= 1 and calle <= 3) and (piso == 3):
                    if calle == 1:
                        start_dir = "HV-3-{}-026-01-01".format(string_zero(calle))
                    elif calle == 2:
                        start_dir = "HV-3-{}-002-01-01".format(string_zero(calle))

                    else:
                        start_dir = "HV-3-{}-001-01-01".format(string_zero(calle))
                        

                elif calle == 1:
                    start_dir = "{}-{}-{}-006-01-01".format(sec, piso, string_zero(calle))
                elif calle == 2 or calle == 9 or calle == 18:
                    start_dir = "{}-{}-{}-002-01-01".format(sec, piso, string_zero(calle))  

                elif calle == 27:
                    start_dir = "{}-{}-{}-005-01-01".format(sec, piso, string_zero(calle))
                else:
                    start_dir = "{}-{}-{}-001-01-01".format(sec, piso, string_zero(calle))

                if (calle >= 1 and calle <= 3) and (piso == 3):
                    end_dir = "HV-3-{}-058-04-05".format(string_zero(calle))
                elif calle > 0 and calle < 4:
                    end_dir = "{}-{}-{}-058-04-05".format(sec, piso, string_zero(calle))
                elif (calle == 8 or calle == 17 or calle == 26) and (piso == 0 or piso == 1):
                    end_dir = "{}-{}-{}-085-04-05".format(sec, piso, string_zero(calle))
                    

                elif calle == 4:
                    if piso <= 1:
                        end_dir = "{}-{}-{}-082-04-05".format(sec, piso, string_zero(calle))
                    elif piso == 2:
                        end_dir = "{}-{}-{}-058-04-05".format(sec, piso, string_zero(calle))
                    elif piso == 3:
                        end_dir = "{}-{}-{}-062-04-05".format(sec, piso, string_zero(calle))

                elif (calle == 5 or calle == 8 or calle == 13 or calle == 17 or calle == 21 or calle == 26) and (piso == 2 or piso == 3):
                    end_dir = "{}-{}-{}-061-04-05".format(sec, piso, string_zero(calle))
                elif piso == 0 or piso == 1:
                    end_dir = "{}-{}-{}-086-04-05".format(sec, piso, string_zero(calle))
                
                elif piso == 2 or piso == 3:
                    end_dir = "{}-{}-{}-062-04-05".format(sec, piso, string_zero(calle))
                
                if calle == 26 and piso == 1:
                    start_dir = ""                
                
                scraper(start_dir, end_dir)


        elif sec == "RK":
            start_dir = "RK-0-{}-001-02-01".format(string_zero(calle))
            if calle == 17:
                start_dir = "NA-9-017-001-03-01"
                end_dir = "NA-9-017-104-04-02"
                scraper(start_dir, end_dir)
                start_dir = "NI-9-017-001-01-01"
                end_dir = "NI-9-017-104-01-02"
                scraper(start_dir, end_dir)

            elif calle == 2:
                end_dir = "RK-0-{}-104-04-02".format(string_zero(calle))
            else:
                end_dir = "RK-0-{}-104-06-02".format(string_zero(calle))
            
            scraper(start_dir, end_dir)

        # elif sec == "RO":
        elif sec == "SI":
            if sector in hilos and hilos[sector].is_alive():
                socketio.emit("TL-SI", cache[sector])
            else:
                x = threading.Thread(target=contador, daemon=True, args=(sector,))
                x.start()
                hilos[sector] = x
                SI_DATA = {}
                threads = []
                dire = []
                def search(page):
                    try:
                        soup = BeautifulSoup(requests.get(f"https://wms.mercadolibre.com.ar/reports/stage-in?page={page}", cookies=jar).text, features="lxml")
                        li_list = soup.find_all("li", {"class" : "andes-pagination__button"})
                        if len(li_list) > 0:
                            del li_list[len(li_list)-1]
                            del li_list[0]
                            for li in li_list:
                                try:
                                    if int(li.text) > page:
                                        x = threading.Thread(target=search, args=(int(li.text),))
                                        index = len(threads)
                                        threads.append(x)
                                        threads[index].start()
                                        break
                                except:
                                    continue
                        tbody = soup.find("tbody")
                        try:
                            tr_list = tbody.find_all('tr')
                            for tr in tr_list:
                                pallet = tr.find("td", {"data-title" : "pallet_id"}).text
                                direccion = tr.find("td",{"data-title" : "address_id"}).text
                                if len(direccion) == 0:
                                    continue
                                dire.append([direccion, pallet])
                                inbound = tr.find("td", {"data-title" : "inbounds"}).text
                                fecha = tr.find("td", {"data-title" : "received_at"}).text
                                if fecha != '-':
                                    fecha = fecha[:6] + "." + fecha[6:]
                                    if direccion not in SI_DATA:
                                        SI_DATA[direccion] = [[inbound, pallet, datetime.strptime(fecha, "%d/%b/%Y %H:%M").strftime("%d/%m/%Y %H:%M")]]
                                    else:
                                        SI_DATA[direccion].append([inbound, pallet, datetime.strptime(fecha, "%d/%b/%Y %H:%M").strftime("%d/%m/%Y %H:%M")])

                                else:
                                    if direccion not in SI_DATA:
                                        SI_DATA[direccion] = [[inbound, pallet, fecha]]
                                    else:
                                        SI_DATA[direccion].append([inbound, pallet, fecha])
                        except:
                            pass
                    except:
                        print(f"Exception: {traceback.format_exc()} ---- Pagina N°{page}")
                                
                search(1)
                for thread in threads:
                    thread.join()
                # 80 
                cache[sector] = SI_DATA

                with open("data.json","w") as file:
                    file.write(str(dire))
                
                print("Enviado data SI...")
                socketio.emit("TL-SI", SI_DATA)

        if llego:
            socketio.emit('contador', 'Busqueda finalizada', room=cliente)

    
    # Chequeo de si ya existe el cliente buscando lugar en otra calle para sacarlo...
    if "SI" in sector:
        foo()
    if llego:
        cliente = args[0]
        for key in cliente_actuales:
            if cliente in cliente_actuales[key] and type(cliente_actuales[key]) != str:
                cliente_actuales[key].remove(cliente)
                break
            elif cliente == cliente_actuales[key]:
                del cliente_actuales[key]
                break

        for key in cliente_esperando:
            if cliente in cliente_esperando[key] and type(cliente_esperando[key]) != str:
                cliente_esperando[key].remove(cliente)
                break
            elif cliente == cliente_esperando[key]:
                del cliente_esperando[key]
                break

        # Si el hilo está activo (todavía falta para volvera a actualizar...)
        if sector in hilos and hilos[sector].is_alive():
            # Si no existe la key actual en la calle sector la crea
            if sector not in cliente_esperando:
                cliente_esperando[sector] = []
            # Si el cliente está esperando...
            elif cliente in cliente_esperando[sector]:
                # Le manda toda la data
                for dir_cache in cache[sector]:
                    socketio.emit('data', [dir_cache[0], dir_cache[1], dir_cache[2]], room=cliente)
                return
            cliente_esperando[sector].append(cliente)
            socketio.emit('clear', 'clear', room=cliente)
            for dir_cache in cache[sector]:
                socketio.emit('data', [dir_cache[0], dir_cache[1], dir_cache[2]], room=cliente)
            while hilos[sector].is_alive():
                try:
                    if cliente not in cliente_esperando[sector]:
                        return
                except: 
                    pass
                time.sleep(1)###
            cliente_esperando[sector].remove(cliente)
        else:
            foo()
    else:
        if sector in hilos and hilos[sector].is_alive():
            pass
        else:
            foo()
    data = {}
    with open("data","r") as file:
        data = eval(file.read())
    with open("data","w") as file:
        data["pos"] = Metrica.pos
        file.write(str(data))
    MESSAGE_TL = "Ultima actualizacion: {}".format(datetime.now().strftime("%d/%m/%Y %H:%M"))

@socketio.on('pedir')
def func(msg):
    cliente = request.sid
    x = threading.Thread(target=buscarLugar, daemon=True, args=(msg[0], int(msg[1]), int(msg[2]), cliente,))
    x.start()
    # buscarLugar(msg[0], int(msg[1]), int(msg[2]), cliente)
@socketio.on('disconnect')
def desconectado():
    cliente = request.sid
    pase = True
    while (pase is True):
        try:
            for key in cliente_actuales:
                if cliente in cliente_actuales[key] and type(cliente_actuales[key]) != str:
                    cliente_actuales[key].remove(cliente)
                    raise Exception("exito")
                elif cliente_actuales[key] == cliente:
                    del cliente_actuales[key]
                    raise Exception("exito")
            raise Exception("exito")
        except Exception as e:
            if (e.args[0] == "exito"):
                pase = False
            else:
                time.sleep(2)
    pase = True
    while (pase is True):
        try:
            for key in cliente_esperando:
                if cliente in cliente_esperando[key] and type(cliente_esperando[key]):
                    cliente_esperando[key].remove(cliente)
                    raise Exception("exito")
                elif cliente == cliente_esperando[key]:
                    del cliente_esperando[key]
                    raise Exception("exito")
            raise Exception("exito")
        except Exception as e:
            if (e.args[0] == "exito"):
                pase = False
            else:
                time.sleep(2)

    if pase == False:
        try:
        
            cliente_TL.remove(cliente)
        except:
            pass
@app.route('/')
def main():
    return render_template('MLSearcher.html')

@app.route('/TL')
def TL():
    
    return render_template('TL.html')

@socketio.on('TL-data')
def TL_data(text):
    def foo(sector, posiciones):
        total = {}
        for pos in posiciones:
            total[pos] = 0
        for pos in posiciones:
            num = Metrica.get_disponible(pos)
            total[pos] += num
            sector[0][pos] = num
        sector.append(total)
        # Obtengo las posiciones ocupadas por piso [MZ]
        sector.append({})
        for pos in posiciones:
            total[pos] = 0
        for pos in posiciones:
            num = Metrica.get_ocupada(pos)
            total[pos] += num
            sector[2][pos] = num
        sector.append(total)
    def t(cliente):
        MZ = [{}]
        RK = [{}]
        foo(MZ, ("MZ-0", "MZ-1", "MZ-2", "MZ-3"))
        foo(RK, ("RK-02","RK-03","RK-04","RK-05","RK-06"))
        cliente_TL.append(cliente)
        socketio.emit('TL-data',[Metrica.pos, MZ, RK], room=cliente)
        socketio.emit('TL-message', MESSAGE_TL, room=cliente)
        buscarLugar("SI", 0, 0, cliente)
    threading.Thread(target=t, daemon=True, args=(request.sid,)).start()


@socketio.on('reporte-qr')
def reporteqr(msg):
    Metrica.add_qr(msg)

@socketio.on('reporte-er')
def reporteer(msg):
    Metrica.add_error(msg)

@socketio.on('update-RK')
def update_lvl(msg):
    def t():
        for calle in range(2, 16):
            buscarLugar("RK", 0, calle)
    x = threading.Thread(target=t, daemon=True)
    x.start()

@socketio.on('update-floor')
def update_floor(msg):
    def t(msg):
        for calle in range(27):
            buscarLugar("MZ", int(msg), calle+1)
    x = threading.Thread(target=t, daemon=True, args=(msg,))
    x.start()

@socketio.on('update-everything')
def update_everything(msg):
    x = threading.Thread(target=inventario, daemon=True)
    x.start()
def inventario():
    t0 = datetime.now()
    MESSAGE_TL = "Actualizando... {}".format(t0.strftime("%d/%m/%Y %H:%M"))
    for waitingclient in cliente_TL:
        socketio.emit("TL-message", MESSAGE_TL, room=waitingclient)
    threads = []
    for piso in (0, 4):
        for calle in range(27):
            buscarLugar("MZ", piso, calle+1)

    for calle in range(2, 16):
        buscarLugar("RK", 0, calle)
    t1 = datetime.now()
    MESSAGE_TL = "Ultima actualización: Inicio: {} -- Fin: {}".format(t0.strftime("%d/%m/%Y %H:%M"), t1.strftime("%d/%m/%Y %H:%M"))
    for waitingclient in cliente_TL:
        socketio.emit('TL-message', MESSAGE_TL, room=waitingclient)
    time.sleep(60 * 60)


    



def reportes():
    while True:
        if Metrica.reporte_error:
            print("Enviando reportes de errores...")
            doc.append_err(Metrica.reporte_error)
            Metrica.reporte_error.clear()
        
        if Metrica.reporte_qr:
            print("Enviando reportes de QR...")
            doc.append_qr(Metrica.reporte_qr)
            Metrica.reporte_qr.clear()

        if Metrica.reporte_meli:
            print("Enviando reportes de MELIs sin Cubing...")
            doc.append_MELI(Metrica.reporte_meli)
            Metrica.reporte_meli.clear()
        
        time.sleep(5 * 60)



def query():
    while True:
        try:
            code = input(": ")
            if "BUSCAR" in code:
                print(Metrica.pos[code[7:]])
            elif "IS_ALIVE" in code:
                print(hilos[code[9:]].is_alive())
            elif "CACHE" in code:
                for pos in cache[code[6:]]:
                    print(pos)
            elif "ALL_POS" in code:
                total = 0
                contador = 0
                if code[8:][:2] == "MZ":
                    for nivel in range(4):
                        for pos in range(5):
                            if code[8:] + "-0{}-0{}".format(nivel+1, pos+1) in Metrica.pos:
                                contador += 1
                                total += Metrica.pos[code[8:] + "-0{}-0{}".format(nivel+1, pos+1)][1]
                                print("{}-0{}-0{}: {}".format(code[:8], nivel+1, pos+1, Metrica.pos[code[8:] + "-0{}-0{}".format(nivel+1, pos+1)]))
                else:
                    for nivel in range(1, 6):
                        for pos in range(2):
                            if code[8:] + "-0{}-0{}".format(nivel+1, pos+1) in Metrica.pos:
                                contador += 1
                                total += Metrica.pos[code[8:] + "-0{}-0{}".format(nivel+1, pos+1)][1]
                                print("{}-0{}-0{}: {}".format(code[:8], nivel+1, pos+1, Metrica.pos[code[8:] + "-0{}-0{}".format(nivel+1, pos+1)]))

                print("Promedio de MELIs: {}".format(round(total/contador,2)))
            elif "SEARCHLUGAR" in code:
                code = code[12:]
                buscarLugar(code[:2], int(code[:4][3]), int(code[:8][5:]))
            elif "VOLUMEN" in code:
                print(round(scrapMELI(code[8:]), 2))
            elif "FREE" in code:
                scraper(code[5:], code[5:])
            elif "CLS" in code or "CLEAR" in code:
                os.system("cls")
            elif "INVENTARIO" in code:
                x = threading.Thread(target=inventario, daemon=True)
                x.start()

            elif "HELP" in code:
                print("BUSCAR x: Buscar posicion en sus pos")
                print("IS_ALIVE x: Buscar hilo x (por sector) en diccionario hilos")
                print("CACHE: Buscar calle x en diccionario cache")
                print("ALL_POS: Buscar todas las pos en modulo x en diccionario ALL_POS")
                print("SEARCHLUGAR: Buscar lugar en sector-piso-calle")
                print("VOLUMEN: Volumen obtenido x MELI")
                print("FREE: Calcular POS y guardarlo")
                print("INVENTARIO: Inicia hilo inventario")
                print("CLS o CLEAR: Limpiar consola")


            else:
                print("ERROR DE COMANDO, ESCRIBA HELP PARA VER LOS COMANDOS DISPONIBLES")
        except Exception as e:
            print("ERROR EN HILO QUERY: {}".format(e.args[0]))


if __name__ == '__main__':
    try:
        ip = str()
        port = int()

        buscador()
        # form = mainForm()
        # form.start()
        
        with open('data', 'r') as file:
            data = eval(file.read())
            ip = data['ip']
            port = int(data['port'])
            Metrica.pos = data['pos']
            Metrica.update()
            for cookie in data['cookies']:
                jar.set(cookie["name"], cookie["value"], domain=cookie["domain"], path=cookie["path"])                

                
        local_ip = socket.gethostbyname(socket.gethostname())
        print("Ejecutando servidor en {}:{}".format(local_ip if ip == '0.0.0.0' else ip, port))
        webbrowser.get().open("http://{}:{}/".format(local_ip if ip == '0.0.0.0' else ip, port), new=2)
        webbrowser.get().open("http://{}:{}/TL".format(local_ip if ip == '0.0.0.0' else ip, port), new=2)



        # x = threading.Thread(target=inventario, daemon=True)
        # x.start()

        y = threading.Thread(target=reportes)
        y.setDaemon(True)
        y.start()
        x = threading.Thread(target=query, daemon=True)
        x.start()
        socketio.run(app, host=ip, port=port, debug=True)
    except Exception as e:
        print("Hubo un error hosteando el servidor... Traceroute: ")
        print(e)
        input()
        del Metrica
    del Metrica
    