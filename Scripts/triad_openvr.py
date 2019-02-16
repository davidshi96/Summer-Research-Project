import time
import sys
import openvr
import math

# Function to print out text but instead of starting a new line it will overwrite the existing line
def update_text(txt):
    sys.stdout.write('\r'+txt)
    sys.stdout.flush()

#Convert the standard 3x4 position/rotation matrix to a x,y,z location and the appropriate Euler angles (in degrees)
def convert_to_euler(pose_mat):
    pitch = math.pi/2 + math.atan2(pose_mat[2][1] , pose_mat[2][2])
    
    if (pitch >  math.pi) & (pitch < 1.5* math.pi):
        pitch = pitch - 2*math.pi 
    
    roll = -math.pi + math.atan2(pose_mat[1][0] , pose_mat[0][0])
    if roll < -math.pi:
        roll = roll + 2*math.pi
    
    denominator = math.sqrt(pow(pose_mat[2][1], 2) + pow(pose_mat[2][2], 2))
    
    if ((pose_mat[2][1] < 0) & (pose_mat[2][2] < 0)):
        denominator = - denominator
    
    # zero is at at 5/6pi
    yaw = -math.pi + math.atan2(pose_mat[2][0] , denominator)
    
    if yaw < -math.pi:
        yaw = yaw + 2*math.pi
    
    
    x = pose_mat[0][3]
    y = pose_mat[1][3]
    z = pose_mat[2][3]
    return [x,y,z,-pitch,-roll,-yaw]
#    yaw = 180 / math.pi * math.atan2(-1 * pose_mat[2][0] , math.sqrt(pow(pose_mat[2][1], 2) + math.pow(pose_mat[2][2], 2)))
#    pitch = 180 / math.pi * math.atan2(pose_mat[2][1] , pose_mat[2][2])
#    roll = 180 / math.pi * math.atan2(pose_mat[1][0] , pose_mat[0][0])
#    x = pose_mat[0][3]
#    y = pose_mat[1][3]
#    z = pose_mat[2][3]
#    return [x,y,z,yaw,pitch,roll]
    

#Convert the standard 3x4 position/rotation matrix to a x,y,z location and the appropriate Quaternion
def convert_to_quaternion(pose_mat):
    #trace value to avoid negative values in the sqrt
    T= pose_mat[0][0]+pose_mat[1][1]+pose_mat[2][2]
    
    if (T > 0):
        r_w = math.sqrt(T + 1)/2
        r_x = (pose_mat[2][1]-pose_mat[1][2])/(4*r_w)
        r_y = (pose_mat[0][2]-pose_mat[2][0])/(4*r_w)
        r_z = (pose_mat[1][0]-pose_mat[0][1])/(4*r_w)
    elif ((pose_mat[0][0] > pose_mat[1][1]) & (pose_mat[0][0] > pose_mat[2][2])):
        S = math.sqrt(1 + pose_mat[0][0] - pose_mat[1][1] - pose_mat[2][2])*2
        r_w = (pose_mat[2][1] - pose_mat[1][2])/S
        r_x = 0.25*S
        r_y = (pose_mat[0][1] + pose_mat[1][0])/S
        r_z = (pose_mat[0][2] + pose_mat[2][0])/S
    elif (pose_mat[1][1] > pose_mat[2][2]):
        S = math.sqrt(1 - pose_mat[0][0] + pose_mat[1][1] - pose_mat[2][2])*2
        r_w = (pose_mat[0][2] - pose_mat[2][0])/S
        r_x = (pose_mat[0][1] + pose_mat[1][0])/S
        r_y = 0.25*S
        r_z = (pose_mat[2][1] + pose_mat[1][2])/S
    else:
        S = math.sqrt(1 - pose_mat[0][0] - pose_mat[1][1] + pose_mat[2][2])*2
        r_w = (pose_mat[1][0] - pose_mat[0][1])/S
        r_x = (pose_mat[0][2] + pose_mat[2][0])/S
        r_y = (pose_mat[2][1] + pose_mat[1][2])/S
        r_z = 0.25*S

    x = pose_mat[0][3]
    y = pose_mat[1][3]
    z = pose_mat[2][3]
    return [x,y,z,r_w,r_x,r_y,r_z]

