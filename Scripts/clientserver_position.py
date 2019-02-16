# -*- coding: utf-8 -*-
"""
Created on Wed Dec 20 15:05:53 2017

@author: yshi321
"""

# Echo client program
import socket
import time
import re
HOST = "192.168.1.2" # The remote host
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

posePosition = []
#jointPosition = []
while (count < 1000):
    print("count is ", count)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT)) # Bind to the port 
    s.listen(5) # Now wait for client connection.
    c, addr = s.accept() # Establish connection with client.
    print("Established Connection")
    targetPosition = [0.4, 0.4, 0, 3, 1, 0]
    try:
        msg = c.recv(1024)
        posePosition = re.findall(r"[-+]?\d*\.\d+|\d+", str(msg))
        print("Pose : ", posePosition)
        #msg = c.recv(1024)
        #jointPosition = re.findall(r"[-+]?\d*\.\d+|\d+", str(msg))
        #print("Joint : ", jointPosition)
        #msg = c.recv(1024)
        #c.sendto(("movel(p["+ str(X) + ", " + str(Y) + ", " + str(Z) + ", " + str(RX) + ", " + str(RY) + ", " + str(RZ) + "], a=1.3962634015954636, v=0.2)"+ "\n").encode(), (CLIENT, PORT))    
        #time.sleep(0.1)
        #if 'asking_for_data' in str(msg):
        count = count + 1
        X = targetPosition[0] 
        Y = targetPosition[1] 
        Z = targetPosition[2]
        rx = targetPosition[3]
        ry = targetPosition[4]
        rz = targetPosition[5]
        #time.sleep(0.5)
        c.sendto(("(" + str(X) + "," + str(Y) + "," + str(Z) + "," + str(rx) + "," + str(ry) + "," + str(rz) + ")").encode(),(CLIENT, PORT));

    except socket.error as socketerror:
        print(count)
 
c.close()
s.close()
print("Program finish")