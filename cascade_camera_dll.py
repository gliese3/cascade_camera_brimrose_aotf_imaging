import ctypes as ct

class CascadeCameraDLL():
    def __init__(self):
        self.lib = ct.WinDLL("lib/pvcam32.dll")
        
        # CONSTANTS
        self.CAMERA_NUM = 0 # the only camera has 0 number
        
        # see "PVCAM User Manual" for details
        self.CONSTANTS = {
            "OPEN_EXCLUSIVE"        : ct.c_int16(0),
            "TIMED_MODE"            : ct.c_int16(0), #!
            "READOUT_COMPLETE"      : ct.c_int16(3),
            "READOUT_IN_PROGRESS"   : ct.c_int16(2),
            "EXPOSURE_IN_PROGRESS"  : ct.c_int16(1),
            "READOUT_FAILED"        : ct.c_int16(4)
            
        }       
    
    
    def pvcamInit(self):
        ret_code = self.lib.pl_pvcam_init()
        assert ret_code == 1, "pvcamInit() error"
        
        
    def camGetName(self):
        self.cam_num = ct.c_int16(self.CAMERA_NUM) 
        ch_array = (ct.c_char * 32)()
        ret_code = self.lib.pl_cam_get_name(self.cam_num, ct.byref(ch_array))
        assert ret_code == 1, "camGetName() error"
        self.camera_name = ch_array
        
        
    def camOpen(self):
        self.hcam = ct.c_int16()
        ret_code = self.lib.pl_cam_open(ct.byref(self.camera_name),
                                        ct.byref(self.hcam),
                                        self.CONSTANTS["OPEN_EXCLUSIVE"])
        assert ret_code == 1, self.errorCode()
        
    
    def expInitSeq(self):
        ret_code = self.lib.pl_exp_init_seq()
        assert ret_code == 1, "expInitSeq() error"
        
        
    def expSetupSeq(self, exp_total, region, exp_time):
        exp_total = ct.c_uint16(exp_total) # specifies the number of images to take
        reg = self.RgnType()
        reg.s1   = region["s1"]
        reg.s2   = region["s2"]
        reg.sbin = region["sbin"]
        reg.p1   = region["p1"]
        reg.p2   = region["p2"]
        reg.pbin = region["pbin"]
        exp_time = ct.c_uint32(exp_time)
        self.stream_size = ct.c_uint32()
        
        ret_code = self.lib.pl_exp_setup_seq(self.hcam,
                                         exp_total,
                                         ct.c_uint16(1), # region definitions?
                                         ct.byref(reg),
                                         self.CONSTANTS["TIMED_MODE"],
                                         exp_time,
                                         ct.byref(self.stream_size))
        if ret_code == 1: 
            self.errorCode()
            raise Exception("expSetupSeq() error")
        
        
    def expStartSeq(self):
        self.frame = (ct.c_uint16 * (int(self.stream_size.value / 2)))() #! looks like / 2 is needed 
        ret_code = self.lib.pl_exp_start_seq(self.hcam, ct.byref(self.frame))
        assert ret_code == 1, "expStartSeq() error"
        
        
    def expCheckStatus(self):
        self.status = ct.c_int16()
        byte_cnt = ct.c_uint32()
        ret_code = self.lib.pl_exp_check_status(self.hcam,
                                            ct.byref(self.status),
                                            ct.byref(byte_cnt))
        # print(f"\nexpCheckStatus() ret_code is {ret_code}")
        if ret_code == 0: 
            self.errorCode()
            raise Exception("expCheckStatus() error")
        else:
            return self.status.value
        
        
    def expFinishSeq(self):
        ret_code = self.lib.pl_exp_finish_seq(self.hcam,
                                          self.frame,
                                          ct.c_int16(0))
        assert ret_code == 1, "expFinishSeq() error"
        
        
    def expUninitSeq(self):
        ret_code = self.lib.pl_exp_uninit_seq()
        assert ret_code == 1, "expUninitSeq() error"                                  
                                          
    
    def camClose(self):
        ret_code = self.lib.pl_cam_close(self.hcam)
        assert ret_code == 1, "camClose() error"
        
        
    def errorCode(self):
        ret_code = self.lib.pl_error_code()
        if ret_code != 0:
            self.errorMessage(ret_code)
            
    
    def errorMessage(self, error_code):
        error_code = ct.c_int16(error_code)
        msg = (ct.c_char * 255)()
        ret_code = self.lib.pl_error_message(error_code, ct.byref(msg))
        assert ret_code == 1, "errorMessage() error"
        print(f"Error code: {error_code} -> {msg.value}")


    def getTemp(self): 
        param_id = ct.c_uint32(16908813) # default value for CCD temp
        param_attrib = ct.c_int16(0) # ATTR_CURRENT, see page 65
        param_value = ct.c_int16() 
        ret_code = self.lib.pl_get_param(self.hcam,
                                         param_id, param_attrib,
                                         ct.byref(param_value))
        assert ret_code == 1, "getParam() error"
        return param_value.value                              
    
        
    # classes to mimic structures in C
    class RgnType(ct.Structure):
        _fields_ = [("s1",      ct.c_uint16), # first pixel in the serial register
                    ("s2",      ct.c_uint16), # last pixel in the serial register
                    ("sbin",    ct.c_uint16), # serial binning for this region
                    ("p1",      ct.c_uint16), # first row in the parallel register
                    ("p2",      ct.c_uint16), # last row in the parallel register
                    ("pbin",    ct.c_uint16)] # parallel binning for this region
        