#Convert the standard 3x4 position/rotation matrix to a x,y,z location and the appropriate axis rotation
def convert_to_axis(m):
    
    #re-oreienting matrix 
    w, h = 3, 3;
    pose_mat = [[0 for x in range(w)] for y in range(h)] 
    
    
    #adjusting for y and z coordinates being swapped
    pose_mat[0][0] = m[0][0]
    pose_mat[0][1] = -m[0][2]
    pose_mat[0][2] = m[0][1]
    pose_mat[1][0] = -m[2][0]
    pose_mat[1][1] = m[2][2]
    pose_mat[1][2] = -m[2][1]
    pose_mat[2][0] = m[1][0]
    pose_mat[2][1] = -m[1][2]
    pose_mat[2][2] = m[1][1]
    
    epsilon = 0.01 #margin for rounding errors
    epsilon2 = 0.1 #margin to distinguish between0 and 180 degrees
    
    x = m[0][3]
    y = m[1][3]
    z = m[2][3]
    
    #found a singularity
    if ((abs(pose_mat[0][1] - pose_mat[1][0]) < epsilon)
        &(abs(pose_mat[0][2] - pose_mat[2][0]) < epsilon)
        &(abs(pose_mat[1][2] - pose_mat[2][1]) < epsilon)):
        #if singularity is the identity matrix so angle = 0
        if ((abs(pose_mat[0][1] + pose_mat[1][0]) < epsilon2)
            &(abs(pose_mat[0][2] + pose_mat[2][0]) < epsilon2)
            &(abs(pose_mat[1][2] + pose_mat[2][1]) < epsilon2)
            &(abs(pose_mat[0][0] + pose_mat[1][1] + pose_mat[2][2] - 3) < epsilon2)):
                return [x,y,z,0,1,0,0]
        #otherwise singularity is at 180 degrees
        angle=math.pi
        xx = (pose_mat[0][0] + 1)/2
        yy = (pose_mat[1][1] + 1)/2
        zz = (pose_mat[2][2] + 1)/2
        xy = (pose_mat[0][1] + pose_mat[1][0])/4
        xz = (pose_mat[0][2] + pose_mat[2][0])/4
        yz = (pose_mat[2][1] + pose_mat[1][2])/4
        
        if ((xx > yy) & (xx > zz)): #when 00 is the largest diagonal term
            if (xx < epsilon):
                rx = 0
                ry = 0.7071
                rz = 0.7071
            else:
                rx = math.sqrt(xx)
                ry = xy / rx
                rz = xz / rx
        elif (yy > zz): #11 is the largest diagonal term
            if (yy < epsilon):
                rx = 0.7071
                ry = 0
                rz = 0.7071
            else:
                ry = math.sqrt(yy)
                rx = xy / ry
                rz = yz / ry
        else: #22 is the largest term
            if (zz < epsilon):
                rx = 0.7071
                ry = 0.7071
                rz = 0
            else:
                rz = math.sqrt(zz)
                rx = xz / rz
                ry = yz / rz
                
        return [x,y,z,angle,rx,ry,rz]
     
    s = math.sqrt((pose_mat[2][1] - pose_mat[1][2])*(pose_mat[2][1] - pose_mat[1][2])
        + (pose_mat[0][2] - pose_mat[2][0])*(pose_mat[0][2] - pose_mat[2][0])
        + (pose_mat[1][0] - pose_mat[0][1])*(pose_mat[1][0] - pose_mat[0][1])) #used to normalise
    if (abs(s) < 0.001):
        s = 1
    angle = math.acos((pose_mat[0][0] + pose_mat[1][1] + pose_mat[2][2] - 1)/2)
    rx = (pose_mat[2][1] - pose_mat[1][2])/s
    ry = (pose_mat[0][2] - pose_mat[2][0])/s
    rz = (pose_mat[1][0] - pose_mat[0][1])/s


    return [x,y,z,angle,rx,ry,rz]


#retrieve 3x3 rotaiton matrix 
def get_mat(m):
    
    return [m[0][0],m[0][1],m[0][2],m[1][0],m[1][1],m[1][2],m[2][0],m[2][1],m[2][2]]

