
__version__ = "0.3.0"

import socket
import time
import xml.etree.ElementTree as ET
import xml.etree.ElementTree as ElementTree
from enum import StrEnum

axes = {
  "x"       : "1",
  "y"       : "2",
  "z"       : "3",
  "pol"     : "4",
  "autslide": "5",
  "azimuth" : "6"
}

axes_sped = {
  "x"       : {"slow": 0.05,  "medium": 0.1,   "fast": 0.4   },
  "y"       : {"slow": 0.1,   "medium": 0.4,   "fast": 1.0  },
  "z"       : {"slow": 0.010, "medium": 0.015, "fast": 0.020 },
  "pol"     : {"slow": 10,    "medium": 60,    "fast": 120   },
  "autslide": {"slow": 0.01,  "medium": 0.05,  "fast": 0.2   },
  "azimuth" : {"slow": 1,     "medium": 5,     "fast": 12    }
}

class SPEED(StrEnum):
  SLOW   = "slow"
  MEDIUM = "medium"
  FAST   = "fast"

class MOVE_TYPE(StrEnum):
  ABSOLUTE = "absolute"
  RELATIVE = "relative"

class Asycont600_2:
  def __init__(self):
    self.TCP_IP   = "10.0.0.20"
    self.TCP_PORT = 4000
    self.socket   = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

  def connect(self):
      self.socket.connect((self.TCP_IP,self.TCP_PORT))

  def disconnect(self):
      self.socket.close()

  def acknowledge(self):
    xmls = '<command name="Ack" />' 
    xmls = xmls.replace("\n","")
    msg = bytes(xmls,"UTF-8")
    for i in range(6):
      self.socket.send(msg)

  def move(self, axis: str, pos: float, mtype: MOVE_TYPE = MOVE_TYPE.RELATIVE, speed: SPEED = SPEED.SLOW) -> None:
    self.acknowledge()
    if mtype == MOVE_TYPE.RELATIVE: pos += self.position(axis) 
    xmls = '<command name="MoveAbs" axis="%s" Acceleration="%s" Deceleration="%s" Velocity="%s" Direction="Auto" Position="%.3f" />' \
    %(axes[axis], axes_sped[axis][str(speed)], axes_sped[axis][str(speed)], axes_sped[axis][str(speed)], pos)
    msg = bytes(xmls,"UTF-8")
    self.socket.send(msg)

  def position(self, axis: str) -> float:
    xmls = '<state><section name="Axis %s"><query name="System Position" /></section></state>' \
    %(axes[axis]) 
    # print(xmls)
    msg = bytes(xmls,"UTF-8")
    self.socket.send(msg)
    try:
      resp = self.socket.recv(4*1024)
      pos  = float(ElementTree.fromstring(resp.decode()).find("section").find("entry").get("v1"))
      if axis == "x" or axis == "y" or axis == "z" or axis == "autslide":
        return round(pos, 3)
      elif axis == "pol":
        return round(pos, 3)
      else:
        return round(pos, 2)
    except:
      print("Read error")
      raise 

  def set_ref0(self, axis: str) -> None:
      xmls = '<command name="Reference" axis="Axis %s" NewPosition="0" />' \
      %(axes[axis])
      msg = bytes(xmls,"UTF-8")
      self.socket.send(msg)

  def stop(self, axis: str) -> None:
    xmls = '<command name="Stop" axis="Axis %s" Deceleration="%s" />' \
    %(axes[axis], axes_sped[axis]["slow"])
    msg = bytes(xmls,"UTF-8")
    self.socket.send(msg)    

    # emsg = bytes(xmls,"UTF-8")
    # self.socket.send(emsg)





# <command name="MoveAbs" axis="1" Acceleration="1" Deceleration="1" Velocity="0.1" Direction="di" Position="0" />

################################################################################
# Existing Implementation
################################################################################
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 22 16:06:02 2017

@author: thomask

