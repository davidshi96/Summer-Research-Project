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
import motor


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



#setting up running average
i=0
sample=10

#scale for movement
scale = 1



#initial starting position
xList = [0.27*scale]*sample
yList = [0.27*scale]*sample
zList = [0.06*scale]*sample
rxList = [-1.33]*sample
ryList = [0.17]*sample
rzList = [0.02]*sample

motor1 = motor.Motor(64, 116, 132, 2, 1, 115200, 'COM24', 2860, 1433)
motor2 = motor.Motor(64, 116, 132, 2, 2, 115200, 'COM24', 3870, 2790)
motor3 = motor.Motor(64, 116, 132, 2, 3, 115200, 'COM24', 3400, 2260)
motor4 = motor.Motor(64, 116, 132, 2, 4, 115200, 'COM24', 3600, 2390)
motor5 = motor.Motor(64, 116, 132, 2, 5, 115200, 'COM24', 1830, 240)

print(motor1.ADDR_PRO_TORQUE_ENABLE)
print(motor2.ADDR_PRO_TORQUE_ENABLE)
print(motor.Motor.MOVING_THRESHOLD)
motor.Motor.set_moving_threshold(1)
print(motor.Motor.MOVING_THRESHOLD)

motor1.set_port()
motor2.set_port()
motor3.set_port()
motor4.set_port()
motor5.set_port()

motor1.open_port()
motor2.open_port()
motor3.open_port()
motor4.open_port()
motor5.open_port()

motor1.torque_enable()
motor2.torque_enable()
motor3.torque_enable()
motor4.torque_enable()
motor5.torque_enable()

thumbPose = 1165

#the socket is no longer opening and closing constantly which means that 
#the program on the touchpad needs to be running first then run this

#open the socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT)) # Bind to the port 
s.listen(5) # Now wait for client connection.
c, addr = s.accept() # Establish connection with client.
print("Established Connection")

while (True):

    trigger, trackpad_x, trackpad_y, menu_button, grip_button, trackpad_pressed, trackpad_touched = v.read_left_controller()
    
    if (trackpad_pressed):
        scale = 1 + trackpad_y
    else:
        scale = 1

    #software limits for robot arm
    lowerLimit = float(0.2)*scale
    upperLimit = float(0.8)*scale
    
    #reading controller coordinates
    txt = ""
    for each in v.devices["controller_1"].get_pose_axis():
        txt += "%.2f" % each
        txt += " "
    targetPosition = re.findall(r"[-+]?\d*\.\d+|\d+", str(txt))
    
    #X axis is left and right to the "work table"
    X = (float(targetPosition[0]))
     
    #Y axis is forward and back relative to the "work table"
    #this reads the 3rd number as that number represents forward and back movement
    Y = (-float(targetPosition[2]))
  
    #Z axis is up and down
    #it is the second number because it is up and down movement
    #the vive axis has y and z swapped around
    Z = (float(targetPosition[1]) - 0.8)

    if (X*X + Y*Y > upperLimit*upperLimit):
        radians = math.atan2(Y,X)
        X = math.cos(radians)*upperLimit
        Y = math.sin(radians)*upperLimit
    elif (X*X + Y*Y < lowerLimit*lowerLimit):
        radians = math.atan2(Y,X)
        X = math.cos(radians)*lowerLimit
        Y = math.sin(radians)*lowerLimit

    #this is the up and down limit, it changes depending on the distance the arm is away
    #from the center, may need to be reworked a bit
    if Z > 1.1*scale - math.sqrt(X*X+Y*Y):
        Z = 1.1*scale - math.sqrt(X*X+Y*Y)
        
        
    # next 4 numbers: 
    
    #angle is in radians
    angle=float(targetPosition[3])
    
    #and vice versa, y and z axis is swapped around
    r_x= float(targetPosition[4])*angle
    r_y= float(targetPosition[5])*angle
    r_z= float(targetPosition[6])*angle
    
    #realigning the r_x so that the hand is facing forward when the controller is facing forward
    r_x = r_x - math.pi/2
    if (r_x > -1.5*math.pi) & (r_x < -math.pi):
        r_x = r_x+2*math.pi
    
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
        
    if (trackpad_touched):
        thumbPose = 1165 - (trackpad_x)*665
    
        
    motor1.write(int(2860 - trigger*900))
    motor2.write(int(3870 - trigger*1080))
    motor3.write(int(3400 - trigger*1140))
    motor4.write(int(3600 - trigger*1210))
    motor5.write(int(thumbPose))    
    if grip_button == True:
        break
    
    
    try:
        
        #sending target coordinates to robot
        c.sendto(("(" + str(X/scale) + "," + str(Y/scale) + "," + str(Z/scale) + "," + str(r_x) + "," + str(r_y) + "," + str(r_z) + ")").encode(),(CLIENT, PORT));
        #c.sendto(("(" + str(x/scale) + "," + str(y/scale) + "," + str(z/scale) + "," + str(rx) + "," + str(ry) + "," + str(rz) + ")").encode(),(CLIENT, PORT));

        
        #reading the message received from the robot arm
        #msg = c.recv(1024)
        #posePosition = re.findall(r"[-+]?\d*\.\d+|\d+", str(msg))
        #printing message
        #print('\r', posePosition, end='')
        time.sleep(0.008)

    except socket.error as socketerror:
        print("socket connection lost")
        c.close()
        s.close()
        motor1.torque_disable()
        motor2.torque_disable()
        motor3.torque_disable()
        motor4.torque_disable()
        motor5.torque_disable()
        motor1.close_port()
        motor2.close_port()
        motor3.close_port()
        motor4.close_port()
        motor5.close_port()
    except KeyboardInterrupt:
        print("CTRL + C Pressed, Ending program")
        c.close()
        s.close()
        motor1.torque_disable()
        motor2.torque_disable()
        motor3.torque_disable()
        motor4.torque_disable()
        motor5.torque_disable()
        motor1.close_port()
        motor2.close_port()
        motor3.close_port()
        motor4.close_port()
        motor5.close_port()        
    
c.close()
s.close()
    
motor1.torque_disable()
motor2.torque_disable()
motor3.torque_disable()
motor4.torque_disable()
motor5.torque_disable()
motor1.close_port()
motor2.close_port()
motor3.close_port()
motor4.close_port()
motor5.close_port()
print("Program finish")