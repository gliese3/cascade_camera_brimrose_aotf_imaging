import numpy as np
import matplotlib.pyplot as plt
from cascade_camera import CascadeCamera

camera = CascadeCamera()
camera.prepareForAcquisition(hor_bin=2, ver_bin=2, exp_time=5000)
image = camera.getImage()
camera.finishAcquisition()
plt.imshow(image, cmap="jet")
plt.colorbar()
plt.show()