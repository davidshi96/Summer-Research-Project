#!/usr/bin/env python
# -*- coding: utf-8 -*-

################################################################################
################################################################################

# Author: Geng Gao

#
# *********     MultiPort Example      *********
#
#
#
#

import os

if os.name == 'nt':
    import msvcrt
    def getch():
        return msvcrt.getch().decode()
else:
    import sys, tty, termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    def getch():
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


# taking input from the user to find out where new motor position should be.
def userInput(min_pos, max_pos, currentPos, motorID):
    # checking if the input is an actual number
    try:
        new_position = input("Please enter a position motor %d between %d to %d: " %(motorID, min_pos, max_pos))
        new_position = int(new_position)
        # checking if in range
        if (max_pos >= new_position >= min_pos):
            return new_position
        else:
            print("Please enter a value within the range %d to %d for motor %d" %(min_pos, max_pos, motorID))
            return currentPos
    except:
        print("the value entered was not a number")
        return currentPos


os.sys.path.append('../dynamixel_functions_py')             # Path setting

import dynamixel_functions as dynamixel                     # Uses Dynamixel SDK library

ESC_ASCII_VALUE = 0x1b

############################################################################################################################################################################
class Motor():

    TORQUE_ENABLE = 1
    TORQUE_DISABLE = 0
    COMM_SUCCESS = 0
    COMM_TX_FAIL = -1001
    MOVING_THRESHOLD = 10

    def __init__(self, ADDR_PRO_TORQUE_ENABLE, ADDR_PRO_GOAL_POSITION , ADDR_PRO_PRESENT_POSITION, PROTOCOL, ID, BAUDRATE, PORT, MAX_POS, MIN_POS):
        self.ADDR_PRO_TORQUE_ENABLE = ADDR_PRO_TORQUE_ENABLE
        self.ADDR_PRO_GOAL_POSITION = ADDR_PRO_GOAL_POSITION
        self.ADDR_PRO_PRESENT_POSITION = ADDR_PRO_PRESENT_POSITION
        self.PROTOCOL = PROTOCOL
        self.ID = ID
        self.BAUDRATE = BAUDRATE
        self.PORT = PORT
        self.MAX_POS = MAX_POS
        self.MIN_POS = MIN_POS
        self.RANGE = MAX_POS - MIN_POS

    def set_port(self):
        getch()
        self.port_num = dynamixel.portHandler(self.PORT)
        print(self.port_num)
        # Initialize PacketHandler Structs
        dynamixel.packetHandler()

    def open_port(self):
        dxl_comm_result = self.COMM_TX_FAIL                              # Communication result
        dxl_error = 0                                               # Dynamixel error

        # Open port
        if dynamixel.openPort(self.port_num):
            print("Succeeded to open the port!")
        else:
            print("Failed to open the port!")
            print("Press any key to terminate...")
            getch()
            quit()

        # Set port baudrate
        if dynamixel.setBaudRate(self.port_num, self.BAUDRATE):
            print("Succeeded to change the baudrate!")
        else:
            print("Failed to change the baudrate!")
            print("Press any key to terminate...")
            getch()
            quit()

    def torque_enable(self):
        # Enable Dynamixel Torque
        dynamixel.write1ByteTxRx(self.port_num, self.PROTOCOL, self.ID, self.ADDR_PRO_TORQUE_ENABLE, self.TORQUE_ENABLE)
        dxl_comm_result = dynamixel.getLastTxRxResult(self.port_num, self.PROTOCOL)
        dxl_error = dynamixel.getLastRxPacketError(self.port_num, self.PROTOCOL)
        if dxl_comm_result != self.COMM_SUCCESS:
            print(dynamixel.getTxRxResult(self.PROTOCOL, dxl_comm_result))
        elif dxl_error != 0:
            print(dynamixel.getRxPacketError(self.PROTOCOL, dxl_error))
        else:
            print("Dynamixel#%03d has been successfully connected" % (self.ID))

    def torque_disable(self):
        dynamixel.write1ByteTxRx(self.port_num, self.PROTOCOL, self.ID, self.ADDR_PRO_TORQUE_ENABLE, self.TORQUE_DISABLE)
        dxl_comm_result = dynamixel.getLastTxRxResult(self.port_num, self.PROTOCOL)
        dxl_error = dynamixel.getLastRxPacketError(self.port_num, self.PROTOCOL)
        if dxl_comm_result != self.COMM_SUCCESS:
            print(dynamixel.getTxRxResult(self.PROTOCOL, dxl_comm_result))
        elif dxl_error != 0:
            print(dynamixel.getRxPacketError(self.PROTOCOL, dxl_error))

    def close_port(self):
        dynamixel.closePort(self.port_num)

    def write(self, new_pos):
        if (self.MAX_POS >= new_pos >= self.MIN_POS):
            dynamixel.write4ByteTxRx(self.port_num, self.PROTOCOL, self.ID, self.ADDR_PRO_GOAL_POSITION, new_pos)
            dxl_comm_result = dynamixel.getLastTxRxResult(self.port_num, self.PROTOCOL)
            dxl_error = dynamixel.getLastRxPacketError(self.port_num, self.PROTOCOL)
            if dxl_comm_result != self.COMM_SUCCESS:
                print(dynamixel.getTxRxResult(self.PROTOCOL, dxl_comm_result))
            elif dxl_error != 0:
                print(dynamixel.getRxPacketError(self.PROTOCOL, dxl_error))

    def read(self):
        # Read present position
        present_position = dynamixel.read4ByteTxRx(self.port_num, self.PROTOCOL, self.ID, self.ADDR_PRO_PRESENT_POSITION)
        dxl_comm_result = dynamixel.getLastTxRxResult(self.port_num, self.PROTOCOL)
        dxl_error = dynamixel.getLastRxPacketError(self.port_num, self.PROTOCOL)
        if dxl_comm_result != self.COMM_SUCCESS:
            print(dynamixel.getTxRxResult(self.PROTOCOL, dxl_comm_result))
        elif dxl_error != 0:
            print(dynamixel.getRxPacketError(self.PROTOCOL, dxl_error))
        return present_position

    @classmethod
    def set_moving_threshold(cls, threshold):
        cls.MOVING_THRESHOLD = threshold
