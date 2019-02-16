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


HOST = "192.168.1.6" # The remote host
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

lowerLimit = float(0.15)
upperLimit = float(0.55)

i=0
sample=100

rxList = [0]*sample
ryList = [0]*sample
rzList = [0]*sample

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
    for each in v.devices["controller_1"].get_pose_euler():
        txt += "%.2f" % each
        txt += " "
    targetPosition1 = re.findall(r"[-+]?\d*\.\d+|\d+", str(txt))
    
    X = -(float(targetPosition1[2]) + 2.3)
    
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
    Y = - (float(targetPosition1[0]) - .3)
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

    if Z > 0.85:
        Z = 0.85
    
    # next 3 numbers: 

    #converting pitch roll and yaw into RX RY AND RZ values 
    
    pitchMatrix = np.matrix([
    [math.cos(float(targetPosition1[3])), 0, math.sin(float(targetPosition1[3]))],
    [0, 1, 0],
    [-math.sin(float(targetPosition1[3])), 0, math.cos(float(targetPosition1[3]))]
    ])
    
    rollMatrix = np.matrix([
    [1, 0, 0],
    [0, math.cos(float(targetPosition1[4])), -math.sin(float(targetPosition1[4]))],
    [0, math.sin(float(targetPosition1[4])), math.cos(float(targetPosition1[4]))]
    ])

    yawMatrix = np.matrix([
    [math.cos(float(targetPosition1[5])), -math.sin(float(targetPosition1[5])), 0],
    [math.sin(float(targetPosition1[5])), math.cos(float(targetPosition1[5])), 0],
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
        #print('\r', posePosition, end='')
        
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
        c.sendto(("(" + str(X) + "," + str(Y) + "," + str(Z) + "," + str(3) + "," + str(1) + "," + str(0) + ")").encode(),(CLIENT, PORT));
        
        #printing posePosition and values sent to robot

    except socket.error as socketerror:
        print("Error")
 
c.close()
s.close()
print("Program finish")