#!/usr/bin/env python
# -*- coding: utf-8 -*-

################################################################################
# Copyright 2017 ROBOTIS CO., LTD.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
################################################################################

# Author: Ryu Woon Jung (Leon)

#
# *********     MultiPort Example      *********
#
#
# Available Dynamixel model on this example : All models using Protocol 2.0
# This example is designed for using two Dynamixel PRO 54-200, and two USB2DYNAMIXELs.
# To use another Dynamixel model, such as X series, see their details in E-Manual(support.robotis.com) and edit below variables yourself.
# Be sure that Dynamixel PRO properties are already set as %% ID : 1 / Baudnum : 1 (Baudrate : 57600)
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

# Control table address
ADDR_PRO_TORQUE_ENABLE       = 64#24                          # Control table address is different in Dynamixel model
ADDR_PRO_GOAL_POSITION       = 116#30
ADDR_PRO_PRESENT_POSITION    = 132#37

# Protocol version
PROTOCOL_VERSION            = 2                             # See which protocol version is used in the Dynamixel

# Default setting
DXL1_ID                     = 1                             # Dynamixel ID: 1
DXL2_ID                     = 2                             # Dynamixel ID: 2
BAUDRATE                    = 57600#1000000
DEVICENAME1                 = "COM28"                        # Check which port is being used on your controller
DEVICENAME2                 = "COM28"                        # ex) Windows: "COM1"   Linux: "/dev/ttyUSB0" Mac: "/dev/tty.usbserial-*"

TORQUE_ENABLE               = 1                             # Value for enabling the torque
TORQUE_DISABLE              = 0                             # Value for disabling the torque
DXL_MINIMUM_POSITION_VALUE  = -4095                       # Dynamixel will rotate between this value
DXL_MAXIMUM_POSITION_VALUE  = 8000#4095#1000                       # and this value (note that the Dynamixel would not move when the position value is out of movable range. Check e-manual about the range of the Dynamixel you use.)
DXL_MOVING_STATUS_THRESHOLD = 10                            # Dynamixel moving status threshold

ESC_ASCII_VALUE             = 0x1b

COMM_SUCCESS                = 0                             # Communication Success result value
COMM_TX_FAIL                = -1001                         # Communication Tx Failed**

# Initialize PortHandler Structs
# Set the port path
# Get methods and members of PortHandlerLinux or PortHandlerWindows
port_num1 = dynamixel.portHandler(DEVICENAME1)
port_num2 = dynamixel.portHandler(DEVICENAME2)

# Initialize PacketHandler Structs
dynamixel.packetHandler()

index = 0
dxl_comm_result = COMM_TX_FAIL                              # Communication result
dxl1_goal_position = DXL_MINIMUM_POSITION_VALUE             # Goal position
dxl2_goal_position = DXL_MINIMUM_POSITION_VALUE

dxl_error = 0                                               # Dynamixel error
dxl1_present_position = 0                                   # Present position
dxl2_present_position = 0

# Open port1
if dynamixel.openPort(port_num1):
    print("Succeeded to open the port!")
else:
    print("Failed to open the port!")
    print("Press any key to terminate...")
    getch()
    quit()

# Open port2
if dynamixel.openPort(port_num2):
    print("Succeeded to open the port!")
else:
    print("Failed to open the port!")
    print("Press any key to terminate...")
    getch()
    quit()


# Set port1 baudrate
if dynamixel.setBaudRate(port_num1, BAUDRATE):
    print("Succeeded to change the baudrate!")
else:
    print("Failed to change the baudrate!")
    print("Press any key to terminate...")
    getch()
    quit()

# Set port2 baudrate
if dynamixel.setBaudRate(port_num2, BAUDRATE):
    print("Succeeded to change the baudrate!")
else:
    print("Failed to change the baudrate!")
    print("Press any key to terminate...")
    getch()
    quit()


# Enable Dynamixel#1 Torque
dynamixel.write1ByteTxRx(port_num1, PROTOCOL_VERSION, DXL1_ID, ADDR_PRO_TORQUE_ENABLE, TORQUE_ENABLE)
dxl_comm_result = dynamixel.getLastTxRxResult(port_num1, PROTOCOL_VERSION)
dxl_error = dynamixel.getLastRxPacketError(port_num1, PROTOCOL_VERSION)
if dxl_comm_result != COMM_SUCCESS:
    print(dynamixel.getTxRxResult(PROTOCOL_VERSION, dxl_comm_result))
elif dxl_error != 0:
    print(dynamixel.getRxPacketError(PROTOCOL_VERSION, dxl_error))
else:
    print("Dynamixel#1 has been successfully connected")

# Enable Dynamixel#2 Torque
dynamixel.write1ByteTxRx(port_num2, PROTOCOL_VERSION, DXL2_ID, ADDR_PRO_TORQUE_ENABLE, TORQUE_ENABLE)
dxl_comm_result = dynamixel.getLastTxRxResult(port_num2, PROTOCOL_VERSION)
dxl_error = dynamixel.getLastRxPacketError(port_num2, PROTOCOL_VERSION)
if dxl_comm_result != COMM_SUCCESS:
    print(dynamixel.getTxRxResult(PROTOCOL_VERSION, dxl_comm_result))
elif dxl_error != 0:
    print(dynamixel.getRxPacketError(PROTOCOL_VERSION, dxl_error))
else:
    print("Dynamixel#2 has been successfully connected")


