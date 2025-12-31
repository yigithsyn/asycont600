
__version__ = "0.8.1"

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

  def pos_low_lim(self, axis: str) -> float:
    xmls = '<par><section name="Axis %s"><query name="Position" /></section></par>' \
    %(axes[axis]) 
    # print(xmls)
    msg = bytes(xmls,"UTF-8")
    self.socket.send(msg)
    try:
      resp = self.socket.recv(4*1024)
      pos  = float(ElementTree.fromstring(resp.decode()).find("section").find("entry").get("min"))
      if axis == "x" or axis == "y" or axis == "z" or axis == "autslide":
        return round(pos, 3)
      elif axis == "pol":
        return round(pos, 3)
      else:
        return round(pos, 2)
    except:
      print("Read error")
      raise 

  def set_reference(self, axis: str) -> None:
    xmls = '<command name="Reference" axis="Axis %s" NewPosition="0" />' \
    %(axes[axis])
    msg = bytes(xmls,"UTF-8")
    self.socket.send(msg)

  def set_offset(self, axis: str, offset: float) -> None:
    xmls = '<command name="Reference" axis="Axis %s" Offset="%.3f" />' \
    %(axes[axis], offset)
    msg = bytes(xmls,"UTF-8")
    self.socket.send(msg)

  def stop(self, axis: str) -> None:
    xmls = '<command name="Stop" axis="Axis %s" Deceleration="%s" />' \
    %(axes[axis], axes_sped[axis]["slow"])
    msg = bytes(xmls,"UTF-8")
    self.socket.send(msg)    
