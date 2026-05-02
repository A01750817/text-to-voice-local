import pyperclip
import signal
import sys
import os
import logging
import numpy as np
from kokoro_onnx import Kokoro
import sounddevice as sd
import threading
import re
import tkinter as tk
from tkinter import ttk
import time
import langid

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")

ultimo_clip = "___inicializado___"
procesando = False
mouse_x = 0
mouse_y = 0

try:
    kokoro = Kokoro("kokoro-v1.0.onnx", "voices-v1.0.bin")
    kokoro.create("warmup", voice="af_bella", speed=1.0, lang="es")
    print("Kokoro cargado correctamente")
except Exception as e:
    print(f"Error cargando Kokoro: {e}")
    sys.exit(1)


def salir(sig, frame):
    os._exit(0)


def limpiar_texto(texto):
    texto = texto.replace("\n", " ")
    texto = re.sub(r'\s+', ' ', texto)
    texto = re.sub(r'[^\w\s.,!?¿¡]', '', texto)
    return texto.strip()


def detectar_idioma(texto):
    try:
        
        idioma, _ = langid.classify(texto)
        return "es" if idioma == "es" else "en-us"
    except:
        return "es"


def narrar(texto, idioma_fijo):
    global ultimo_clip, procesando
    procesando = True

    try:
        texto = limpiar_texto(texto)

        if not texto:
            print("Texto vacío")
            return

        print(f"Procesando en {idioma_fijo}...")

        voice = "ef_dora" if idioma_fijo == "es" else "af_bella"
        lang = "es" if idioma_fijo == "es" else "en-us"

        samples, sr = kokoro.create(texto, voice=voice, speed=1.0, lang=lang)

        print(f"Audio generado: {len(samples)} samples, {sr} Hz")

        sd.play(samples, sr)
        sd.wait()

        print("Listo!")

    except Exception as e:
        logging.error(f"Error: {e}")
        print(f"Error: {e}")
    finally:
        procesando = False
def mostrar_ui(texto, x, y):
    global procesando
    if procesando:
        return

    try:
        root = tk.Tk()
        root.title("Narrador")
        root.geometry(f"290x220+{x-40}+{y-220}")
        root.attributes("-topmost", True)
        root.attributes("-alpha", 0.97)
        root.overrideredirect(True)
        root.configure(bg="#e9eef5")

        style = ttk.Style()
        style.configure("TLabel", font=("Segoe UI", 11))
        style.configure("TButton", font=("Segoe UI", 11, "bold"), padding=(12, 8))

        shell = tk.Frame(root, bg="#e9eef5", padx=12, pady=12)
        shell.pack(fill=tk.BOTH, expand=True)

        frame = tk.Frame(shell, bg="#f8fbff", padx=16, pady=14, highlightthickness=1, highlightbackground="#d0d9e8")
        frame.pack(fill=tk.BOTH, expand=True)

        header = tk.Frame(frame, bg="#f8fbff")
        header.pack(fill=tk.X)

        close_btn = tk.Button(
            header,
            text="x",
            command=root.destroy,
            font=("Segoe UI", 10, "bold"),
            bg="#f8fbff",
            fg="#5d6b82",
            activebackground="#e8eef8",
            activeforeground="#24344d",
            relief="flat",
            bd=0,
            padx=8,
            pady=2,
            cursor="hand2",
        )
        close_btn.pack(side=tk.RIGHT)

        label_texto = ttk.Label(frame, text=f"Texto: {len(texto)} caracteres", font=("Segoe UI", 10))
        label_texto.pack(pady=(4, 10))

        idioma_detectado = detectar_idioma(texto)

        ttk.Label(frame, text="Idioma detectado:").pack(pady=(10, 0))

        idioma_var = tk.StringVar(value=idioma_detectado)
        combo = ttk.Combobox(frame, textvariable=idioma_var, values=["es", "en-us"], state="readonly", width=10, font=("Segoe UI", 11))
        combo.pack(pady=5)

        def iniciar():
            idioma = idioma_var.get()
            root.destroy()
            threading.Thread(target=narrar, args=(texto, idioma), daemon=True).start()

        btn = tk.Button(
            frame,
            text="Narrar",
            command=iniciar,
            font=("Segoe UI", 11, "bold"),
            bg="#1f6feb",
            fg="white",
            activebackground="#1558b0",
            activeforeground="white",
            relief="flat",
            padx=18,
            pady=10,
            height=2,
            bd=0,
            highlightthickness=0,
            cursor="hand2",
        )
        btn.pack(pady=(16, 8), fill=tk.X)

        root.bind('<Return>', lambda e: iniciar())
        root.bind('<Button-3>', lambda e: root.destroy())
        root.bind('<Escape>', lambda e: root.destroy())

        combo.focus()
        root.after(8000, root.destroy)
        root.mainloop()
    except Exception as e:
        print(f"Error mostrando UI: {e}")


def monitorear_clipboard():
    global ultimo_clip

    time.sleep(2)

    try:
        ultimo_clip = pyperclip.paste() or "___inicializado___"
    except:
        ultimo_clip = "___inicializado___"

    while True:
        time.sleep(0.5)
        try:
            actual = pyperclip.paste()
            if actual and actual != ultimo_clip and len(actual.strip()) > 3:
                ultimo_clip = actual
                print(f"Clipboard: {actual[:50]}...")
                mostrar_ui(actual, mouse_x, mouse_y)
        except Exception as e:
            logging.debug(f"Error clipboard: {e}")


def on_click(x, y):
    global mouse_x, mouse_y
    mouse_x = x
    mouse_y = y


def crear_tray():
    from pystray import Icon, Menu, MenuItem
    from PIL import Image, ImageDraw

    img = Image.new('RGB', (64, 64), color='#5B5EA6')
    d = ImageDraw.Draw(img)
    d.ellipse([16, 16, 48, 48], fill='white')
    d.rectangle([28, 28, 36, 36], fill='#5B5EA6')

    def salir(icon, item):
        icon.stop()
        os._exit(0)

    menu = Menu(MenuItem("Mostrar", lambda i, u: print("Narrador activo")),
                MenuItem("Salir", salir))
    icon = Icon("narrador", img, "Narrador", menu)
    icon.run()


signal.signal(signal.SIGINT, salir)

try:
    from pynput.mouse import Listener

    threading.Thread(target=crear_tray, daemon=True).start()
    threading.Thread(target=monitorear_clipboard, daemon=True).start()

    print("Narrador activo. Ctrl+C para copiar texto.")
    print("Click derecho en bandeja para salir.")

    with Listener(on_click=on_click, on_release=lambda x, y: None) as listener:
        listener.join()

except ImportError as e:
    print(f"Falta dependencia: {e}")
    print("Instalá: pip install pynput pystray pillow")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
