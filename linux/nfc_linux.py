import time
from smartcard.System import readers
from smartcard.util import toHexString
from smartcard.Exceptions import NoCardException
from evdev import UInput, ecodes as e

# Mapeo de caracteres hexadecimales a códigos de tecla
KEY_MAP = {
    '0': e.KEY_0, '1': e.KEY_1, '2': e.KEY_2, '3': e.KEY_3,
    '4': e.KEY_4, '5': e.KEY_5, '6': e.KEY_6, '7': e.KEY_7,
    '8': e.KEY_8, '9': e.KEY_9,
    'A': e.KEY_A, 'B': e.KEY_B, 'C': e.KEY_C, 'D': e.KEY_D,
    'E': e.KEY_E, 'F': e.KEY_F
}

def type_string(ui, text):
    for char in text:
        keycode = KEY_MAP.get(char.upper())
        if not keycode:
            continue
        
        if char.isalpha():
            ui.write(e.EV_KEY, e.KEY_LEFTSHIFT, 1) # Shift presionado
            ui.write(e.EV_KEY, keycode, 1)         # Tecla presionada
            ui.write(e.EV_KEY, keycode, 0)         # Tecla soltada
            ui.write(e.EV_KEY, e.KEY_LEFTSHIFT, 0) # Shift soltado
        else:
            ui.write(e.EV_KEY, keycode, 1)
            ui.write(e.EV_KEY, keycode, 0)
        
        ui.syn()
        # time.sleep(0.01) 
        
    ui.write(e.EV_KEY, e.KEY_ENTER, 1)
    ui.write(e.EV_KEY, e.KEY_ENTER, 0)
    ui.syn()

def leer_nfc():
    r = readers()
    if not r:
        print("No se detectó ningún lector.")
        return

    lector = r[0]
    print(f"Lector detectado: {lector}")
    
    try:
        ui = UInput(name="ACR122U_Virtual_Keyboard")
        print("Teclado virtual creado con éxito a nivel kernel.")
    except Exception as err:
        print("Error al crear teclado virtual. ¿Lo ejecutaste con sudo?")
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
                
                type_string(ui, uid)
                
                # Pausa de 2 segundos para evitar que escriba el UID decenas de veces si dejas la tarjeta puesta
                time.sleep(3)
        except NoCardException:
            time.sleep(0.5)
        except Exception:
            time.sleep(0.5)

if __name__ == '__main__':
    leer_nfc()
