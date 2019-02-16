# -*- coding: utf-8 -*-
"""
Created on Wed Dec 20 15:05:53 2017

@author: yshi321
"""

# Echo client program
import socket
import time
HOST = "192.168.1.2" # The remote host
CLIENT = "192.168.1.10"
PORT = 30000 # The same port as used by the server
print("Starting Program")
count = 0

#the pc is the server and the arm is the client

print("Established Connection")
X = -0.4
Y = -0.4
Z = 0
RX = 3
RY = 1
RZ = 0

while (count < 1000):
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT)) # Bind to the port 
    s.listen(5) # Now wait for client connection.
    c, addr = s.accept() # Establish connection with client.
    print("Established Connection")

    try:
        #c.sendto(("movel(p["+ str(X) + ", " + str(Y) + ", " + str(Z) + ", " + str(RX) + ", " + str(RY) + ", " + str(RZ) + "], a=1.3962634015954636, v=0.2)"+ "\n").encode(), (CLIENT, PORT))
        c.sendto("sending".encode(),(CLIENT, PORT));
        print("sending message")
        msg = c.recv(1024)        
        time.sleep(1)
        if 'waiting' in str(msg):
            count = count + 1
            print("The count is: ", count)
            time.sleep(0.5)
            print("\n")
            time.sleep(0.5)
            c.sendto("(0.1,0.1,0.1)".encode(),(CLIENT, PORT));
            print("sent message")
            
    except socket.error as socketerror:
        print(count)
 
c.close()
s.close()
print("Program finish")