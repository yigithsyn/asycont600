import sys
import pytest
import time 

sys.path.append('./src')
import asycont600
from asycont600 import Asycont600
from asycont600 import Asycont600_2

cont = Asycont600_2()
cont.connect()
# cont.move("y", -1)
# cont.move("y", 0, asycont600.MOVE_TYPE.ABSOLUTE)
# cont.move("y", -2, "relative", "fast")
print(cont.position("y"))
cont.pos_low_lim("y")
# cont.set_ref0("y")
cont.disconnect()

# import numpy as np



# velX=0.4
# accX=0.5

# velY=1
# accY=1

# c=Asycont600("10.0.0.20")

# c.Connect()

# print("x","y","z",sep=";")
# X=np.linspace(-2,2,41)
# Y=np.linspace(-2,2,41)
# i = 0
# for posX in X:
#     c.MoveAbs(1,accX,accX,velX,"Auto",posX)
#     c.Wait(1,posX,0.0001,1.0,45)
    
#     for posY in Y:
#         if(i%2 == 0):
#             c.MoveAbs(2,accY,accY,velY,"Auto",posY)
#             c.Wait(2,posY,0.0001,1.0,45) 
#         else:
#             c.MoveAbs(2,accY,accY,velY,"Auto",-posY)
#             c.Wait(2,-posY,0.0001,1.0,45)  
        
#         time.sleep(3)
#         x=c.ActPosition(1)
#         y=c.ActPosition(2)
#         z=c.ActPosition(3)
#         print(x,y,z,sep=";") 
#     i = i + 1

# c.Disconnect()