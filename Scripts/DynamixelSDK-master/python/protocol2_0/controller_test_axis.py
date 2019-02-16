#import openvr
from __future__ import print_function
import triad_openvr
import time
import math
import sys
import re
import motor


v = triad_openvr.triad_openvr()
v.print_discovered_objects()

if (len(sys.argv) == 1) | (len(sys.argv) == 2):
    run = True
else:
    print("Invalid number of arguments")
    run = False
    
targetPosition1 = [0]*6
rawPosition = []

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

while(run == True):
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
    
#    if (trigger > 0.0) | (menu_button == True) | (grip_button == True):
#        print("\r", round(trigger,2), round(trackpad_x,2), round(trackpad_y,2), menu_button, grip_button, trackpad_pressed, trackpad_touched, end = "")
#    else:
#        print("\r", targetPosition1, end = "")
    
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

    
    
    if (trackpad_touched):
        thumbPose = (trackpad_x)*665 + 1165
    
        
    motor1.write(int(2860 - trigger*900))
    motor2.write(int(3870 - trigger*1080))
    motor3.write(int(3400 - trigger*1140))
    motor4.write(int(3600 - trigger*1210))
    motor5.write(int(thumbPose))    
    if grip_button == True:
        break

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

print("end of function")