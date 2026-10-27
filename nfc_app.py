import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time
import sqlite3
from datetime import datetime
from smartcard.System import readers
from smartcard.util import toHexString
from smartcard.Exceptions import NoCardException
from pynput.keyboard import Controller, Key

class LectorNFCApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Lector NFC - SIRAE Local")
        self.root.geometry("450x400")
        self.root.resizable(False, False)
        
        self.hilo_lector = None
        self.detener_evento = threading.Event()
        
        self.init_db()
        self.crear_interfaz()

    def init_db(self):
        """Inicializa la base de datos SQLite local."""
        conn = sqlite3.connect("nfc_local.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uid TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                synced INTEGER DEFAULT 0
            )
        """)
        conn.commit()
        conn.close()

    def guardar_log(self, uid):
        """Guarda la lectura en la BD y actualiza la GUI."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Guardar en SQLite
        conn = sqlite3.connect("nfc_local.db")
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT id FROM log WHERE uid = ?", (uid,))

        except Exception as e:
            print(f"Error al consultar la base de datos: {e}")

        if cursor.fetchone() is not None:
            mensaje = f"[{now}] UID ya registrado: {uid}\n"
            self.root.after(0, self.escribir_consola, mensaje)
            conn.close()
        else:
            cursor.execute("INSERT INTO log (uid, timestamp, synced) VALUES (?, ?, 0)", (uid, now))
            conn.commit()
            conn.close()

            # Actualizar la interfaz (se usa root.after para ser thread-safe)
            mensaje = f"[{now}] UID: {uid}\n"
            self.root.after(0, self.escribir_consola, mensaje)


    def crear_interfaz(self):
        # Marco de botones
        frame_top = tk.Frame(self.root, pady=10)
        frame_top.pack(fill=tk.X)

        self.btn_iniciar = ttk.Button(frame_top, text="▶ Iniciar Lector", command=self.iniciar_lector)
        self.btn_iniciar.pack(side=tk.LEFT, padx=20, expand=True)

        self.btn_detener = ttk.Button(frame_top, text="⏹ Detener Lector", command=self.detener_lector, state=tk.DISABLED)
        self.btn_detener.pack(side=tk.RIGHT, padx=20, expand=True)

        # Etiqueta de estado
        self.lbl_estado = tk.Label(self.root, text="Estado: Detenido", fg="red", font=("Arial", 10, "bold"))
        self.lbl_estado.pack(pady=5)

        # Consola de logs
        self.consola = scrolledtext.ScrolledText(self.root, width=50, height=15, state=tk.DISABLED, bg="#1e1e1e", fg="#00ff00", font=("Consolas", 9))
        self.consola.pack(padx=10, pady=10)
        
        self.escribir_consola("Sistema inicializado. Listo para comenzar.\n")

    def escribir_consola(self, texto):
        """Agrega texto al recuadro de logs."""
        self.consola.config(state=tk.NORMAL)
        self.consola.insert(tk.END, texto)
        self.consola.see(tk.END)
        self.consola.config(state=tk.DISABLED)

    def iniciar_lector(self):
        self.btn_iniciar.config(state=tk.DISABLED)
        self.btn_detener.config(state=tk.NORMAL)
        self.lbl_estado.config(text="Estado: Buscando lector...", fg="orange")
        
        self.detener_evento.clear()
        self.hilo_lector = threading.Thread(target=self.bucle_lectura, daemon=True)
        self.hilo_lector.start()

    def detener_lector(self):
        self.detener_evento.set()
        self.btn_iniciar.config(state=tk.NORMAL)
        self.btn_detener.config(state=tk.DISABLED)
        self.lbl_estado.config(text="Estado: Detenido", fg="red")
        self.escribir_consola("Lector detenido por el usuario.\n")

    def bucle_lectura(self):
        r = readers()
        if not r:
            self.root.after(0, self.lbl_estado.config, {"text": "Estado: Error - Lector no detectado", "fg": "red"})
            self.root.after(0, self.escribir_consola, "ERROR: Conecta el lector ACR122U y vuelve a iniciar.\n")
            self.root.after(0, self.btn_iniciar.config, {"state": tk.NORMAL})
            self.root.after(0, self.btn_detener.config, {"state": tk.DISABLED})
            return

        lector = r[0]
        teclado = Controller()
        self.root.after(0, self.lbl_estado.config, {"text": f"Estado: Activo ({lector})", "fg": "green"})
        self.root.after(0, self.escribir_consola, "Lector NFC conectado. Escaneando...\n")

        conexion = lector.createConnection()

        while not self.detener_evento.is_set():
            try:
                conexion.connect()
                comando_uid = [0xFF, 0xCA, 0x00, 0x00, 0x00]
                data, sw1, sw2 = conexion.transmit(comando_uid)
                
                if sw1 == 144 and sw2 == 0:
                    uid = toHexString(data).replace(" ", "")
                    
                    # 1. Escribir UID con pynput
                    teclado.type(uid)
                    teclado.press(Key.enter)
                    teclado.release(Key.enter)
                    
                    # 2. Guardar en SQLite y Log
                    self.guardar_log(uid)
                    
                    # Evitar rebotes de lectura
                    time.sleep(3)
            except NoCardException:
                time.sleep(0.3)
            except Exception as e:
                # Si se desconecta el cable de golpe
                time.sleep(0.3)

if __name__ == "__main__":
    root = tk.Tk()
    app = LectorNFCApp(root)
    root.mainloop()