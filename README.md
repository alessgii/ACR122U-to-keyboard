# ACR122U NFC to Keyboard Emulator

Este repositorio contiene dos scripts en Python diseñados para leer el UID de tarjetas o credenciales NFC usando un lector ACR122U, y automáticamente inyectar ese UID como si fuera escrito desde un teclado físico. 

El proyecto está dividido en dos carpetas, ya que la emulación de teclado funciona de forma muy distinta dependiendo del sistema operativo.

## Estructura del proyecto

```text
.
├── linux/
│   └── nfc_linux.py
├── windows/
│   └── nfc_windows.py
└── README.md
```

---

## 1. Linux (Probado en Fedora 44)

En Linux (especialmente en entornos con Wayland), las herramientas tradicionales para simular teclas no siempre funcionan. Este script usa `evdev` y `/dev/uinput` para crear un teclado virtual directamente en el kernel.

### Requisitos previos

Instala los demonios para leer tarjetas inteligentes y las librerías de Python necesarias:

```bash
sudo dnf install pcsc-lite pcsc-lite-ccid pcsc-tools python3-pyscard python3-evdev
```

Activa el servicio de lectura:

```bash
sudo systemctl enable --now pcscd
```

### Solución de problemas con el driver nativo (Importante)

Por defecto, el kernel de Linux suele cargar los módulos `pn533` y `nfc`, los cuales secuestran el lector ACR122U y evitan que el demonio de tarjetas pueda leerlo. Para solucionarlo, hay que agregarlos a la lista negra:

1. Desconecta el lector.
2. Crea el archivo de blacklist ejecutando este comando:
```bash
echo -e "blacklist pn533\nblacklist pn533_usb\nblacklist nfc" | sudo tee /etc/modprobe.d/blacklist-acr122u.conf
```
3. Descarga los módulos de la memoria (ignora los errores si no están cargados):
```bash
sudo modprobe -r pn533_usb pn533 nfc
```
4. Reinicia el servicio y vuelve a conectar el lector:
```bash
sudo systemctl restart pcscd
```

### Uso

Entra a la carpeta de Linux y ejecuta el script. **Es obligatorio usar `sudo`** porque el script necesita interactuar directamente con `/dev/uinput` para emular el teclado.

```bash
cd linux
sudo python3 nfc_linux.py
```

---

## 2. Windows

En Windows el proceso es más sencillo porque no hay módulos nativos que interfieran con el lector, y la inyección de teclas se hace directamente con la librería `pynput`.

### Requisitos previos

Asegúrate de tener Python instalado y ejecuta en tu CMD o PowerShell los comandos para descargar las dependencias. Puedes usar cualquiera de las siguientes opciones dependiendo de cómo esté configurado tu entorno:

**Opción 1: Usando pip directamente**
```powershell
pip install pyscard pynput
```

**Opción 2: Usando el ejecutable de Python (útil si la opción 1 falla)**
```powershell
py -m pip install pyscard pynput
```

### Uso

Entra a la carpeta de Windows y ejecuta el script normalmente:

```cmd
cd windows
python nfc_windows.py
```
*(Nota: Si PowerShell te da problemas al usar el comando `python`, puedes intentar ejecutarlo usando `py nfc_windows.py`)*

---

### Notas adicionales
Ambos scripts incluyen un retraso automático después de leer una tarjeta. Esto evita que, si dejas la credencial pegada al lector, el UID se escriba decenas de veces seguidas. Además, ambos scripts envían un "Enter" automático al terminar de inyectar el UID para agilizar el uso en sistemas web o bases de datos.