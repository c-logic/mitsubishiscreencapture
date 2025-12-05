#!/usr/bin/python3
import pathlib
import tkinter as tk
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from tkinter import PhotoImage,NW
import pygubu
from screencaptureui import screenUI
import http.client
import io
import os
import re
import time

class screen(screenUI):
    def __init__(self, master=None):
        super().__init__(master)
        self.canvas=self.builder.get_object("canvas1", master)
        self.button1=self.builder.get_object("button1", master)
        self.timelabel=self.builder.get_object("timelabel", master)
        self.finishlabel=self.builder.get_object("finishlabel", master)
        self.alabel=self.builder.get_object("alabel", master)
        self.auto=False
        self.conn=None
        self.save=self.builder.tkvariables['savepic']
        self.captime=self.builder.tkvariables['captime']
        self.mainwindow.title(f"Mitsubishi Screencapture")
        fnt = ImageFont.truetype("msgothic.ttc", 16)
        self.fontmask=np.zeros(((127-32), 15, 8),dtype=np.bool)
        #for i in range(32,127):
        #    im=Image.new("1",(8,15))
        #    dc=ImageDraw.Draw(im)
        #    dc.text((0, 0), chr(i), font=fnt, fill=(255))
        #    self.fontmask[i-32]=np.array(im)
        #np.save("fontmask1",self.fontmask)
        self.fontmask1=np.load("fontmask1.npy")
        self.fontmask2=np.load("fontmask3.npy")
        self.fontmask2translate=("0","1","2","3","4","5","6","7","8","9","-"," ")
        self.list=os.listdir("test")
        self.captime.trace_add('write', self.my_callback)
        self.listn=0

    def my_callback(self, var, index, mode):
        self.timelabel.config(text=f"{int(self.captime.get()):2d}s")

    def callback(self, event=None):
        self.auto=not self.auto
        if self.auto:
            self.mainwindow.after(2000,self.get)

    def searchdataSymetric(self,image,fmask,xpos,ypos,width,height,colors,offset=0,translate=None,precision=100,debug=False):
        fh,fw = fmask[0].shape
        detect=fh*fw*precision/100
        img=image.crop((xpos,ypos,xpos+fw*width,ypos+fh*height))
        if debug:
            img.save("XXX1.png")
        data = np.array(img)
        arr = None
        for c in colors:
            if arr is None: arr = np.all(data==np.array(c),axis=-1)
            else: arr |= np.all(data==np.array(c),axis=-1)

        if debug:
            Image.fromarray(arr).save("XXX2.png")
        text=tuple(bytearray(width) for _ in range(height))
        for y in range(height):
            for x in range(width):
                test = arr[fh*y:fh*y+fh,fw*x:fw*x+fw]
                counts = np.sum(fmask == test, axis=(1, 2))
                if debug: print("COUNT:",counts)
                match = np.where(counts == np.max(counts))
                text[y][x] = ord("?")
                if debug: print("MATCH:",match)
                if len(match)==1:
                    code=np.argmax(counts)
                    if counts[code]>=detect:
                        if not translate is None and code<len(translate):
                            text[y][x] = ord(translate[code])
                        else:
                            text[y][x] = code+offset
        return tuple(t.decode() for t in text) if len(text)>1 else text[0].decode()

    def searchdata(self,image,fmask,xpos,ypos,width,height,xvals,colors,precision=100,translate=None,debug=False):
        if debug:
            print(xpos,xvals)
        fh,fw = fmask[0].shape
        detect=fh*fw*precision/100
        minx=min(xvals)
        xpos+=minx
        xvals=tuple(i-minx for i in xvals)
        if debug:
            print(xpos,xvals)
        img = image.crop((xpos,ypos,xpos+width+max(xvals),ypos+height))
        if debug:
            img.save("XXX1.png")
        data = np.array(img)
        imgmask = None
        for color in colors:
            im = np.all(data == np.array(color), axis = -1)
            if imgmask is None: imgmask = im
            else: imgmask |= im

        if debug:
            Image.fromarray(imgmask).save("XXX2.png")
        q=bytearray(len(xvals))
        y=0
        for xv in range(len(xvals)):
            test=imgmask[y*height:height*y+height,xvals[xv]:xvals[xv]+width]
            if np.sum(test)!=0:
                counts = np.sum(fmask == test, axis=(1, 2))
                match = np.where(counts == np.max(counts))
                if debug:
                    print(counts,match,"DET:",detect)
                q[xv]=ord("?")
                if len(match)==1:
                    v=np.argmax(counts)
                    if debug: print(counts[v])
                    if counts[v]>=detect:
                        code=np.argmax(counts)
                        if not translate is None and code<len(translate):
                            q[xv]=ord(translate[code])
                        else:
                            q[xv]=code+0x30
            else:
                q[xv]=ord(" ")
        return q.decode()

    def get(self):
        if self.auto:
            self.mainwindow.after(self.captime.get()*1000 if self.captime.get()>=2 else 2000,self.get)
        self.button1.config(background="#ffff00" if self.auto else "#aaaaaa")
        try:
            if not self.auto:
                if not self.conn is None:
                    self.conn.close()
                    self.conn=None
                return
            if self.conn is None:
                self.conn = http.client.HTTPConnection("192.168.178.105", 80, timeout=1)
            self.conn.request("GET","/gamenp")
            r2 = self.conn.getresponse()
            if r2.status==200:
                fi=r2
            else:
                fi=None
        except:
            fi=True
            r2=open("test/"+self.list[self.listn],"rb")
            self.listn=(self.listn+1) % len(self.list)
            
        if not fi is None:
            data2 = r2.read()

            img = Image.open(io.BytesIO(data2))

            #
            text=self.searchdataSymetric(img,self.fontmask1,22,102,12,6,((0, 255, 255),),32)
            for i in range(len(text)):
                if text[i][0].isalpha():
                    getattr(self,f"line{i+1}").set(text[i])

            #Z1-Z5
            text=[self.searchdataSymetric(img,self.fontmask1,617,117,13,1,((0, 255, 0),),32)]
            text.append(self.searchdataSymetric(img,self.fontmask1,617,117+15,13,1,((0, 255, 255),),32))
            text.extend(self.searchdataSymetric(img,self.fontmask1,617,117+30,13,2,((255, 255, 255),),32))
            text.append(self.searchdataSymetric(img,self.fontmask1,617,117+60,13,1,((255, 255, 0),),32))
            for i in range(len(text)):
                if text[i].startswith("Z"):
                    getattr(self,f"zline{i+1}").set(text[i][:2]+text[i][-10:])

            #RM
            text=self.searchdataSymetric(img,self.fontmask1,22,254,12,1,((255, 255, 0),),32)
            if text.startswith("RM"):
                self.remain.set(f'RM  {float(text[2:]):8.3f}')

            #LNB
            text=self.searchdataSymetric(img,self.fontmask1,438,83,26,1,((255, 255, 0),),32)
            parts = re.findall(r'([LNB])\s+(\d+)', text)
            if len(text)>0:
                d={key: int(value) for key, value in parts}
                if "L" in d:
                    self.program.set(f'L   {d["L"]: 8d}')
                if "N" in d:
                    self.linenr.set(f'N   {d["N"]: 8d}')
                if "B" in d:
                    self.block.set(f'B   {d["B"]: 8d}')

            #FC
            text=self.searchdata(img,self.fontmask2,69,627,10,12,(0,10,20,30,40,55,65,75),((0,0,0),)).strip()
            if text.isdigit():
                self.fc.set(f"FC {float(text)/1000:9.3f}")

            #FA
            text=self.searchdata(img,self.fontmask2,66,665,10,12,(0,10,20,30,40,55,65,75),((0,0,0),)).strip()
            if text.isdigit():
                self.fa.set(f"FA {float(text)/1000:9.3f}")
            else:
                self.fa.set("FA ?")

            #E
            text=self.searchdataSymetric(img,self.fontmask2,97,578,5,1,((0, 0, 0),),translate=self.fontmask2translate).strip()
            if text.isdigit():
                self.evalue.set(f"E  {int(text): 9d}")
            else:
                self.evalue.set("E ?")

            #H
            texth=self.searchdata(img,self.fontmask2,218,627,10,12,(0,10,20,30,40),((132,130,132),(0,0,0))).strip()
            textoff=self.searchdata(img,self.fontmask2,369,627,10,12,(0,15,25,35),((132,130,132),(0,0,0))).strip()
            if texth.isdigit() and textoff.isdigit():
                self.hvalue.set(f"H{int(texth):3d}   {float(textoff)/1000:.3f}")
            else:
                self.hvalue.set("H ?")

            #finish
            textfinish=self.searchdata(img,self.fontmask2,384,662,10,12,(-15,0,10,20),((132,130,132),(0,0,0))).strip()
            if textfinish.isdigit():
                q=float(textfinish)/1000
                self.finish.set(f"+  {q:9.3f}")
                if q != 0:
                    self.finishlabel.config(background='red1')
                else:
                    self.finishlabel.config(background='green1')
            else:
                self.finish.set("FINISH ?")

            #A
            if "000" in self.searchdata(img,self.fontmask2,226,662,10,12,(0,16,32),((132,130,132),(0,0,0))).strip():
                texta="0"
            else:
                texta=self.searchdata(img,self.fontmask2,193,662,10,12,(0,10,20,35,45,55,65),((132,130,132),(0,0,0)),translate=self.fontmask2translate).strip()
            if texta.startswith("-") and texta[1:].isdigit() or texta.isdigit():
                q=float(texta)/10000
                if q != 0:
                    self.alabel.config(background='yellow1')
                else:
                    self.alabel.config(background='green1')
                self.avalue.set(f"A   {q:-8.4f}")
            else:
                self.avalue.set("A ?")

            try:
                g41,g42=img.getpixel((430,632)), img.getpixel((430,668))
                g41,g42=not all(round(i/max(g41),0) for i in g41), not all(round(i/max(g42),0) for i in g42)
                self.g4142.set(f"G4{'1' if g41 else '2' if g42 else '0'}")
            except:
                pass

            #Voltage 546,664
            text=self.searchdataSymetric(img,self.fontmask2,564,664,3,1,((0, 0, 0),),translate=self.fontmask2translate,precision=100).strip()
            print("V:",text)

            
            #FCreg 334,569 90 11,22,33,44,56,67,78,89,100
            q=tuple(img.getpixel((334+i,580))==(66, 69, 181) for i in (0,11,22,33,45,56,67,78,89)).index(True)-4
            print(f"M106 Q{q}")
            #v0 514,580 75 16
            #vg 543,580 75
            #vg 572,580 75
            #pm 632,580 75
            #h 660,580 75

            self.img = PhotoImage(data=data2, format="png")
            if self.save:
                if self.save.get():
                    if not os.path.isdir('./pictures'):
                        os.mkdir("./pictures")
                    if os.path.isdir('./pictures'):
                        open(f'{time.strftime("./pictures/%d%m%Y_%H%M%S")}.png',"wb+").write(data2)
            self.canvas.config(width=self.img.width(),height=self.img.height())
            self.canvas.create_image(0,0, anchor=NW, image=self.img)

if __name__ == "__main__":
    app = screen()
    app.run()
