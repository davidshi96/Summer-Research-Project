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
    
targetPosition1 = [0,0,0,0,0,0,0]
rawPosition = []

i=0
if interval:
    while(True):
        start = time.time()
        txt = ""
        txt2 = ""
        for each in v.devices["controller_1"].get_pose_quaternion():
            txt += "%.2f" % each
            txt += " "
        rawPosition = re.findall(r"[-+]?\d*\.\d+|\d+", str(txt))
        targetPosition1[0] = round(float(rawPosition[0]) - 0.8, 2) #X
        targetPosition1[1] = round(-float(rawPosition[2]) + 0.2, 2) #Z axis for vr, y axis for robot
        targetPosition1[2] = round(float(rawPosition[1]) - 1, 2)#Y axis for vr, Z axis for robot
        qw=float(rawPosition[3])
        qx=float(rawPosition[4])
        qy=float(rawPosition[6])
        qz=float(rawPosition[5])
        
        
        sqw = qw*qw
        sqx = qx*qx
        sqy = qy*qy
        sqz = qz*qz
        
        unit = sqw + sqx + sqy + sqz
        T = qx*qy + qz*qw
        
        
        #yaw = roll, roll = pitch, pitch = yaw
        if (T > 0.4999*unit):
            roll = 2*math.atan2(qx,qw)
            yaw = math.pi/2
            pitch = 0
        elif (T < -0.4999*unit):
            roll = -2*math.atan2(qx,qw)
            yaw = -math.pi/2
            pitch = 0
        else:
            roll = math.atan2(2*qy*qw - 2*qx*qz, sqx - sqy - sqz + sqw)
            yaw = math.asin(2*T/unit)
            pitch = math.atan2(2*qx*qw - 2*qy*qz, -sqx + sqy - sqz + sqw)
        
        #recalibrating
        
        pitch = pitch - math.pi/2
        if (pitch > -1.5*math.pi) & (pitch < -math.pi):
            pitch = pitch+2*math.pi
                
        #converting pitch roll and yaw into RX RY AND RZ values 
        
        pitchMatrix = np.matrix([
        [math.cos(pitch), 0, math.sin(pitch)],
        [0, 1, 0],
        [-math.sin(pitch), 0, math.cos(pitch)]
        ])
        
        rollMatrix = np.matrix([
        [1, 0, 0],
        [0, math.cos(roll), -math.sin(roll)],
        [0, math.sin(roll), math.cos(roll)]
        ])
    
        yawMatrix = np.matrix([
        [math.cos(yaw), -math.sin(yaw), 0],
        [math.sin(yaw), math.cos(yaw), 0],
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
        
        
        targetPosition1[3] = round(roll, 2)
        targetPosition1[4] = round(pitch, 2)
        targetPosition1[5] = round(yaw, 2)                   
        
        print("\r" , targetPosition1 , end="")