#Define a class to make it easy to append pose matricies and convert to both Euler and Quaternion for plotting
class pose_sample_buffer():
    def __init__(self):
        self.i = 0
        self.index = []
        self.time = []
        self.x = []
        self.y = []
        self.z = []
        self.yaw = []
        self.pitch = []
        self.roll = []
        self.r_w = []
        self.r_x = []
        self.r_y = []
        self.r_z = []
    
    def append(self,pose_mat,t):
        self.time.append(t)
        self.x.append(pose_mat[0][3])
        self.y.append(pose_mat[1][3])
        self.z.append(pose_mat[2][3])
        self.yaw.append(180 / math.pi * math.atan(pose_mat[1][0] /pose_mat[0][0]))
        self.pitch.append(180 / math.pi * math.atan(-1 * pose_mat[2][0] / math.sqrt(pow(pose_mat[2][1], 2) + math.pow(pose_mat[2][2], 2))))
        self.roll.append(180 / math.pi * math.atan(pose_mat[2][1] /pose_mat[2][2]))
        r_w = math.sqrt(abs(1+pose_mat[0][0]+pose_mat[1][1]+pose_mat[2][2]))/2
        self.r_w.append(r_w)
        self.r_x.append((pose_mat[2][1]-pose_mat[1][2])/(4*r_w))
        self.r_y.append((pose_mat[0][2]-pose_mat[2][0])/(4*r_w))
        self.r_z.append((pose_mat[1][0]-pose_mat[0][1])/(4*r_w))

class vr_tracked_device():
    def __init__(self,vr_obj,index,device_class):
        self.device_class = device_class
        self.index = index
        self.vr = vr_obj
        
    def get_serial(self):
        return self.vr.getStringTrackedDeviceProperty(self.index,openvr.Prop_SerialNumber_String).decode('utf-8')
    
    def get_model(self):
        return self.vr.getStringTrackedDeviceProperty(self.index,openvr.Prop_ModelNumber_String).decode('utf-8')
        
    def sample(self,num_samples,sample_rate):
        interval = 1/sample_rate
        rtn = pose_sample_buffer()
        sample_start = time.time()
        for i in range(num_samples):
            start = time.time()
            pose = self.vr.getDeviceToAbsoluteTrackingPose(openvr.TrackingUniverseStanding, 0,openvr.k_unMaxTrackedDeviceCount)
            rtn.append(pose[self.index].mDeviceToAbsoluteTracking,time.time()-sample_start)
            sleep_time = interval- (time.time()-start)
            if sleep_time>0:
                time.sleep(sleep_time)
        return rtn
        
    def get_pose_euler(self):
        pose = self.vr.getDeviceToAbsoluteTrackingPose(openvr.TrackingUniverseStanding, 0,openvr.k_unMaxTrackedDeviceCount)
        return convert_to_euler(pose[self.index].mDeviceToAbsoluteTracking)
    
    def get_pose_quaternion(self):
        pose = self.vr.getDeviceToAbsoluteTrackingPose(openvr.TrackingUniverseStanding, 0,openvr.k_unMaxTrackedDeviceCount)
        return convert_to_quaternion(pose[self.index].mDeviceToAbsoluteTracking)
    
    def get_pose_axis(self):
        pose = self.vr.getDeviceToAbsoluteTrackingPose(openvr.TrackingUniverseStanding, 0,openvr.k_unMaxTrackedDeviceCount)
        return convert_to_axis(pose[self.index].mDeviceToAbsoluteTracking)
    
    def get_pose_mat(self):
        pose = self.vr.getDeviceToAbsoluteTrackingPose(openvr.TrackingUniverseStanding, 0,openvr.k_unMaxTrackedDeviceCount)
        return get_mat(pose[self.index].mDeviceToAbsoluteTracking)

class vr_tracking_reference(vr_tracked_device):
    def get_mode(self):
        return self.vr.getStringTrackedDeviceProperty(self.index,openvr.Prop_ModeLabel_String).decode('utf-8').upper()
    def sample(self,num_samples,sample_rate):
        print("Warning: Tracking References do not move, sample isn't much use...")
        