Connect to server and send data
"""

import socket
import io
import time
import xml.etree.ElementTree as ET
import numpy as np


def GetXMLStartTag(s):
    tag=s[s.find("<"):s.find(">")+1]
    l=len(tag)
    if tag[1]=="?":
        tag=s[s.find("<",5):s.find(">",l)+1]
    l=len(tag)
    b=tag.find(" ")
    if b != -1:
        tag=tag[0:b+1]
    return tag[1:l-1]

def CheckXMLStopTag(s,tag):
    t="</"+tag+">"
    if s.find(t)==-1:
        return False
    return True

def AttrNew(self,root,theme,section,entry,dtype,value):
    root=ET.Element(theme)
    section=ET.SubElement(root,"section")
    section.set("name", section)
    q1=ET.SubElement(section,"entry")
    q1.set("name", entry)
    q1.set("type", dtype)
    q1.set("v1", value)    
    xmls=ET.tostring(root).decode()

def AttrAppend(self,root,theme,section,entry,dtype,value):
    section=ET.SubElement(root,"section")
    section.set("name", section)
    q1=ET.SubElement(section,"entry")
    q1.set("name", entry)
    q1.set("type", dtype)
    q1.set("v1", value)    
    xmls=ET.tostring(root).decode()


"""
Class Asycont600
"""
class Asycont600:
    
    def __init__(self,TCP_IP):
        self.TCP_IP=TCP_IP
        self.TCP_PORT=4000
        self.s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    def SyntErr(self):
        root=ET.Element("par")
        section=ET.SubElement(root,"section")
        section.set("name", "Axis " + str(1))
        q1=ET.SubElement(section,"entry")
        q1.set("name", "foo")
        q1.set("type", "string")
        q1.set("v1", str("on"))
        xmls=ET.tostring(root).decode()
        self.Send(xmls)
        
    def Connect(self):
        self.s.connect((self.TCP_IP,self.TCP_PORT))
    
    def Disconnect(self):
        self.s.close()
    
    def EchoCommandOn(self):
        root=ET.Element("par")
        section=ET.SubElement(root,"section")
        section.set("name", "Communication")
        q1=ET.SubElement(section,"entry")
        q1.set("name", "Echo")
        q1.set("type", "string")
        q1.set("size", "1")
        q1.set("v1", str("command"))
        tree=ET.ElementTree(root)
        xmls=ET.tostring(root).decode()
        self.Send(xmls)
        
    def EchoOff(self):
        root=ET.Element("par")
        section=ET.SubElement(root,"section")
        section.set("name", "Communication")
        q1=ET.SubElement(section,"entry")
        q1.set("name", "Echo")
        q1.set("type", "string")
        q1.set("size", "0")
        tree=ET.ElementTree(root)
        xmls=ET.tostring(root).decode()
        self.Send(xmls)
        
    def Send(self,msg):
        emsg=bytes(msg,"UTF-8")
        self.s.send(emsg)
        
    def Read(self):
        res=""
        res=self.s.recv(4*1024)
        #print(res.decode())
        return res

    def ReadXML(self):
        res=""
        res=self.s.recv(4*1024).decode()
        print(res)
        tag=GetXMLStartTag(res)
        print(tag)
        while CheckXMLStopTag(res,tag) == False:
            res=res+self.s.recv(4*1024).decode()
            print(res)
        return res

    def SendFile(self,fn):
        f=open(fn,"r")
        msg=f.read()
        self.Send(msg)
        f.close()

    def Send2File2(self,fn1,fn2):
        f1=open(fn1,"r")
        msg1=f1.read()
        f2=open(fn2,"r")
        msg2=f2.read()
        self.Send(msg1)
        time.sleep(0.1)
        self.Send(msg2)
        f1.close()
        f2.close()
        
    def ReceiveFile(self,fn):
        f=open(fn,"w")
        msg=self.Read()
        f.write(msg.decode("utf-8"))
        f.close()
        
    def sf(self,fn):
        self.Connect()
        self.SendFile(fn)
        self.Disconnect()

    def gf(self,fn):
        self.Connect()
        self.SendFile(fn)
        time.sleep(0.2)
        self.ReceiveFile("rec.xml")
        self.Disconnect()
        
    def SendParam(self,fn):
        root=ET.Element("command")
        root.set("name","SendParam")
        tree=ET.ElementTree(root)
        xmls=ET.tostring(root).decode()
        self.Send(xmls)
        time.sleep(0.2)
        self.ReceiveFile(fn)
        
    def SendConfig(self,fn):
        root=ET.Element("command")
        root.set("name","SendConfig")
        tree=ET.ElementTree(root)
        xmls=ET.tostring(root).decode()
        self.Send(xmls)
        time.sleep(0.2)
        self.ReceiveFile(fn)
        
    def ActPosition(self,axis):
        root=ET.Element("state")
        section=ET.SubElement(root,"section")
        section.set("name", "Axis " + str(axis))
        q1=ET.SubElement(section,"query")
        q1.set("name", "System Position")
        tree=ET.ElementTree(root)
        xmls=ET.tostring(root).decode()
        self.Send(xmls)
        try:
            r=self.Read()
        except:
            print("read error")
            raise
        try:
            tree2=ET.fromstring(r.decode())
        except:
            print("parse error")
            print(r)
        try:
            p=tree2.find("section")
            q=p.find("entry")
            fp=float(q.get("v1"))
        except:
            print("float")
            return 1E9
        return fp
        
    def ActVelocity(self,axis):
        root=ET.Element("state")
        section=ET.SubElement(root,"section")
        section.set("name", "Axis " + str(axis))
        q1=ET.SubElement(section,"query")
        q1.set("name", "Velocity")
        tree=ET.ElementTree(root)
        xmls=ET.tostring(root).decode()
        self.Send(xmls)
        r=self.Read()
        tree2=ET.fromstring(r.decode())
        p=tree2.find("section")
        q=p.find("entry")
        fp=float(q.get("v1"))
        return fp
        
    def ActStatus(self,axis):
        root=ET.Element("state")
        section=ET.SubElement(root,"section")
        section.set("name", "Axis " + str(axis))
        # query nominal position
        q1=ET.SubElement(section,"query")
        q1.set("name", "Nominal Position")
        # query position
        q1=ET.SubElement(section,"query")
        q1.set("name", "System Position")
        # position error
        q1=ET.SubElement(section,"query")
        q1.set("name", "Position Error")
        # query nominal velocity
        q2=ET.SubElement(section,"query")
        q2.set("name", "Nominal Velocity")
        # query velocity
        q2=ET.SubElement(section,"query")
        q2.set("name", "Velocity")
        tree=ET.ElementTree(root)
        xmls=ET.tostring(root).decode()
        self.Send(xmls)      
        try:
            r=self.Read()
            tree2=ET.fromstring(r.decode())
        except:
            print("parse error")
            print(r)
        p=tree2.find("section")
        qlist=p.findall("entry")
        fp=[0,0,0,0,0]
        fp[0]=float(qlist[0].get("v1"))
        fp[1]=float(qlist[1].get("v1"))
        fp[2]=float(qlist[2].get("v1"))
        fp[3]=float(qlist[3].get("v1"))
        fp[4]=float(qlist[4].get("v1"))
        return fp
        
    def Enable(self,axis):
        root=ET.Element("par")
        section=ET.SubElement(root,"section")
        section.set("name", "Axis " + str(axis))
        q1=ET.SubElement(section,"entry")
        q1.set("name", "Enabled")
        q1.set("type", "string")
        q1.set("v1", str("on"))
        xmls=ET.tostring(root).decode()
        self.Send(xmls)
            
    def Disable(self,axis):
        root=ET.Element("par")
        section=ET.SubElement(root,"section")
        section.set("name", "Axis " + str(axis))
        q1=ET.SubElement(section,"entry")
        q1.set("name", "Enabled")
        q1.set("type", "string")
        q1.set("v1", str("off"))
        xmls=ET.tostring(root).decode()
        self.Send(xmls)
            
    def MoveAbs(self,axis,acc,dec,vel,di,pos):
        root=ET.Element("command")
        root.set("name","MoveAbs")
        root.set("axis",str(axis))
        root.set("Acceleration",str(acc))
        root.set("Deceleration",str(dec))
        root.set("Velocity",str(vel))
        root.set("Direction",di)
        root.set("Position",str(pos))
        tree=ET.ElementTree(root)
        xmls=ET.tostring(root).decode()
        self.Send(xmls)
        
    def ContF(self,axis,acc,dec,vel):
        root=ET.Element("command")
        root.set("name","ContF")
        root.set("axis",str(axis))
        root.set("Acceleration",str(acc))
        root.set("Deceleration",str(dec))
        root.set("Velocity",str(vel))
        tree=ET.ElementTree(root)
        xmls=ET.tostring(root).decode()
        self.Send(xmls)
        
    def ContR(self,axis,acc,dec,vel):
        root=ET.Element("command")
        root.set("name","ContR")
        root.set("axis",str(axis))
        root.set("Acceleration",str(acc))
        root.set("Deceleration",str(dec))
        root.set("Velocity",str(vel))
        tree=ET.ElementTree(root)
        xmls=ET.tostring(root).decode()
        self.Send(xmls)
        
    def Stop(self,axis,dec):
        root=ET.Element("command")
        root.set("name","Stop")
        root.set("axis",str(axis))
        root.set("Deceleration",str(dec))
        tree=ET.ElementTree(root)
        xmls=ET.tostring(root).decode()
        self.Send(xmls)
        
    def Wait(self,axis,pos,window,delay,tmo):
        tstart=time.time()
        pact=self.ActPosition(axis)
        while abs(pos-pact) > window:
            time.sleep(0.0)
            if (time.time()-tstart) > tmo:
                return False
            try:
                pact=self.ActPosition(axis)
            except:
                pact=1E9
        time.sleep(delay)
        return True
        
    def DefTrgMode(self,mode):
        root=ET.Element("par")
        section=ET.SubElement(root,"section")
        section.set("name", "Trigger System")
        q1=ET.SubElement(section,"entry")
        q1.set("name", "Mode")
        q1.set("type", "string")
        q1.set("v1", mode)
        q2=ET.SubElement(section,"entry")
        q2.set("name", "State")
        q2.set("type", "string")
        q2.set("v1", "on")
        section=ET.SubElement(root,"section")
        section.set("name", "TR1")
        q1=ET.SubElement(section,"entry")
        q1.set("name", "Mode")
        q1.set("type", "string")
        q1.set("v1", "trgrdy")
        xmls=ET.tostring(root).decode()
        self.Send(xmls)
    
    def EnableTrg(self):
        root=ET.Element("command")
        root.set("name","EnableTrg")
        tree=ET.ElementTree(root)
        xmls=ET.tostring(root).decode()
        self.Send(xmls)
    
    def DisableTrg(self):
        root=ET.Element("command")
        root.set("name","DisableTrg")
        tree=ET.ElementTree(root)
        xmls=ET.tostring(root).decode()
        self.Send(xmls)
    
    def SetStartTrg(self,si):
        root=ET.Element("par")
        section=ET.SubElement(root,"section")
        section.set("name", "Trigger Positions")
        q1=ET.SubElement(section,"entry")
        q1.set("name", "Next")
        q1.set("type", "int")
        q1.set("v1", str(si))
        tree=ET.ElementTree(root)
        xmls=ET.tostring(root).decode()
        self.Send(xmls)
        
    def SetTrgRange(self,si1,si2):
        root=ET.Element("par")
        section=ET.SubElement(root,"section")
        section.set("name", "Trigger Positions")
        q1=ET.SubElement(section,"entry")
        q1.set("name", "Next")
        q1.set("type", "int")
        q1.set("v1", str(si1))
        q2=ET.SubElement(section,"entry")
        q2.set("name", "Last")
        q2.set("type", "int")
        q2.set("v1", str(si2))
        tree=ET.ElementTree(root)
        xmls=ET.tostring(root).decode()
        self.Send(xmls)
        
    def StatusTrg(self):
        root=ET.Element("state")
        section=ET.SubElement(root,"section")
        section.set("name", "Trigger System")
        q1=ET.SubElement(section,"query")
        q1.set("name", "State")
        tree=ET.ElementTree(root)
        xmls=ET.tostring(root).decode()
        self.Send(xmls)
        r=self.Read()
        try:
            tree2=ET.fromstring(r.decode())
        except:
            print("parse error")
            print(r)
        p=tree2.find("section")
        q=p.find("entry")
        res=q.get("v1")
        return res

    def CountTrg(self):
        root=ET.Element("par")
        section=ET.SubElement(root,"section")
        section.set("name", "Trigger Positions")
        q1=ET.SubElement(section,"query")
        q1.set("name", "Next")
        tree=ET.ElementTree(root)
        xmls=ET.tostring(root).decode()
        self.Send(xmls)
        r=self.Read()
        tree2=ET.fromstring(r.decode())
        p=tree2.find("section")
        q=p.find("entry")
        res=q.get("v1")
        return int(res)

    def GetErrors(self):
        root=ET.Element("state")
        section=ET.SubElement(root,"section")
        section.set("name", "System")
        q1=ET.SubElement(section,"query")
        q1.set("name", "Errors")
        tree=ET.ElementTree(root)
        xmls=ET.tostring(root).decode()
        self.Send(xmls)
        r=self.Read()
        tree2=ET.fromstring(r.decode())
        p=tree2.find("section")
        Q=p.find("entry")
        size=int(Q.get("size"))
        res=[]
        for i in range(size):
            vs="v"+str(i+1)
            res.append(Q.get(vs))
        return res

    def LastError(self):
        root=ET.Element("state")
        section=ET.SubElement(root,"section")
        section.set("name", "System")
        q1=ET.SubElement(section,"query")
        q1.set("name", "Last Error")
        tree=ET.ElementTree(root)
        xmls=ET.tostring(root).decode()
        self.Send(xmls)
        r=self.Read()
        tree2=ET.fromstring(r.decode())
        p=tree2.find("section")
        q=p.find("entry")
        res=q.get("v1")
        return res

    def GetRecLog(self):
        root=ET.Element("state")
        section=ET.SubElement(root,"section")
        section.set("name", "System")
        q1=ET.SubElement(section,"query")
        q1.set("name", "Receive Log")
        tree=ET.ElementTree(root)
        xmls=ET.tostring(root).decode()
        self.Send(xmls)
        r=self.Read()
        tree2=ET.fromstring(r.decode())
        p=tree2.find("section")
        Q=p.find("entry")
        size=int(Q.get("size"))
        res=[]
        for i in range(size):
            vs="v"+str(i+1)
            res.append(Q.get(vs))
        return res

    def GetRecLogRaw(self):
        root=ET.Element("state")
        section=ET.SubElement(root,"section")
        section.set("name", "System")
        q1=ET.SubElement(section,"query")
        q1.set("name", "Receive Log")
        tree=ET.ElementTree(root)
        xmls=ET.tostring(root).decode()
        self.Send(xmls)
        r=self.Read()
        return r

    def GetSendLog(self):
        root=ET.Element("state")
        section=ET.SubElement(root,"section")
        section.set("name", "System")
        q1=ET.SubElement(section,"query")
        q1.set("name", "Send Log")
        tree=ET.ElementTree(root)
        xmls=ET.tostring(root).decode()
        self.Send(xmls)
        r=self.Read()
        tree2=ET.fromstring(r.decode())
        p=tree2.find("section")
        Q=p.find("entry")
        size=int(Q.get("size"))
        res=[]
        for i in range(size):
            vs="v"+str(i+1)
            res.append(Q.get(vs))
        return res

    def Trg(self):
        root=ET.Element("command")
        root.set("name","TriggerTRSequence")
        tree=ET.ElementTree(root)
        xmls=ET.tostring(root).decode()
        self.Send(xmls)

    def DefTRTest(self,res,N,tmo):
        root=ET.Element("par")
        section=ET.SubElement(root,"section")
        section.set("name", "Trigger System")
        q1=ET.SubElement(section,"entry")
        q1.set("name", "Mode")
        q1.set("type", "string")
        q1.set("v1", "measure")
        q2=ET.SubElement(section,"entry")
        q2.set("name", "State")
        q2.set("type", "string")
        q2.set("v1", "on")
        section=ET.SubElement(root,"section")
        section.set("name", "TR1")
        q1=ET.SubElement(section,"entry")
        q1.set("name", "Mode")
        q1.set("type", "string")
        q1.set("v1", "measure")
        section=ET.SubElement(root,"section")
        section.set("name", "TR1/TR Test")
        q1=ET.SubElement(section,"entry")
        q1.set("name", "N")
        q1.set("type", "int")
        q1.set("v1", str(N))
        q1=ET.SubElement(section,"entry")
        q1.set("name", "Timeout")
        q1.set("type", "float")
        q1.set("v1", str(tmo))
        xmls=ET.tostring(root).decode()
        self.Send(xmls)
            
    def InitTRTest(self):
        root=ET.Element("command")
        root.set("name","InitTRTest")
        tree=ET.ElementTree(root)
        xmls=ET.tostring(root).decode()
        self.Send(xmls)

    def StatusTRMeas(self):
        root=ET.Element("state")
        section=ET.SubElement(root,"section")
        section.set("name", "Trigger System")
        q1=ET.SubElement(section,"query")
        q1.set("name", "TR Meas")
        tree=ET.ElementTree(root)
        xmls=ET.tostring(root).decode()
        self.Send(xmls)
        r=self.Read()
        try:
            tree2=ET.fromstring(r.decode())
        except:
            print(r)
        p=tree2.find("section")
        q=p.find("entry")
        res=q.get("v1")
        return res
    
    def ResultTRMeas(self):
        root=ET.Element("par")
        section=ET.SubElement(root,"section")
        section.set("name", "TR1/TR Test")
        q1=ET.SubElement(section,"query")
        q1.set("name", "Result")
        tree=ET.ElementTree(root)
        xmls=ET.tostring(root).decode()
        self.Send(xmls)
        r=self.ReadXML()
        tree2=ET.fromstring(r)
        p=tree2.find("section")
        Q=p.find("entry")
        size=int(Q.get("size"))
        res=[]
        for i in range(size):
            vs="v"+str(i+1)
            res.append(float(Q.get(vs)))
        return res
    
    def Load(self,fn):
        root=ET.Element("command")
        root.set("name","Load")
        root.set("file",fn)
        tree=ET.ElementTree(root)
        xmls=ET.tostring(root).decode()
        self.Send(xmls)
        
    def GetConfig(self):
        root=ET.Element("command")
        root.set("name","SendConfig")
        tree=ET.ElementTree(root)
        xmls=ET.tostring(root).decode()
        self.Send(xmls)
        msg=self.ReadXML()
        return msg
        
    def SetTRState(self,tr,state):
        root=ET.Element("command")
        c="StateTR" + str(tr)
        root.set("name",c)
        root.set("State",str(state))
        tree=ET.ElementTree(root)
        xmls=ET.tostring(root).decode()
        self.Send(xmls)

    def test(self):
        X=np.linspace(1,100,100)
        for x in X:
            t=time.time();
            p=self.ActPosition(2)
            delta=time.time()-t
            print(t,";     ",p)
            #time.sleep(0.1)
        print("done")
        
