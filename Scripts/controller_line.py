# -*- coding: utf-8 -*-
"""
Created on Wed Dec 20 15:05:53 2017

@author: yshi321
"""

import triad_openvr
import time
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
x = 0.27
y = 0.27
z = 0.06
rx = -1.33
ry = 0.17
rz = 0.02

count = 0

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

while (count < 1000):
    x = x + 0.00015
    y = y + 0.00015
    z = z + 0.00015
    
    count = count + 1
    try:
        
        #sending target coordinates to robot
        #c.sendto(("(" + str(X/scale) + "," + str(Y/scale) + "," + str(Z/scale) + "," + str(r_x) + "," + str(r_y) + "," + str(r_z) + ")").encode(),(CLIENT, PORT));
        c.sendto(("(" + str(x) + "," + str(y) + "," + str(z) + "," + str(rx) + "," + str(ry) + "," + str(rz) + ")").encode(),(CLIENT, PORT));

        
        #reading the message received from the robot arm
        #msg = c.recv(1024)
        #posePosition = re.findall(r"[-+]?\d*\.\d+|\d+", str(msg))
        #printing message
        #print('\r', posePosition, end='')
        time.sleep(0.008)

    except socket.error as socketerror:
        print('\r', "------------------------------Error------------------------------", end='')

    
c.close()
s.close()
print("Program finish")