import time
from smartcard.System import readers
from smartcard.util import toHexString
from smartcard.Exceptions import NoCardException
import pyautogui

def leer_nfc_windows():
    r = readers()
    if not r:
        print("No se detectó ningún lector.")
        return

    lector = r[0]
    print(f"✅ Lector detectado: {lector}")
    conexion = lector.createConnection()
    print("Listo. Acerca la credencial...")

    while True:
        try:
            conexion.connect()
            comando_uid = [0xFF, 0xCA, 0x00, 0x00, 0x00]
            data, sw1, sw2 = conexion.transmit(comando_uid)
            
            if sw1 == 144 and sw2 == 0:
                uid = toHexString(data).replace(" ", "")
                print(f"UID leído: {uid} -> Inyectando en Windows...")
                
                pyautogui.write(uid)
                pyautogui.press('enter')
                
                time.sleep(2)
        except NoCardException:
            time.sleep(0.5)
        except Exception:
            time.sleep(0.5)

if __name__ == '__main__':
    leer_nfc_windows()