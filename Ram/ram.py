#coding=utf-8
from tkinter import *
from tkinter.ttk import *
import socket
import threading
import json
import time
from ast import literal_eval

MOD_KEYS={'Ctrl','Alt','Shift','Win'}
PORT=48684

current_id=None

tk=Tk()
tk.title('Ram (not listening)')
tk.rowconfigure(0,weight=1)
tk.columnconfigure(0,weight=1)

book=Notebook(tk)
book.grid(row=0,column=0,sticky='nswe')
book.rowconfigure(0,weight=1)
book.columnconfigure(0,weight=1)

class FancyPrefix:
    def __init__(self):
        self.time=''
        self.catagory=''

    def next(self,time,catagory,value):
        now_time=':'.join(time.split(':')[:2])
        out=(now_time if now_time!=self.time else ' '*len(self.time))+\
            (' >> ' if catagory!=self.catagory else '    ')+value
        self.time=now_time
        self.catagory=catagory
        print(out)
        return out

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

def _write(chunk,te,lvar):
    global current_id

    if chunk['type']!='title':
        te.insert(END,chunk['time'],'time')
        te.insert(END,' ')
    if chunk['type']=='string':
        te.insert(END,'"','info')
        te.insert(END,chunk['value'],'string')
        te.insert(END,'"','info')
    elif chunk['type']=='modkey':
        for key in chunk['value']:
            te.insert(END,' %s '%key,'modkey' if key in MOD_KEYS else 'key')
    elif chunk['type']=='title':
        te.insert('end','\n')
        te.insert('end','[%s] %s'%(chunk['value'][0],chunk['value'][1]),'title')
        old_var=literal_eval(lvar.get() or '()')
        te.mark_set('ind_%d'%len(old_var),'end -1 lines')
        if current_id!=chunk['value'][0]:
            current_id=chunk['value'][0]
        lvar.set(old_var+(lvar.fancy.next(chunk['time'],current_id,chunk['value'][1]),))
    else:
        te.insert('end',str(chunk),'warning')
    te.insert('end','\n')

def handle(s, addr):
    f=Frame(tk)
    f.rowconfigure(0,weight=1)
    f.columnconfigure(0,weight=3)
    f.columnconfigure(1,weight=2)
    book.add(f,text=' %s : %s '%addr)

    lvar=StringVar(value=())
    lvar.fancy=FancyPrefix()
    li=_scroll(f,Listbox,{'font':'Consolas -13','listvariable':lvar,'width':100},0,0)
    te=_scroll(f,Text,{'font':'Consolas -13'},0,1)

    def select_callback(*_):
        x=li.curselection()
        if x:
            te.see('ind_%d'%x[0])

    li.bind('<<ListboxSelect>>',select_callback)

    te.tag_config('warning',foreground='#fff',background='#f00')
    te.tag_config('string',foreground='#00f')
    te.tag_config('info',foreground='#aaa')
    te.tag_config('modkey',foreground='#000',background='#ff0')
    te.tag_config('key',foreground='#fff',background='#444')
    te.tag_config('title',foreground='#444')
    te.tag_config('time',background='#0f0')

    while True:
        try:
            xx=s.readline()
        except socket.error as e:
            te.insert(END,time.strftime('%H:%M:%S',time.localtime()),'time')
            te.insert(END,' ')
            te.insert(END,'Connection closed.','warning')
            te.insert(END,' ')
            te.insert(END,str(e),'string')
            raise
        #print(xx)
        if xx:
            chunk=json.loads(xx)
            _write(chunk,te,lvar)

def listener():
    global mainsock

    mainsock=socket.socket()
    mainsock.bind(('0.0.0.0',PORT))
    mainsock.listen(10)
    tk.title('Ram (listening on port %d)'%PORT)

    while True:
        sock,addr=mainsock.accept()
        threading.Thread(target=handle,args=(sock.makefile(encoding='utf-8'),addr)).start()

threading.Thread(target=listener).start()
mainloop()
mainsock.close()