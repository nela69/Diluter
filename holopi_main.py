##############################################################
###                       HOLOPI MAIN                      ###
##############################################################

######################## Version 1.4 #########################

# Displaying a video feed with OpenCV and Tkinter
# import the necessary packages
from __future__ import print_function
from holopi_app_bas import HoloPiAppBas
# from holopi_app_pi import HoloPiAppPi
from holopi_app_pi2 import HoloPiAppPi
from pividstr_conf2 import PiVidStr_Conf
from baslerstr_conf import BaslerStr_conf
import time
import hp_globals as hpg
import camera_selector as cs
import sys

hpg.sequences = hpg.listSequences(hpg.sequences_path)
average_updated = False

cam_select = cs.selectCamera()
print(hpg.selected_cam)
# initialize the video stream and allow the camera sensor to warmup

if hpg.selected_cam == 0:
    print("Exiting...")
    sys.exit()
elif hpg.selected_cam == 1:
    print('Pi camera is starting...')
    hpg.vs = PiVidStr_Conf().start()
    print("[INFO] warming up camera...")
    time.sleep(2.0)
    # start the app
    pba = HoloPiAppPi(hpg.outputPath)
elif hpg.selected_cam == 2:
    print('Basler camera is starting...')
    hpg.vs = BaslerStr_conf().start()
    print("[INFO] warming up camera...")
    time.sleep(2.0)
    # start the app
    pba = HoloPiAppBas(hpg.outputPath)

pba.root.mainloop()
