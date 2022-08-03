from cascade_camera_dll import CascadeCameraDLL
import numpy as np

class CascadeCamera():
    def __init__(self):
        # init camera
        self.camera = CascadeCameraDLL()
        self.camera.pvcamInit()
        self.camera.camGetName()
        self.camera.camOpen()
        print("Camera was successfully initialized.")
    
    
    def setParameters(self):
        pass
    
    
    def prepareForAcquisition(self, hor_bin=1, ver_bin=1, exp_time=10):
        self.camera.expInitSeq()
        self.hor_bin = hor_bin
        self.ver_bin = ver_bin
        region = {
            "s1"    : 0,             # first pixel in the serial register
            "s2"    : 511,           # last pixel in the serial register
            "sbin"  : self.hor_bin , # serial binning for this region
            "p1"    : 0,             # first row in the parallel register
            "p2"    : 511,           # last row in the parallel register
            "pbin"  : ver_bin        # parallel binning for this region
        }
        self.camera.expSetupSeq(1, region, exp_time)
        print("Camera is ready to get images.")
    
    
    def getImage(self):
        self.camera.expStartSeq()
        while True:
            # wait for data or error
            status = self.camera.expCheckStatus()
            if status == self.camera.CONSTANTS["READOUT_FAILED"].value: # bad
                print(f"getImage() error")
                self.camera.errorCode()
                break
            elif status == self.camera.CONSTANTS["READOUT_COMPLETE"].value: # good
                # convert 1-D array to 2-D
                # "512" must be changed if non standard region is used
                # print( np.asarray(self.camera.frame), f"len is {len(np.asarray(self.camera.frame))}")
                frame = np.asarray(np.array_split(self.camera.frame, 512 / self.hor_bin))
                return frame
            
            
    def finishAcquisition(self):
        # must be used at the end to free all resources and properly close the camera
        self.camera.expFinishSeq()
        self.camera.expUninitSeq()
                

    def getCameraTemperature(self):
        temp = self.camera.getTemp()
        return temp / 100    