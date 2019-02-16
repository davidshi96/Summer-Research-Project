import time
import sys
import openvr
import math


def get_controller_ids(vrsys=None):
    if vrsys is None:
        vrsys = openvr.VRSystem()
    else:
        vrsys = vrsys
    left = None
    right = None
    for i in range(openvr.k_unMaxTrackedDeviceCount):
        device_class = vrsys.getTrackedDeviceClass(i)
        if device_class == openvr.TrackedDeviceClass_Controller:
            role = vrsys.getControllerRoleForTrackedDeviceIndex(i)
            if role == openvr.TrackedControllerRole_RightHand:
                right = i
            if role == openvr.TrackedControllerRole_LeftHand:
                left = i
    return left, right


if __name__ == '__main__':
    max_init_retries = 4
    retries = 0
    print("===========================")
    print("Initializing OpenVR...")
    while retries < max_init_retries:
        try:
            openvr.init(openvr.VRApplication_Other)
            break
        except openvr.OpenVRError as e:
            print("Error when initializing OpenVR (try {} / {})".format(
                  retries + 1, max_init_retries))
            print(e)
            retries += 1
            time.sleep(2.0)
    else:
        print("Could not initialize OpenVR, aborting.")
        print("Make sure the system is correctly plugged, you can also try")
        print("to do:")
        print("killall -9 vrcompositor vrmonitor vrdashboard")
        print("Before running this program again.")
        exit(0)

    print("Success!")
    print("===========================")
    vrsystem = openvr.VRSystem()

    left_id, right_id = None, None
    print("===========================")
    print("Waiting for controllers...")
    try:
        while left_id is None or right_id is None:
            left_id, right_id = get_controller_ids(vrsystem)
            if left_id and right_id:
                break
            print("Waiting for controllers...")
            time.sleep(1.0)
    except KeyboardInterrupt:
        print("Control+C pressed, shutting down...")
        openvr.shutdown()

    print("Left controller ID: " + str(left_id))
    print("Right controller ID: " + str(right_id))
    print("===========================")

    reading_rate_hz = 250

    print("===========================")
    print("Printing trigger events!")
    try:
        while True:
            time.sleep(1.0 / reading_rate_hz)
            result1, pControllerState1 = vrsystem.getControllerState(left_id)
            trigger1 = pControllerState1.rAxis[1].x
            result2, pControllerState2 = vrsystem.getControllerState(right_id)
            trigger2 = pControllerState2.rAxis[1].x
            
            print("\r", trigger1, trigger2, end = "")
            
            
    except KeyboardInterrupt:
        print("Control+C pressed, shutting down...")
        openvr.shutdown()


#vrsystem = openvr.VRSystem()
#poses_t = openvr.TrackedDevicePose_t * openvr.k_unMaxTrackedDeviceCount
#poses = poses_t()
#vrsystem.getDeviceToAbsoluteTrackingPose(openvr.TrackingUniverseSeated, 0, len(poses), poses)
#


#openvr.init(openvr.VRApplication_Background)
#
#while True:
#    print()
#    for c in range(16):
#        result, pControllerState = openvr.VRSystem().getControllerState(c)
#        for i in pControllerState.rAxis:
#            if i.x != 0 or i.y != 0:
#                print(i.x, i.y)
#                time.sleep(1/250)
