#coding=utf-8
from tkinter import *
from tkinter.ttk import *
import socket
import threading
import json

PORT=48684

tk=Tk()
tk.title('Ram (not listening)')
tk.rowconfigure(0,weight=1)
tk.columnconfigure(0,weight=1)

book=Notebook(tk)
book.grid(row=0,column=0,sticky='nswe')
book.rowconfigure(0,weight=1)
book.columnconfigure(0,weight=1)

def _scroll(root,clas,config,row,column):
    outer_frame=Frame(root)
    outer_frame.grid(row=row,column=column,sticky='nswe')
    outer_frame.rowconfigure(0,weight=1)
    outer_frame.columnconfigure(0,weight=1)

    obj=clas(outer_frame,**config)
    obj.grid(row=0,column=0,sticky='nswe')
    scroll_bar=Scrollbar(outer_frame,orient=VERTICAL,command=obj.yview)
    scroll_bar.grid(row=0,column=1,sticky='ns')
    obj['yscrollcommand'] = scroll_bar.set

    return obj

def handle(s,addr):
    f=Frame(tk)
    f.rowconfigure(0,weight=1)
    f.columnconfigure(0,weight=1)
    f.columnconfigure(1,weight=2)
    book.add(f,text=' %s:%s '%addr)

    li=_scroll(f,Listbox,{'font':'Consolas -12'},0,0)
    te=_scroll(f,Text,{'font':'Consolas -12'},0,1)

    f=s.makefile(encoding='utf-8')
    while True:
        xx=f.readline()
        print(xx)
        chunk=json.loads(xx)
        te.insert(END,xx)

def listener():
    s=socket.socket()
    s.bind(('0.0.0.0',PORT))
    s.listen(10)
    tk.title('Ram (listening on port %d)'%PORT)

    while True:
        sock,addr=s.accept()
        handle(sock,addr)

threading.Thread(target=listener).start()
mainloop()