import win32api
import win32con
import time

while True:
    estado = win32api.GetKeyState(win32con.VK_LBUTTON)
    print(estado)
    time.sleep(0.2)