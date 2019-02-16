#import openvr
from __future__ import print_function
import triad_openvr
import time
import math
import sys
import re


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
    while(True):
        trigger, trackpad_x, trackpad_y, menu_button, grip_button, trackpad_pressed, trackpad_touched = v.read_right_controller()
        start = time.time()
        txt = ""
        txt2 = ""
        for each in v.devices["controller_1"].get_pose_axis():
            txt += "%.2f" % each
            txt += " "
        rawPosition = re.findall(r"[-+]?\d*\.\d+|\d+", str(txt))
        targetPosition1[0] = round(float(rawPosition[0]), 2) #X
        targetPosition1[1] = round(-float(rawPosition[2]), 2) #Z axis for vr, y axis for robot
        targetPosition1[2] = round(float(rawPosition[1]) - 0.8, 2)#Y axis for vr, Z axis for robot
        
        rx = float(rawPosition[3])*float(rawPosition[4])
        
        rx = rx - math.pi/2
        if (rx > -1.5*math.pi) & (rx < -math.pi):
            rx = rx+2*math.pi
        
        targetPosition1[3]= round(rx,2)
        targetPosition1[4]= -round(float(rawPosition[3])*float(rawPosition[5]),2)

        rz = float(rawPosition[3])*float(rawPosition[6])
        
#        rz = rz + math.pi/2
#        if (rz < 1.5*math.pi) & (rz > math.pi):
#            rz = rz - 2*math.pi


        targetPosition1[5]= round(rz,2)
        
        if (trigger > 0.0) | (menu_button == True) | (grip_button == True):
            print("\r", round(trigger,2), round(trackpad_x,2), round(trackpad_y,2), menu_button, grip_button, trackpad_pressed, trackpad_touched, end = "")
        else:
            print("\r", targetPosition1, end = "")
        
#        for each in v.devices["controller_1"].get_pose_mat():
#            txt2 += "%.2f" % each
#            txt2 += " "
#        matrix = re.findall(r"[-+]?\d*\.\d+|\d+", str(txt2))
#        
#        
#        print(matrix, "\n")
#        
#        
#        i = i+ 1
