# -*- coding: utf-8 -*-
"""
Created on Wed Dec 20 15:05:53 2017

@author: yshi321
"""

import triad_openvr
#import time
import sys
import socket
import re
import math
import numpy as np


HOST = "192.168.1.2" # IP address of the PC (host)
CLIENT = "192.168.1.10" # IP address of the robot (Client)
PORT = 30000 # The same port should be used for both the robot and the pc
print("Starting Program")


#initialising variables to be sent to the robot
x = 0
y = 0
z = 0
rx = 0
ry = 0
rz = 0

#printing discoverable objects
v = triad_openvr.triad_openvr()
v.print_discovered_objects()

#posePosition is the position of the robot arm
posePosition = [0,0,0,0,0,0]

#targetPosition is the position of the vive controller, the robot will try to achieve this position
targetPosition = [0, 0, 0, 0, 0, 0]

#software limits for robot arm
lowerLimit = float(0.1)
upperLimit = float(0.55)

#setting up running average
i=0
sample=2

#initial starting position
xList = [0.27]*sample
yList = [0.27]*sample
zList = [0.06]*sample
rxList = [-1.33]*sample
ryList = [0.17]*sample
rzList = [0.02]*sample

#the socket is no longer opening and closing constantly which means that 
#the program on the touchpad needs to be running first then run this

#open the socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT)) # Bind to the port 
s.listen(5) # Now wait for client connection.
c, addr = s.accept() # Establish connection with client.

#the user has about 5 seconds between clicking start program and getting the 
#controller in position
print("Established Connection")

while (True):

    #reading controller coordinates
    txt = ""
    for each in v.devices["controller_1"].get_pose_quaternion():
        txt += "%.2f" % each
        txt += " "
    targetPosition = re.findall(r"[-+]?\d*\.\d+|\d+", str(txt))
    
    #X axis is left and right to the "work table"
    X = float(targetPosition[0]) - 0.8
    
    if (X < lowerLimit) & (X >= 0):
        X = lowerLimit
    elif (X < 0) & (X > -lowerLimit):
        X = -lowerLimit
    elif X > upperLimit:
        X = upperLimit
    elif X < -upperLimit:
        X = -upperLimit        
        

     
    #Y axis is forward and back relative to the "work table"
    #this reads the 3rd number as that number represents forward and back movement
    Y = -float(targetPosition[2]) + 0.2
        
    if (Y < lowerLimit) & (Y >= 0):
        Y = lowerLimit
    elif (Y < 0) & (Y > -lowerLimit):
        Y = -lowerLimit
    elif Y > upperLimit:
        Y = upperLimit
    elif Y < -upperLimit:
        Y = -upperLimit
  
    #Z axis is up and down
    #it is the second number because it is up and down movement
    #the vive axis has y and z swapped around
    Z = float(targetPosition[1]) - 1


    #this is the up and down limit, it changes depending on the distance the arm is away
    #from the center, may need to be reworked a bit
    if Z > 1.1-math.sqrt(X*X+Y*Y):
        Z = 1.1-math.sqrt(X*X+Y*Y)
        
        
    # next 4 numbers: 
    qw=float(targetPosition[3])
    qx=float(targetPosition[4])
    qy=float(targetPosition[6])
    qz=float(targetPosition[5])
    
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

    #applying running average filter to the angles
#    if i < sample:
#        rxList[i]=float(rx)
#        ryList[i]=float(ry)
#        rzList[i]=float(rz)
#            
#        if i==(sample-1):
#            i=0
#        else:
#            i=i+1
#
#    rx = round(sum(rxList)/sample, 2)
#    ry = round(sum(ryList)/sample, 2)
#    rz = round(sum(rzList)/sample, 2)
    
#    #applying running average filter to the angles
#    if i < sample:
#        xList[i] = X
#        yList[i] = Y
#        zList[i]= Z
#        rxList[i]=r_x
#        ryList[i]=r_y
#        rzList[i]=r_z
#            
#        if i==(sample-1):
#            i=0
#        else:
#            i=i+1
#
#
#    x = sum(xList)/sample
#    y = sum(yList)/sample
#    z = sum(zList)/sample
#    rx = sum(rxList)/sample
#    ry = sum(ryList)/sample
#    rz = sum(rzList)/sample

    try:
        
        #sending target coordinates to robot
        #c.sendto(("(" + str(X) + "," + str(Y) + "," + str(Z) + "," + str(r_x) + "," + str(r_y) + "," + str(r_z) + ")").encode(),(CLIENT, PORT));
        c.sendto(("(" + str(X) + "," + str(Y) + "," + str(Z) + "," + str(rx) + "," + str(ry) + "," + str(rz) + ")").encode(),(CLIENT, PORT));

        
        #reading the message received from the robot arm
        msg = c.recv(1024)
        posePosition = re.findall(r"[-+]?\d*\.\d+|\d+", str(msg))
        #printing message
        print('\r', posePosition, end='')
        

    except socket.error as socketerror:
        print('\r', "------------------------------Error------------------------------", end='')
 
c.close()
s.close()
print("Program finish")