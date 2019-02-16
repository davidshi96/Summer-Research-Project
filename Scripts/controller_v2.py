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


HOST = "192.168.1.3" # The remote host
CLIENT = "192.168.1.10"
PORT = 30000 # The same port as used by the server
print("Starting Program")
count = 0

#the pc is the server and the arm is the client

X = 0
Y = 0
Z = 0
RX = 0
RY = 0
RZ = 0

v = triad_openvr.triad_openvr()
v.print_discovered_objects()

posePosition = []
targetPosition1 = [0, 0, 0, 0, 0, 0]

lowerLimit = float(0.1)
upperLimit = float(0.55)

i=0
sample=25

rxList = [0.04]*sample
ryList = [-3.12]*sample
rzList = [-0.30]*sample

#the socket is no longer opening and closing constantly which means that 
#the program on the touchpad needs to be running first then run this

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT)) # Bind to the port 
s.listen(5) # Now wait for client connection.
c, addr = s.accept() # Establish connection with client.
print("Established Connection")


while (True):

    #reading controller coordinates
    txt = ""
    for each in v.devices["controller_1"].get_pose_quaternion():
        txt += "%.2f" % each
        txt += " "
    targetPosition1 = re.findall(r"[-+]?\d*\.\d+|\d+", str(txt))
    
    X = (float(targetPosition1[2]) + 2.3)
    
    if (X < lowerLimit) & (X >= 0):
        X = lowerLimit
    elif (X < 0) & (X > -lowerLimit):
        X = -lowerLimit
    elif X > upperLimit:
        X = upperLimit
    elif X < -upperLimit:
        X = -upperLimit
#        
    #Y axis is up and down
    Y = (float(targetPosition1[0]) + .3)
#        
    if (Y < lowerLimit) & (Y >= 0):
        Y = lowerLimit
    elif (Y < 0) & (Y > -lowerLimit):
        Y = -lowerLimit
    elif Y > upperLimit:
        Y = upperLimit
    elif Y < -upperLimit:
        Y = -upperLimit
#        
    #Z axis is forward and back
    Z = float(targetPosition1[1]) + 1.6

    if Z > 1.1-math.sqrt(X*X+Y*Y):
        Z = 1.1-math.sqrt(X*X+Y*Y)
    # next 3 numbers: 
    qw=float(targetPosition1[3])
    qx=float(targetPosition1[4])
    qy=float(targetPosition1[5])
    qz=float(targetPosition1[6])
    
    angle = 2*math.acos(qw)
    x = qx / math.sqrt(1-qw*qw)
    y = qy / math.sqrt(1-qw*qw)
    z = qz / math.sqrt(1-qw*qw)
    
    T = qx*qy + qz*qw
    if (T > 0.499):
        yaw = 2*math.atan2(qx,qw)
        roll = math.pi/2
        pitch = 0
    elif (T < -0.499):
        yaw = -2*math.atan2(qx,qw)
        roll = -math.pi/2
        pitch = 0
    else:
        yaw = math.atan2(2*qy*qw - 2*qx*qz, 1- 2*qy*qy - 2*qz*qz)
        roll = math.asin(2*T)
        pitch = math.atan2(2*qx*qw - 2*qy*qz,1-2*qx*qx-2*qz*qz)
    
    #recalibrating
    yaw = -math.pi + yaw
    if yaw < -math.pi:
        yaw = yaw + 2*math.pi
    
    pitch = pitch - math.pi/2
    if (pitch > -1.5*math.pi) & (pitch < -math.pi):
        pitch = pitch+2*math.pi
            
    #converting pitch roll and yaw into RX RY AND RZ values 
    
    pitchMatrix = np.matrix([
    [math.cos(-pitch), 0, math.sin(-pitch)],
    [0, 1, 0],
    [-math.sin(-pitch), 0, math.cos(-pitch)]
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
    if i < sample:
        rxList[i]=float(rx)
        ryList[i]=float(ry)
        rzList[i]=float(rz)
            
        if i==(sample-1):
            i=0
        else:
            i=i+1

    rx = round(sum(rxList)/sample, 2)
    ry = round(sum(ryList)/sample, 2)
    rz = round(sum(rzList)/sample, 2)

    try:
        msg = c.recv(1024)
        posePosition = re.findall(r"[-+]?\d*\.\d+|\d+", str(msg))
#        print('\r', posePosition, end='')
        
        #msg = c.recv(1024)
        #jointPosition = re.findall(r"[-+]?\d*\.\d+|\d+", str(msg))
        #print("Joint : ", jointPosition)
        #msg = c.recv(1024)
        #c.sendto(("movel(p["+ str(X) + ", " + str(Y) + ", " + str(Z) + ", " + str(RX) + ", " + str(RY) + ", " + str(RZ) + "], a=1.3962634015954636, v=0.2)"+ "\n").encode(), (CLIENT, PORT))    
        #time.sleep(0.1)
        #if 'asking_for_data' in str(msg):
        #    count = count + 1
        

        
        #next 3 numbers that need to be sent are the joint angles of the arm
        #these joint angles correspond to the pitch, yaw and roll
        
        
        #RX is the pitch
        #pitch from the targetPosition works where it is 0 at rest (horizontal)
        #rx = rx - float(posePosition[3])
        # ry is the roll
        # roll works similar to pitch where it is 0 at rest position (horizontal)
        #ry = ry - float(posePosition[4])
        # rz is the yaw 
        # yaw is a bit weird, were it 0 and goes to +- 90 on either side and then mirrors itself 
        # on the other side, so it goes -0 <- -90 <- 0 -> 90 -> 0
        #rz = rz - float(posePosition[5])
        
        # may need to have software limits on where the arm can go, but this comes from testing
        
        
        #time.sleep(0.5)
        #c.sendto(("(" + str(X) + "," + str(Y) + "," + str(Z) + "," + str(rx) + "," + str(ry) + "," + str(rz) +  ")").encode(),(CLIENT, PORT));
        c.sendto(("(" + str(X) + "," + str(Y) + "," + str(Z) + "," + str(rx) + "," + str(ry) + "," + str(rz) + ")").encode(),(CLIENT, PORT));
        
        #printing posePosition and values sent to robot

    except socket.error as socketerror:
        print("Error")
 
c.close()
s.close()
print("Program finish")