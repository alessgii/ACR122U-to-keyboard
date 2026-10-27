import time
from smartcard.System import readers
from smartcard.util import toHexString
from smartcard.Exceptions import NoCardException
from pynput.keyboard import Controller, Key

def type_string(teclado, text):
    teclado.type(text)
    teclado.press(Key.enter)
    teclado.release(Key.enter)

def leer_nfc():
    r = readers()
    if not r:
        print("No se detectó ningún lector.")
        return

    lector = r[0]
    print(f"Lector detectado: {lector}")
    
    try:
        teclado = Controller()
        print("Controlador de teclado virtual inicializado con éxito.")
    except Exception as err:
        print(f"Error al iniciar el teclado virtual: {err}")
        return
    
    conexion = lector.createConnection()
    print("Puedes comenzar a escanear...")

    while True:
        try:
            conexion.connect()
            comando_uid = [0xFF, 0xCA, 0x00, 0x00, 0x00]
            data, sw1, sw2 = conexion.transmit(comando_uid)
            
            if sw1 == 144 and sw2 == 0:
                uid = toHexString(data).replace(" ", "")
                print(f"UID leído: {uid} -> Inyectando teclas...")
                
                type_string(teclado, uid)
                
                time.sleep(3)
        except NoCardException:
            time.sleep(0.5)
        except Exception:
            time.sleep(0.5)

if __name__ == '__main__':
    leer_nfc()