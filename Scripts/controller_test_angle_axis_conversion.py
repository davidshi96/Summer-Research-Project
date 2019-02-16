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
    
targetPosition1 = [0]*6
rawPosition = []

i=0
if interval:
    while(i<1):
        start = time.time()
        txt = ""
        txt2 = ""
        for each in v.devices["controller_1"].get_pose_axis():
            txt += "%.2f" % each
            txt += " "
        rawPosition = re.findall(r"[-+]?\d*\.\d+|\d+", str(txt))
        targetPosition1[0] = round(float(rawPosition[0]) - 0.8, 2) #X
        targetPosition1[1] = round(-float(rawPosition[2]) + 0.2, 2) #Z axis for vr, y axis for robot
        targetPosition1[2] = round(float(rawPosition[1]) - 1, 2)#Y axis for vr, Z axis for robot
        
        rx = round(float(rawPosition[3])*float(rawPosition[4]),2)
        
        rx = rx - math.pi/2
        if (rx > -1.5*math.pi) & (rx < -math.pi):
            rx = rx+2*math.pi
        
        targetPosition1[3]= round(rx,2)
        targetPosition1[4]=-round(float(rawPosition[3])*float(rawPosition[6]),2)
        targetPosition1[5]=round(float(rawPosition[3])*float(rawPosition[5]),2)
        
        print("\r", targetPosition1, end = "")
        
        for each in v.devices["controller_1"].get_pose_mat():
            txt2 += "%.2f" % each
            txt2 += " "
        matrix = re.findall(r"[-+]?\d*\.\d+|\d+", str(txt2))
        
        
        print(matrix, "\n")
        
        
        i = i+ 1