###########################################################################################################################################################################3
#test code
#motor1 = Motor(64, 116, 132, 2, 1, 115200, 'COM24', 2860, 1433)
#motor2 = Motor(64, 116, 132, 2, 2, 115200, 'COM24', 3870, 2790)
#motor3 = Motor(64, 116, 132, 2, 3, 115200, 'COM24', 3400, 2260)
#motor4 = Motor(64, 116, 132, 2, 4, 115200, 'COM24', 3600, 2390)
#motor5 = Motor(64, 116, 132, 2, 5, 115200, 'COM24', 1830, 240)
#
#print(motor1.ADDR_PRO_TORQUE_ENABLE)
#print(motor2.ADDR_PRO_TORQUE_ENABLE)
#print(Motor.MOVING_THRESHOLD)
#Motor.set_moving_threshold(1)
#print(Motor.MOVING_THRESHOLD)
#
#
#motor1.set_port()
#motor2.set_port()
#motor3.set_port()
#motor4.set_port()
#motor5.set_port()
#
#motor1.open_port()
#motor2.open_port()
#motor3.open_port()
#motor4.open_port()
#motor5.open_port()
#
#motor1.torque_enable()
#motor2.torque_enable()
#motor3.torque_enable()
#motor4.torque_enable()
#motor5.torque_enable()
#
#while 1:
#
#    print(motor1.read())
#    print(motor2.read())
#    print(motor3.read())
#    print(motor4.read())
#    print(motor5.read())
#
#    print("Press any key to continue! (or press ESC to quit!)")
#    if getch() == chr(ESC_ASCII_VALUE):
#        break
#
#motor1.torque_disable()
#motor2.torque_disable()
#motor3.torque_disable()
#motor4.torque_disable()
#motor5.torque_disable()
#
#motor1.close_port()
#motor2.close_port()
#motor3.close_port()
#motor4.close_port()
#motor5.close_port()
