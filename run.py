from brimrose_aotf import AOTF
from cascade_camera import CascadeCamera

import numpy as np
import matplotlib.pyplot as plt
from time import sleep
from datetime import date
import os

#******************************* INITIAL SETTINGS *****************************
# GENERAL SETTINGS
SAMPLE_NAME = "irina1"
TIME_PAUSE = 10 # pause between steps in seconds
WAVE_LEN_ARRAY = [520, 530, 540, 580, 590, 600, 610, 620] # in nm
NUM_OF_STEPS = 50 # number of iterations

# SETTINGS FOR CAMERA
HOR_BIN = 2     # horizontal binning
VER_BIN = 2     # vertical binning
EXP_TIME = 3000 # exposure time

# SETTINGS FOR AOTF
AOTF_AMPLITUDE = 308 # in range from 0 to 4095
#******************************************************************************

# init our devices
aotf = AOTF()
camera = CascadeCamera()

# create a folder for data
current_dir = os.getcwd()
today = date.today()
directory = f"[{today}] {SAMPLE_NAME}"
full_path = os.path.join(current_dir, "data", directory)
try:
    os.mkdir(full_path)
except Exception:
    print(f"warning: folder {directory} elready exists")

# create sub-folders for each wavelength
for wave_len in  WAVE_LEN_ARRAY:
    path = os.path.join(full_path, str(wave_len))
    try:
        os.mkdir(path)
    except Exception:
        print(f"warning: folder {wave_len} in {directory} elready exists")

# prepare devices for experiment
aotf.setAmplitude(308)
camera.prepareForAcquisition(hor_bin=HOR_BIN,
                             ver_bin=VER_BIN,
                             exp_time=EXP_TIME)

# prepare container for images
images_dict = {wav_len : [] for wav_len in WAVE_LEN_ARRAY}

# experiment loop
print("Ready for experiment.\n")
print("-" * 40)
for step in range(NUM_OF_STEPS):
    for wave_len in WAVE_LEN_ARRAY:
        print(f"step: {step} of {NUM_OF_STEPS -1} | wavelength: {wave_len} nm")
        aotf.setWavelength(wave_len)
        image = camera.getImage()
        images_dict[wave_len].append(image)

    print(f"pause for {TIME_PAUSE} seconds\n")
    sleep(TIME_PAUSE)
    print("-" * 40)

# close the camera
camera.finishAcquisition()
print("Data is acquired.\n")

# save recieved data
print("Saving data...", end=" ")
for wave_len in WAVE_LEN_ARRAY:
    for i, image in enumerate(images_dict[wave_len]):
        np.savetxt(f"{full_path}\\{wave_len}\\{i}.csv",
                    image,
                    delimiter="\t",
                    fmt="%d")
print("Done!. Experiment has finished.")