while 1:
    print("Press any key to continue! (or press ESC to quit!)")
    if getch() == chr(ESC_ASCII_VALUE):
        break

    # asking user for input
    dxl1_goal_position = userInput(DXL_MINIMUM_POSITION_VALUE, DXL_MAXIMUM_POSITION_VALUE, dxl1_present_position, DXL1_ID)
    dxl2_goal_position = userInput(DXL_MINIMUM_POSITION_VALUE, DXL_MAXIMUM_POSITION_VALUE, dxl2_present_position, DXL2_ID)

    # Write Dynamixel#1 goal position
    dynamixel.write4ByteTxRx(port_num1, PROTOCOL_VERSION, DXL1_ID, ADDR_PRO_GOAL_POSITION, dxl1_goal_position)
    dxl_comm_result = dynamixel.getLastTxRxResult(port_num1, PROTOCOL_VERSION)
    dxl_error = dynamixel.getLastRxPacketError(port_num1, PROTOCOL_VERSION)
    if dxl_comm_result != COMM_SUCCESS:
        print(dynamixel.getTxRxResult(PROTOCOL_VERSION, dxl_comm_result))
    elif dxl_error != 0:
        print(dynamixel.getRxPacketError(PROTOCOL_VERSION, dxl_error))

    # Write Dynamixel#2 goal position
    dynamixel.write4ByteTxRx(port_num2, PROTOCOL_VERSION, DXL2_ID, ADDR_PRO_GOAL_POSITION, dxl2_goal_position)
    dxl_comm_result = dynamixel.getLastTxRxResult(port_num2, PROTOCOL_VERSION)
    dxl_error = dynamixel.getLastRxPacketError(port_num2, PROTOCOL_VERSION)
    if dxl_comm_result != COMM_SUCCESS:
        print(dynamixel.getTxRxResult(PROTOCOL_VERSION, dxl_comm_result))
    elif dxl_error != 0:
        print(dynamixel.getRxPacketError(PROTOCOL_VERSION, dxl_error))

    while 1:
        # Read present position
        dxl1_present_position = dynamixel.read4ByteTxRx(port_num1, PROTOCOL_VERSION, DXL1_ID, ADDR_PRO_PRESENT_POSITION)
        dxl_comm_result = dynamixel.getLastTxRxResult(port_num1, PROTOCOL_VERSION)
        dxl_error = dynamixel.getLastRxPacketError(port_num1, PROTOCOL_VERSION)
        if dxl_comm_result != COMM_SUCCESS:
            print(dynamixel.getTxRxResult(PROTOCOL_VERSION, dxl_comm_result))
        elif dxl_error != 0:
            print(dynamixel.getRxPacketError(PROTOCOL_VERSION, dxl_error))

        # Read present position
        dxl2_present_position = dynamixel.read4ByteTxRx(port_num2, PROTOCOL_VERSION, DXL2_ID, ADDR_PRO_PRESENT_POSITION)
        dxl_comm_result = dynamixel.getLastTxRxResult(port_num2, PROTOCOL_VERSION)
        dxl_error = dynamixel.getLastRxPacketError(port_num2, PROTOCOL_VERSION)
        if dxl_comm_result != COMM_SUCCESS:
            print(dynamixel.getTxRxResult(PROTOCOL_VERSION, dxl_comm_result))
        elif dxl_error != 0:
            print(dynamixel.getRxPacketError(PROTOCOL_VERSION, dxl_error))

        print("[ID:%03d] GoalPos:%03d  PresPos:%03d\t[ID:%03d] GoalPos:%03d  PresPos:%03d" % (DXL1_ID, dxl1_goal_position, dxl1_present_position, DXL2_ID, dxl2_goal_position, dxl2_present_position))

        if not ((abs(dxl1_goal_position - dxl1_present_position) > DXL_MOVING_STATUS_THRESHOLD) or (abs(dxl2_goal_position - dxl2_present_position) > DXL_MOVING_STATUS_THRESHOLD)):
            break

    # Change goal position
    '''
    if index == 0:
        index = 1
    else:
        index = 0'''


# Disable Dynamixel#1 Torque
dynamixel.write1ByteTxRx(port_num1, PROTOCOL_VERSION, DXL1_ID, ADDR_PRO_TORQUE_ENABLE, TORQUE_DISABLE)
dxl_comm_result = dynamixel.getLastTxRxResult(port_num1, PROTOCOL_VERSION)
dxl_error = dynamixel.getLastRxPacketError(port_num1, PROTOCOL_VERSION)
if dxl_comm_result != COMM_SUCCESS:
    print(dynamixel.getTxRxResult(PROTOCOL_VERSION, dxl_comm_result))
elif dxl_error != 0:
    print(dynamixel.getRxPacketError(PROTOCOL_VERSION, dxl_error))

# Disable Dynamixel#2 Torque
dynamixel.write1ByteTxRx(port_num2, PROTOCOL_VERSION, DXL2_ID, ADDR_PRO_TORQUE_ENABLE, TORQUE_DISABLE)
dxl_comm_result = dynamixel.getLastTxRxResult(port_num2, PROTOCOL_VERSION)
dxl_error = dynamixel.getLastRxPacketError(port_num2, PROTOCOL_VERSION)
if dxl_comm_result != COMM_SUCCESS:
    print(dynamixel.getTxRxResult(PROTOCOL_VERSION, dxl_comm_result))
elif dxl_error != 0:
    print(dynamixel.getRxPacketError(PROTOCOL_VERSION, dxl_error))

# Close port
dynamixel.closePort(port_num1)

dynamixel.closePort(port_num2)