class triad_openvr():
    def __init__(self):
        # Initialize OpenVR in the 
        self.vr = openvr.init(openvr.VRApplication_Other)
        
        # Initializing object to hold indexes for various tracked objects 
        self.object_names = {"Tracking Reference":[],"HMD":[],"Controller":[],"Tracker":[]}
        self.devices = {}
        self.left = 0
        self.right = 0
        self.trigger1 = 0.0
        self.trigger2 = 0.0
        poses = self.vr.getDeviceToAbsoluteTrackingPose(openvr.TrackingUniverseStanding, 0,
                                                               openvr.k_unMaxTrackedDeviceCount)        
        
        # Iterate through the pose list to find the active devices and determine their type
        for i in range(openvr.k_unMaxTrackedDeviceCount):
            if poses[i].bPoseIsValid:
                device_class = self.vr.getTrackedDeviceClass(i)
                if (device_class == openvr.TrackedDeviceClass_Controller):
                    device_name = "controller_"+str(len(self.object_names["Controller"])+1)
                    self.object_names["Controller"].append(device_name)
                    self.devices[device_name] = vr_tracked_device(self.vr,i,"Controller")
                    
                    role = self.vr.getControllerRoleForTrackedDeviceIndex(i)
                    if role == openvr.TrackedControllerRole_RightHand:
                        self.right = i
                    if role == openvr.TrackedControllerRole_LeftHand:
                        self.left = i
                        
                elif (device_class == openvr.TrackedDeviceClass_HMD):
                    device_name = "hmd_"+str(len(self.object_names["HMD"])+1)
                    self.object_names["HMD"].append(device_name)
                    self.devices[device_name] = vr_tracked_device(self.vr,i,"HMD")
                elif (device_class == openvr.TrackedDeviceClass_GenericTracker):
                    device_name = "tracker_"+str(len(self.object_names["Tracker"])+1)
                    self.object_names["Tracker"].append(device_name)
                    self.devices[device_name] = vr_tracked_device(self.vr,i,"Tracker")
                elif (device_class == openvr.TrackedDeviceClass_TrackingReference):
                    device_name = "tracking_reference_"+str(len(self.object_names["Tracking Reference"])+1)
                    self.object_names["Tracking Reference"].append(device_name)
                    self.devices[device_name] = vr_tracking_reference(self.vr,i,"Tracking Reference")
    
    def rename_device(self,old_device_name,new_device_name):
        self.devices[new_device_name] = self.devices.pop(old_device_name)
        for i in range(len(self.object_names[self.devices[new_device_name].device_class])):
            if self.object_names[self.devices[new_device_name].device_class][i] == old_device_name:
                self.object_names[self.devices[new_device_name].device_class][i] = new_device_name
    
    def print_discovered_objects(self):   
        for device_type in self.object_names:
            plural = device_type
            if len(self.object_names[device_type])!=1:
                plural+="s"
            print("Found "+str(len(self.object_names[device_type]))+" "+plural)
            for device in self.object_names[device_type]:
                if device_type == "Tracking Reference":
                    print("  "+device+" ("+self.devices[device].get_serial()+
                          ", Mode "+self.devices[device].get_mode()+
                          ", "+self.devices[device].get_model()+
                          ")")
                else:
                    print("  "+device+" ("+self.devices[device].get_serial()+
                          ", "+self.devices[device].get_model()+")")    
                          
    def read_left_controller(self):
        result1, pControllerState1 = self.vr.getControllerState(self.left)
        self.trigger1 = pControllerState1.rAxis[1].x
        self.trackpad_x1 = pControllerState1.rAxis[0].x
        self.trackpad_y1 = pControllerState1.rAxis[0].y
        self.menu_button1 = bool(pControllerState1.ulButtonPressed >> 1 & 1)
        self.grip_button1 = bool(pControllerState1.ulButtonPressed >> 2 & 1)
        self.trackpad_pressed1 = bool(pControllerState1.ulButtonPressed >> 32 & 1) 
        self.trackpad_touched1 = bool(pControllerState1.ulButtonTouched >> 32 & 1)
        return [self.trigger1, self.trackpad_x1, self.trackpad_y1, self.menu_button1, self.grip_button1, self.trackpad_pressed1, self.trackpad_touched1]
    
    
    def read_right_controller(self):
        result2, pControllerState2 = self.vr.getControllerState(self.right)
        self.trigger2 = pControllerState2.rAxis[1].x
        self.trackpad_x2 = pControllerState2.rAxis[0].x
        self.trackpad_y2 = pControllerState2.rAxis[0].y
        self.menu_button2 = bool(pControllerState2.ulButtonPressed >> 1 & 1)
        self.grip_button2 = bool(pControllerState2.ulButtonPressed >> 2 & 1)
        self.trackpad_pressed2 = bool(pControllerState2.ulButtonPressed >> 32 & 1) 
        self.trackpad_touched2 = bool(pControllerState2.ulButtonTouched >> 32 & 1)
        
        return [self.trigger2, self.trackpad_x2, self.trackpad_y2, self.menu_button2, self.grip_button2, self.trackpad_pressed2, self.trackpad_touched2]