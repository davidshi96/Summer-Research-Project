# -*- coding: utf-8 -*-
"""
Created on Wed Dec 13 10:50:29 2017

@author: yshi321
"""
import socket
import time
HOST = '192.168.1.10' # The remote host
PORT = 30002 # The same port as used by the server
print('Starting Program')
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

#first number = base angle in rad, -1 is about straight ahead
#second number = shoulder angle, about -3 is flat
#third number = elbow angle
#4-6 number = 3 wrist angles

#position numbers:
#1: x axis (direction labelled on robot)
#2: y axis (direction labelled on robot)
#3: z axis (+ve is up)
#4: change angle of hand up or down while still pointing at same thing
#5: change angle of hand, keeping it in same spot but pointing at different thing
#6: rotate wrist

# so now i need to be able to somehow map the vive remote location into 3D coordiates and map it onto the 
# 3D space coordinates of the arm and continuously read the 3D coordinates of the vive remote and continuously
# send commands to the arm to move the arm to the specified location
X = -0.4
Y = -0.4
count = 0

while count < 10:
    
    Z = 0
    RX = 3
    RY = 1
    RZ = 0
    
#    X, Y= input("please enter the X, Y, Z axis values (seperated by a space) \n").split()
#    X = input("please enter a X axis input") #-0.4
#    Y = input("please enter a Y axis input") #-0.4
#    Z = input("please enter a Z axis input") #0.2
# rx = 3 ry = 1 rz = 0
    
    s.sendto(("movel(p["+ X + ", " + Y + ", " + Z + ", " + RX + ", " + RY + ", " + RZ + "], a=1.3962634015954636, v=0.2)"+ "\n").encode(), (HOST, PORT))
    time.sleep(.01)

    count = count + 1
#data = s.recv(1024)
s.close()
#print ("Received", repr(data))