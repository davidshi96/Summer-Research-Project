#import openvr
import triad_openvr
import time
import math
import sys
import re
import numpy as np

v = triad_openvr.triad_openvr()
v.print_discovered_objects()

if len(sys.argv) == 1:
    interval = 1/250
elif len(sys.argv) == 2:
    interval = 1/float(sys.argv[0])
else:
    print("Invalid number of arguments")
    interval = False
    
targetPosition1 = [0,0,0,'0','0','0']
rawPosition = []


sample = 100
rxList = [0]*sample
ryList = [0]*sample
rzList = [0]*sample

i=0
if interval:
    while(True):
        start = time.time()
        txt = ""
        txt2 = ""
        for each in v.devices["controller_1"].get_pose_euler():
            txt += "%.2f" % each
            txt += " "
        rawPosition = re.findall(r"[-+]?\d*\.\d+|\d+", str(txt))
        targetPosition1[0] = round(-(float(rawPosition[2]) + 2.3), 2)
        targetPosition1[1] = round(-(float(rawPosition[0]) - .3), 2)
        targetPosition1[2] = round(float(rawPosition[1]) + 1.6, 2)
       
        pitchMatrix = np.matrix([
        [math.cos(float(rawPosition[3])), 0, math.sin(float(rawPosition[3]))],
        [0, 1, 0],
        [-math.sin(float(rawPosition[3])), 0, math.cos(float(rawPosition[3]))]
        ])
        
        rollMatrix = np.matrix([
        [1, 0, 0],
        [0, math.cos(float(rawPosition[4])), -math.sin(float(rawPosition[4]))],
        [0, math.sin(float(rawPosition[4])), math.cos(float(rawPosition[4]))]
        ])
    
        yawMatrix = np.matrix([
        [math.cos(float(rawPosition[5])), -math.sin(float(rawPosition[5])), 0],
        [math.sin(float(rawPosition[5])), math.cos(float(rawPosition[5])), 0],
        [0, 0, 1]
        ])
        
        
        R = yawMatrix * pitchMatrix * rollMatrix
        
        theta = math.acos(((R[0, 0] + R[1, 1] + R[2, 2]) - 1) / 2)
        
        if theta != 0 :
            multi = 1 / (2 * math.sin(theta))
            rx = multi * (R[2, 1] - R[1, 2]) * theta
            ry = multi * (R[0, 2] - R[2, 0]) * theta
            rz = multi * (R[1, 0] - R[0, 1]) * theta
        elif theta == 0:
            rx = 0
            ry = 0
            rz = 0
    
        #applying running average filter to the angles
        if i < sample:
            rxList[i]=float(rx)
            ryList[i]=float(ry)
            rzList[i]=float(rz)
                
            if i==(sample-1):
                i=0
            else:
                i=i+1
    
        targetPosition1[3] = round(sum(rxList)/sample, 2)
        targetPosition1[4] = round(sum(ryList)/sample, 2)
        targetPosition1[5] = round(sum(rzList)/sample, 2)
    
        
        
        
#        targetPosition1[0] = round(-(float(targetPosition1[0])- .5), 2)
#        temp = targetPosition1[1]
#        targetPosition1[1] = round((-float(targetPosition1[2]) - 2), 2)
#        targetPosition1[2] = round(float(temp) + 1.5, 2)
#        
#        for each in v.devices["controller_2"].get_pose_euler():
#            txt2 += "%.4f" % each
#            txt2 += " "
#        targetPosition2 = re.findall(r"[-+]?\d*\.\d+|\d+", str(txt2))

        
        
        
        
        print("\r" , targetPosition1 , end="")