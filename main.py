import pyperclip
import win32gui
import langid
import ctypes
import signal
import sys
import logging
import numpy as np
from kokoro_onnx import Kokoro
import sounddevice as sd
import threading
import re
import queue

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")

kokoro = Kokoro("kokoro-v1.0.onnx", "voices-v1.0.bin")
kokoro.create("warmup", voice="af_bella", speed=1.0, lang="es")  # primera inferencia cuesta más

WM_CLIPBOARDUPDATE = 0x031D
ultimo_clip = ""
detener = threading.Event()
lock_clipboard = threading.Lock()


def salir(sig, frame):
    win32gui.PostQuitMessage(0)
    sys.exit(0)


def crear_ventana():
    wc = win32gui.WNDCLASS()
    wc.lpfnWndProc = procesar_mensaje
    wc.lpszClassName = "NarradorClipboard"
    wc.hInstance = win32gui.GetModuleHandle(None)
    win32gui.RegisterClass(wc)
    hwnd = win32gui.CreateWindow(
        wc.lpszClassName, "Narrador",
        0, 0, 0, 0, 0,  # invisible, sin tamaño
        0, 0, wc.hInstance, None
    )
    ctypes.windll.user32.AddClipboardFormatListener(hwnd)
    return hwnd


def detectar_idioma(text):
    idioma, _ = langid.classify(text)
    return "es" if idioma == "es" else "en-us"


def limpiar_texto(texto):
    texto = texto.replace("\n", " ")
    texto = re.sub(r'\s+', ' ', texto)          # espacios múltiples → uno
    texto = re.sub(r'[^\w\s.,!?¿¡]', '', texto) # quitar símbolos raros
    return texto.strip()


def voz_por_idioma(lang):
    return "ef_dora" if lang == "es" else "af_bella"


def narrar_streaming(texto):
    texto = limpiar_texto(texto)
    frases = re.split(r'(?<=[.!?,])\s+', texto.strip())
    frases = [f for f in frases if f.strip()]

    cola = queue.Queue()

    def generador():
        for frase in frases:
            if detener.is_set():
                break
            idioma = detectar_idioma(frase)
            voice = voz_por_idioma(idioma)
            frase_tts = frase.strip()
            if not frase_tts.endswith(('.', '!', '?')):
                frase_tts += '.'  # evita que Kokoro corte el último fonema
            samples, sr = kokoro.create(frase_tts, voice=voice, speed=1.0, lang=idioma)
            silencio = np.zeros(int(sr * 0.3), dtype=np.float32)
            samples = np.concatenate([samples, silencio])
            cola.put((samples, sr))
        cola.put(None)  # señal de fin

    def reproductor():
        while True:
            item = cola.get()
            if item is None or detener.is_set():
                break
            samples, sr = item
            sd.play(samples, sr)
            sd.wait()

    threading.Thread(target=generador, daemon=True).start()
    reproductor()


def procesar_mensaje(hwnd, msg, wparam, lparam):
    global ultimo_clip
    if msg == WM_CLIPBOARDUPDATE:
        clip = pyperclip.paste()
        with lock_clipboard:
            if clip == ultimo_clip or not clip.strip():
                return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)
            ultimo_clip = clip

        logging.info("Clipboard cambió: %s", clip[:50])
        detener.set()
        sd.stop()
        detener.wait(timeout=0.1)  # deja que threads vean el evento
        detener.clear()
        threading.Thread(target=lambda: narrar_streaming(clip), daemon=True).start()

    return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)


signal.signal(signal.SIGINT, salir)
hwnd = crear_ventana()
win32gui.PumpMessages()  # espera mensajes de Windows
