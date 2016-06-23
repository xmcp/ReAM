#coding=utf-8

import threading
import pyHook
import pythoncom
import time
import json
import socket
import sys

PY2=sys.version_info[0]==2

queue=__import__('Queue' if PY2 else 'queue')

SPECIAL_KEYS={
    'Lcontrol','Lmenu','Lwin','Rcontrol','Rmenu','Rwin',
    'Escape','Snapshot','Home','End','Prior','Next','Return',
    'F1','F2','F3','F4','F5','F6','F7','F8','F9','F10','F11','F12',
}
MOD_KEYS={
    'Lcontrol','Lmenu','Lwin','Rcontrol','Rmenu','Rwin',
}
SHIFT={'Lshift','Rshift'}
NICKNAME={
    'Up': '↑', 'Down': '↓', 'Left': '←', 'Right': '→', 'Tab': '⇥',
    'Return': '⏎', 'Space': '⎵', 'Back': '◁', 'Delete': '◀',
    'Escape': 'Esc', 'Snapshot': 'PrtSc', 'Prior': 'PgUp', 'Next': 'PgDn',
    'Lcontrol': 'Ctrl', 'Lmenu': 'Alt', 'Lwin': 'Win',
    'Rcontrol': 'Ctrl', 'Rmenu': 'Alt', 'Rwin': 'Win',
    'Oem_Minus': '-', 'Oem_Plus': '=',  'Oem_Comma': ',', 'Oem_Period': '.',
    'Oem_5': '\\', 'Oem_3': '`', 'Oem_2': '/', 'Oem_1': ';', 'Oem_7': "'", 'Oem_4': '[', 'Oem_6': ']',
}
STRING_TIMEOUT=2
SCREENSHOT_THRESHOLD_TIME=.5
RAM_ADDR=('127.0.0.1',48684)

last_screenshot_time=0

def screenshot():
    import win32gui
    from PIL import ImageGrab
    import base64
    from io import BytesIO

    global last_screenshot_time
    if time.time()-last_screenshot_time<SCREENSHOT_THRESHOLD_TIME:
        return None
    last_screenshot_time=time.time()

    hwnd=win32gui.GetForegroundWindow()
    img_file=BytesIO()
    ImageGrab.grab(win32gui.GetWindowRect(hwnd)).save(img_file,'png')
    return base64.b64encode(img_file.getvalue()).decode()

class Chunk(object):
    __slots__=['type','time','value','image']

    def __init__(self,type_,value):
        self.time=time.strftime('%H:%M:%S',time.localtime())
        self.type=type_
        self.value=value
        self.image=None

    def json(self):
        return json.dumps({
            'type': self.type,
            'time': self.time,
            'value': self.value,
            'image': self.image,
        })

class Pumper:
    def __init__(self):
        self.msg=None
        self.chunks=[]
        self.lock=threading.Lock()
        threading.Thread(target=self.connector).start()

    def connector(self):
        while True:
            try:
                print('connecting to ram')
                s=socket.socket()
                s.connect(RAM_ADDR)
                print('connected')
                while True:
                    with self.lock:
                        buf='\n'.join(self.chunks)
                    if buf:
                        print('send %d chars'%len(buf))
                        s.send(buf.encode('utf-8'))
                        s.send(b'\n')
                        with self.lock:
                            self.chunks=[]
                    time.sleep(.5)
            except socket.error:
                time.sleep(1)

    def pump(self):
        with self.lock:
            if self.msg is not None:
                self.chunks.append(self.msg.json())
                self.msg=None

    def create(self,typ,value):
        self.pump()
        with self.lock:
            self.msg=Chunk(typ,value)

    def img(self):
        with self.lock:
            if self.msg:
                self.msg.image=screenshot()

    def breakout(self,typ,value,img=False):
        chk=Chunk(typ,value)
        if img:
            chk.image=screenshot()
        with self.lock:
            self.chunks.append(chk.json())

pumper=Pumper()
holdkey=set()
last_time=0
current_title=None
status='idle'
kqueue=queue.Queue()

def hooker():
    hm=pyHook.HookManager()
    hm.SubscribeKeyDown(keydown)
    hm.SubscribeKeyUp(keyup)
    hm.HookKeyboard()
    print('Started.')
    pythoncom.PumpMessages()

def worker(event):
    def proc():
        return NICKNAME.get(event.Key)

    global status
    global last_time
    global current_title

    window_name=(event.WindowName or '(None)').decode('gbk', 'ignore') if PY2 else (event.WindowName or '(None)')
    if current_title!=window_name:
        current_title=window_name
        pumper.breakout('title', [event.Window,window_name], img=True)

    if status=='string':
        if event.Key in SPECIAL_KEYS or time.time()-last_time>STRING_TIMEOUT:
            status='idle'
    if status=='idle':
        if event.Key in SPECIAL_KEYS:
            status='modkey'
            pumper.create(status,[])
        else:
            status='string'
            pumper.create(status,'')
            pumper.img()

    if status=='string':
        pumper.msg.value+=(proc() or (chr(event.Ascii) if event.Ascii else '⍰'))
    else: #status=='modkey'
        if any((s in holdkey for s in SHIFT)):
            pumper.msg.value.append('Shift')
            for s in SHIFT:
                holdkey.discard(s)
        pumper.msg.value.append(proc() or event.Key)
        if event.Key=='Return':
            pumper.img()

    last_time=time.time()

def queue_finder():
    while True:
        worker(kqueue.get())

def keydown(event):
    holdkey.add(event.Key)
    if event.Key not in SHIFT:
        kqueue.put(event)
    return True

def keyup(event):
    global status
    holdkey.discard(event.Key)
    if status=='modkey' and not holdkey:
        pumper.pump()
        status='idle'
    return True

if __name__=='__main__':
    #print(len(screenshot()))
    threading.Thread(target=queue_finder).start()
    hooker()