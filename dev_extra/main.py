from tkinter import Tk, Button, Label, messagebox, Toplevel, END as tk_END, Entry, PhotoImage, TOP as tkTOP
from tkinter.ttk import Treeview, Combobox
from traceback import format_exc
from socket import gethostbyname, gethostname
from UserManager import User_Manager
class Form:


    def __deletePos(self):
        pos = self.tabla.item(self.tabla.focus())['text']
        if pos and messagebox.askokcancel(title="Eliminar posicion", message=f"¿Esta seguro que desea eliminar la pos inexistente {pos}?"):
            self.data.remove(pos)
            self.__updateFile_pos()
            self.__table_update()

    def __updateFile_pos(self):
        with open("pos","w") as file:
            file.write(str(self.data))
    def __addPos(self):
        add_root = Toplevel(self.root)
        add_root.title("Agregar pos")
        l1 = Label(add_root, text="Posicion: ")
        eadd = Entry(add_root)
        def add():
            text = eadd.get()
            if text:
                if text not in self.data:
                    self.data.append(text)
                    add_root.destroy()
                    add_root.update()
                    messagebox.showinfo(title="Actualizado", message=f"La posicion {text} fue agregada a la base de datos de exclusión satisfactoriamente.")
                    self.__updateFile_pos()
                    self.__table_update()
                else:
                    messagebox.showwarning(title="Ya existe", message=f"La posicion {text} ya esta registrada en la base de datos")

            else:
                messagebox.showerror(title="ERROR", message=f"ERROR: Por favor ingrese una posicion para excluir de la busqueda.")
        bok = Button(add_root, text="Agregar posicion", command=add)

        l1.grid(row=0, column=0, padx=10, pady=10)
        eadd.grid(row=0, column=1, padx=10, pady=10)
        bok.grid(row=1, column=0, columnspan=2, padx=10, pady=10)




    def __table_update(self):
            self.tabla.delete(*self.tabla.get_children())
            for pos in self.data:
                if pos[:8] == self.cSector.get():
                    self.tabla.insert("", tk_END, text=pos)
            
    def __posiciones_inexistentes(self):
        pos_root = Toplevel(self.root)
        pos_root.title("Posiciones inexistentes")
        self.tabla = Treeview(pos_root)
        badd_pos = Button(pos_root, text="Agregar posicion", command=self.__addPos)
        bdelete_pos = Button(pos_root, text="Eliminar posicion", command=self.__deletePos)    
        l1 = Label(pos_root, text="Sector-piso-calle: ")
        self.cSector = Combobox(pos_root, width=10)
        self.tabla.heading("#0", text="Posición")

        
        self.data = []
        with open("pos","r") as file:
            self.data = eval(file.read())
        self.data.sort()

        sectores = []
        for pos in self.data:
            if pos[:8] not in sectores:
                sectores.append(pos[:8])
        self.cSector['values'] = sectores

        
        self.cSector.bind("<<ComboboxSelected>>", lambda x: self.__table_update())
        l1.grid(row=0, column=0)
        self.cSector.grid(row=0, column=1, padx=10)
        self.tabla.column("#0", anchor="n")    
        self.tabla.grid(row=1, column=0, columnspan=2)
        badd_pos.grid(row=2, column=0, pady=10, padx=10)
        bdelete_pos.grid(row=2, column=1, padx=10)

    def __read_file(self):
        with open("data","r") as file:
            data = eval(file.read())
            ip = data["ip"]
            if ip == "0.0.0.0":
                ip = gethostbyname(gethostname())
                

            self.label_IP['text'] = ip + ":" + data["port"]
    def __init__(self):
        AccountManagar = User_Manager()
        self.root = Tk()
        ON_IMG = PhotoImage(file="ON_ICON.png").subsample(3, 3)
        OF_IMG = PhotoImage(file="OFF_ICON.png").subsample(3, 3)
        self.root.geometry("300x300")
        self.root.title("P.A Helper")
        self.label_IP = Label(self.root)
        l0 = Label(self.root, text="Usuario registrado: ")
        l1 = Label(self.root, text="IP del servidor: ")
        l2 = Label(self.root, text="Ultima actualizacion: ")
        self.luser = Label(self.root, text=AccountManagar.get_username())
        
        def check_account():
            if self.luser["text"] == "..." or self.luser["text"] == "Ninguno":
                AccountManagar.login()
                self.luser = Label(self.root, text=AccountManagar.get_username())
        check_account()
        # Ultima actualizacion
        self.label_lastupdate = Label(self.root)
        self.__read_file()

        # Boton para ver posiciones inexistentes
        verPosiciones_inexistentes = Button(self.root, text="Posiciones inexistentes", 
                                            width=20, height=3, command=self.__posiciones_inexistentes)
                
        self.ON = False
        def _start():
            if self.ON:
                self.bstart_stop.configure(image=OF_IMG)
                self.bstart_stop.image = OF_IMG
                self.ON = False
            else:
                self.bstart_stop.configure(image=ON_IMG)
                self.bstart_stop.image = ON_IMG
                self.ON = True
        self.bstart_stop = Button(self.root, image=OF_IMG, command=_start)
        self.bstart_stop.image = OF_IMG
        salir = Button(self.root, text="Salir", width=20, height=3, command=self.root.quit)
        # Posicionamiento widgets
        l0.grid(row=0, column=0, sticky="w", padx=10)
        self.luser.grid(row=0, column=1, sticky="w", padx=10)
        l1.grid(row=1, column=0, columnspan=2, sticky="w", padx=10)
        self.label_IP.grid(row=1, column=1)

        l2.grid(row=2, column=0, sticky="w", padx=10)
        self.label_lastupdate.grid(row=2, column=1)
        
        self.bstart_stop.grid(row=3, column=0, columnspan=2, pady=18)
        verPosiciones_inexistentes.grid(row=4, column=0, columnspan=2)
        
        salir.grid(row=5, column=0, columnspan=2, pady=18)
        self.root.grid_columnconfigure((0,1), weight=1)

        

    def start(self):
        self.root.mainloop()

if __name__ == "__main__":
    f = Form()
    f.start()