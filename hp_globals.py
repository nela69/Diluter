# Hoplopi global variables
from time import sleep
import datetime
from os import path, listdir
from fractions import Fraction
import RPi.GPIO as GPIO
import tkinter as tki
import GPIO_actuators as Ga
from collections.abc import Mapping
import re
import numpy as np
import imutils
import cv2
from matplotlib import pyplot as plt
from matplotlib import colors as cl

# picamera object
pi_camera = None # pi camera object
bas_camera = None # basler camera object
selected_cam = 0
vs = None # video stream object
picam_config = None
configfile = './config/picamconfig.txt'
GPIO_config_file = './config/GPIO_config.txt'
sequences_path = './sequences'
config_changed = 0
outputPath = "images"
bkg_comp = False
average_updated = True
gs_coeff = [0.2989, 0.5870, 0.1140]
t = None
hp_console = None # console object

current_frame = None
current_bkg = None
# store the accumulated weight factor
accumWeight = 0.1
bkginterval = 1

pump = None
pump1 = None
pump2 = None

valve = None
valve = None
valve = None

heating = None

LED = None
LED1 = None
LED2 = None

laser = None
laser1 = None
laser2 = None

pspeed = 100
pwm_freq = 100


########################### Basler Camera Parameters ###############################

cam_pixformat_enum = ['RGB8', 'YCbCr422_8', 'BayerGR8', 'BayerGR12']
cam_expauto_enum = ['Off', 'Once', 'Continuous']
cam_gainauto_enum = ['Off', 'Once', 'Continuous']
cam_balwhiteauto_enum = ['Off', 'Once', 'Continuous']

cropx_low = 0
cropy_low = 0
cropx_high = 100
cropy_high = 100

def getBasSettings():
    global cam_deviceinfo
    global cam_width
    global cam_height
    global cam_pixformat
    global cam_exptime
    global cam_expauto
    global cam_gain
    global cam_gainauto
    global cam_balwhiteauto
    global cam_acqframerate
    
    cam_deviceinfo = bas_camera.GetDeviceInfo().GetModelName()
    cam_width = bas_camera.Width.GetValue()
    cam_height = bas_camera.Height.GetValue()
    cam_pixformat = bas_camera.PixelFormat.GetValue()
    cam_exptime = bas_camera.ExposureTime.GetValue()
    cam_expauto = bas_camera.ExposureAuto.GetValue()
    cam_gain = bas_camera.Gain.GetValue()
    cam_gainauto = bas_camera.GainAuto.GetValue()
    cam_balwhiteauto = bas_camera.BalanceWhiteAuto.GetValue()
    cam_acqframerate = int(bas_camera.AcquisitionFrameRate.GetValue())
   
########################### Pi Camera Parameters ###############################

picam_config = {
                'awb_gains' : [Fraction(0, 1), Fraction(0, 1)],
                'awb_mode' : 'auto',
                'brightness' : 50,
                'contrast' : 50,
                'drc_strength' : 'off',
                'exposure_compensation' : 0,
                'exposure_mode' : 'auto',
                'flash_mode' : 'off',
                'framerate' : 20,
                'framerate_range' : [Fraction(1, 1), Fraction(30, 1)],
                'image_denoise' : True,
                'iso' : 0,
                'meter_mode' : 'average',
                'resolution' : [1680, 1056],
                'rotation' : 0,
                'saturation' : 0,
                'sensor_mode' : 0,
                'sharpness' : 0,
                'shutter_speed' : 0,
                'vflip' : False,
                'video_denoise' : True,
                'zoom' : (0.0, 0.0, 1.0, 1.0),
                'use_video_port' : True,
                'format' : 'bgr',
                'h_flip' : False,
                'resize' : None,
            }

picam_pixformat_enum = ['jpeg', 'png', 'gif', 'bmp', 'yuv', 'rgb', 'rgba', 'bgr', 'bgra']

awb_mode_enum = ['off', 'auto', 'sunlight', 'cloudy', 'shade', 'tungsten', 'fluorescent', 'incandescent', 'flash', 'horizon']

# dynamic range compression strength
drc_strength_enum = ['off', 'low', 'medium', 'high']

exposure_mode_enum = ['off', 'auto', 'night', 'nightpreview', 'backlight',
                      'spotlight', 'sports', 'snow', 'beach', 'verylong', 'fixedfps', 'antishake', 'fireworks']

meter_mode_enum = ['average', 'spot', 'backlit', 'matrix']

iso_enum = [0, 100, 200, 320, 400, 500, 640, 800]
                      
cropx_low = 0
cropy_low = 0
cropx_high = 100
cropy_high = 100

def getPiCamSettings():
    for ckey in picam_config:
        if not(ckey == 'use_video_port' or ckey == 'format' or ckey == 'h_flip' or ckey == 'resize'):
            picam_config[ckey] = eval('pi_camera.' + ckey)

#print(picam_config)


#     global awb_gains
#     global awb_mode
#     global brightness
#     global contrast
#     global digital_gain  # read-only
#     global exposure_compansation # [-25, 25] default = 0
#     global exposure_speed # read-only, if shutter_speed > 0, exposure_speed = shutter_speed
#     global frame_rate
#     global image_denoise # Boolean, default = False
#     global iso # 100, 200, 320, 400, 500, 640, 800
#     global saturation # [-100, 100]    
#     global sharpness # [-100, 100]    
#     global shutter_speed #
#     global zoom # (0.0, 0.0, 1.0, 1.0)

#######################################################################################
GPIO_config = { 'pump': ['pwm', 17, 18],
#                 'heater_cleaning_temp': ['temperature', 'None'],
#                 'valve_H': ['binary', 'None'],
#                 'valve_in': ['binary', 'None'],
#                 'valve_out': ['binary', 'None'],
#                 'valve_waste': ['binary', 'None'],
#                 'valve_clean': ['binary', 'None'],
                'LED1': ['binary', 13],
                'LED2': ['no_pwm', 24, 23],
                'LED3': ['binary', 26]
                }

def init_GPIO_Config(): # initializing GPIO
    
    global pspeed
    global st_speed
    global st_angle
    global average_updated
    global pumpDir
    
    average_updated = False
            
    global LED1
    global LED2
    global LED3
    global pump
    global stepper
    
# Assigning actuators(GPIO outputs) to pumps, valves and lights
#    GPIO.cleanup()
    pump = Ga.Actuator(17, 27, 18, pwm_freq, pspeed)
    pumpDir = 1
    
    LED1 = Ga.Actuator(13) # 405nm LED
    LED2 = Ga.Actuator(24, 0, 23) # amber LED
#    LED3 = Ga.Actuator(26)
    stepper = Ga.UniStepper(5, 6, 25, 12)
    # stepper = Ga.UniStepper(16,18,13,15)
    
    st_speed = 100
    st_angle = 360

# def init_GPIO_Config(): # initializing GPIO
#     
#     global pspeed
#     global average_updated
#     
#     average_updated = False
#     
#     for key in GPIO_config:
#         if GPIO_config[key][1] != 'None':
#             exec('global ' + key)
#             if GPIO_config[key][0] == 'pwm':
#                 exec(key + ' = Ga.Actuator({}, {}, {}, {})'.format(GPIO_config[key][1], GPIO_config[key][2], 'pwm_freq', 'pspeed'))
#             elif GPIO_config[key][0] == 'no_pwm':
#                 exec(key + ' = Ga.Actuator({}, {})'.format(GPIO_config[key][1], GPIO_config[key][2]))
#             elif GPIO_config[key][0] == 'binary':
#                 exec(key + ' = Ga.Actuator({})'.format(GPIO_config[key][1]))
#             elif GPIO_config[key][0] == 'temperature':
#                 exec(key + ' = Ga.Heater({}, {})'.format(GPIO_config[key][1], GPIO_config[key][2]))

##############################################################
###                 SEQUENCE DEFINITIONS                   ###
##############################################################

# command sequences in dropdown menu. Names should exactly match that of the functions

sequences = []

def listSequences(path):
    sequence_files = listdir(path)
    sequences = []
    for seq in sequence_files:
        seq_file = seq.split('.')
        if seq_file[0][0].isalnum() and len(seq_file) > 1:
            if seq_file[1] == 'txt':
                sequences.append(seq_file[0])

    return sequences

#################### Read Sequences ##########################

def readControlBatch(seq_path, command_config):
    if path.exists(seq_path) == True:

        with open(seq_path,'r') as inf:
            lines = inf.readlines()
            for line in lines:
                if line[0].isalnum():
                    command = line.split(' ')
                    command_str = ''
                    if command[0] == 'wait':
                        wait_time = int(command[1]) / 1000
                        hp_console.write2Console('wait time: ' + str(wait_time) + 's')
                        sleep(wait_time)
                    elif command[0] == 'capture':
                        if len(command) == 3:
                            hp_console.write2Console('Capturing with: ' + command[2][:-1])
                            takeSnapshot(bool(command[1]), command[2][:-1] + '_', False)
                        else:
                            hp_console.write2Console('Invalid number of parameters in script')
                    elif command[0] == 'average_bkg':
                        if len(command) == 2:
                            updateAverage(int(command[1]))                        
                        elif len(command) == 3:
                            updateAverage(int(command[1]), int(command[2]))
                        elif len(command) == 4:
                            updateAverage(int(command[1]), int(command[2]), float(command[3]))
                        elif len(command) == 5:
                            updateAverage(int(command[1]), int(command[2]), float(command[3]), command[4])
                        elif len(command) == 6:
                            updateAverage(int(command[1]), int(command[2]), float(command[3]), command[4], command[5])                            
                    elif command[0] == 'count_fluor_pixels':
                        if len(command) == 2:
                            countColorPixels(command[1])
                        elif len(command) == 3:
                            countColorPixels(command[1], int(command[2]))
                        elif len(command) == 4:
                            countColorPixels(int(command[1]), int(command[2]), float(command[3]))
                        elif len(command) == 5:
                            countColorPixels(int(command[1]), int(command[2]), float(command[3]), command[4])
                        elif len(command) == 6:
                            countColorPixels(int(command[1]), int(command[2]), float(command[3]), float(command[4]), command[5])
                        elif len(command) == 7:
                            countColorPixels(int(command[1]), int(command[2]), float(command[3]), command[4], float(command[5]), command[6])                            
                        elif len(command) == 8:
                            countColorPixels(int(command[1]), int(command[2]), float(command[3]), float(command[4]), command[5], float(command[6]), command[7])
                        elif len(command) == 9:
                            countColorPixels(int(command[1]), int(command[2]), float(command[3]), command[4], float(command[5]), command[6], loat(command[7]), command[8])
                        elif len(command) == 10:
                            countColorPixels(int(command[1]), int(command[2]), float(command[3]), command[4], float(command[5]), command[6], loat(command[7]), command[8], int(command[9]))
                        else:
                            countColorPixels()
                    elif command[0] in command_config.keys():
                        if GPIO_config[command[0]][0] == 'pwm':
                            if int(command[1]) == 1:
                                command_str = command[0] + '.On()'
                            elif int(command[1]) == 0:
                                command_str = command[0] + '.Off()'
                            else:
                                command_str = command[0] + '.setSpeed({})'.format(int(command[1]))
                        elif  GPIO_config[command[0]][0] == 'binary' or GPIO_config[command[0]][0] == 'no_pwm':
                            if int(command[1]) == 1:
                                command_str = command[0] + '.On()'
                            elif int(command[1]) == 0:
                                command_str = command[0] + '.Off()'
                            elif int(command[1]) == -1:
                                command_str = command[0] + '.Toggle()'
                        elif  GPIO_config[command[0]][0] == 'temperature':
                            command_str = command[0] + '.setTemp({})'.format(int(command[1]))
                        hp_console.write2Console(command_str)
                        exec(command_str)
                    elif command[0] == 'stepper':
                        if len(command) != 3:
                            hp_console.write2Console('invalid number of parameters: ' + command[0])
                        else:
                            stepper.runStepper(int(command[1]), int(command[2]))
                    else:
                        hp_console.write2Console('invalid command: ' + command[0])
    else:
         hp_console.write2Console('No config file')

##############################################################
###                   GLOBAL FUNCTIONS                     ###
##############################################################

def setPiCamConfig():
    if path.exists(configfile) == True:
         
        with open(configfile,'r') as inf:
            picam_config = eval(inf.read())
    #        p_console.write2Console(picam_config)
            for ckey in picam_config:
                if ckey != 'use_video_port':
                    if isinstance(picam_config[ckey], str):                 
                        par_assign = "pi_camera." + ckey + " = '" + str(picam_config[ckey]) + "'"
                    else:
                        par_assign = "pi_camera." + ckey + " = " + str(picam_config[ckey])
                        
                    # print(par_assign)
                    exec(par_assign)
                else:
                    break
                
    else:
        p_console.write2Console('No config file')
         
    return picam_config

def savePiCamConfig():
    
    with open(configfile,'w') as inf:
        inf.write('{\n')
        for ckey in picam_config:
            if isinstance(picam_config[ckey], str):
                inf.write("   '" + ckey + "': '"  + str(picam_config[ckey]) + "',\n")
            else:
                inf.write("   '" + ckey + "': "  + str(picam_config[ckey]) + ",\n")
        inf.write('}')

def updateConfPanel(confpanel):
    for widget in confpanel.winfo_children():
        if not isinstance(widget, tki.Button):
            widget.destroy()
        
    config_labels = []
    for ckey in picam_config:
        if ckey == 'awb_gains' or ckey == 'framerate_range':
            label_text = ckey +': ' + str(picam_config[ckey][0]) + '  ' + str(picam_config[ckey][1])
        else:
            label_text = ckey +': ' + str(picam_config[ckey])
        config_labels.append(tki.Label(confpanel, justify = "left", wraplength = 180, text = label_text))
        config_labels[-1].pack(anchor = "w")
        
def updateConfPanel2(confpanel):
    
    confpanel.sel_cam_width.delete(0, tki.END)
    confpanel.sel_cam_width.insert(0, str(picam_config['resolution'][0]))

    confpanel.sel_cam_height.delete(0, tki.END)
    confpanel.sel_cam_height.insert(0, str(picam_config['resolution'][1]))
    
    confpanel.pf_var.set(picam_config['format'])

    confpanel.sel_cam_exptime.delete(0, tki.END)
    confpanel.sel_cam_exptime.insert(0, str(picam_config['shutter_speed']))

    confpanel.ea_var.set(picam_config['exposure_mode'])
 
    confpanel.sel_cam_gainR.delete(0, tki.END)
    confpanel.sel_cam_gainR.insert(0, str(picam_config['awb_gains'][0]))

    confpanel.sel_cam_gainB.delete(0, tki.END)
    confpanel.sel_cam_gainB.insert(0, str(picam_config['awb_gains'][1]))

    confpanel.ga_var.set(picam_config['awb_mode'])

    confpanel.meter_var.set(picam_config['meter_mode'])

    confpanel.sel_cam_acqframerate.delete(0, tki.END)
    confpanel.sel_cam_acqframerate.insert(0, str(picam_config['framerate']))
    
    confpanel.set_cropx_low.set(cropx_low)
    confpanel.set_cropx_high.set(cropx_high)
    confpanel.set_cropy_low.set(cropy_low)
    confpanel.set_cropy_high.set(cropy_high)
        
def camsettings2console():
    hp_console.write2Console("Using device ", cam_deviceinfo)
    hp_console.write2Console("width: " + str(cam_width) + ' height: ' + str(cam_height))
    hp_console.write2Console("pixelformat: " + cam_pixformat)
    hp_console.write2Console("cam_exptime: " + str(cam_exptime))
    hp_console.write2Console("cam_expauto: " + cam_expauto)
    hp_console.write2Console("cam_gain: " + str(cam_gain))
    hp_console.write2Console("cam_gainauto: " + cam_gainauto)
    hp_console.write2Console("cam_balwhiteauto: " + cam_balwhiteauto)
    hp_console.write2Console("cam_acqframerate: " + str(cam_acqframerate))

def takeSnapshot(bkg_extract = False, f_prefix = 'hp_', show = True):
    # f_prefix + grab the current timestamp and use it to construct the
    # output path
 
    ts = datetime.datetime.now()
    filename = f_prefix + "{}.png".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))
    p = path.sep.join((outputPath, filename))
    # save the file

    if (bkg_extract or bkg_comp) and average_updated:
        image = cv2.absdiff(current_bkg.astype("uint8"), current_frame)
        #image = delta.astype("uint8")
    else:                          
        image = current_frame
        
              
    cv2.imwrite(p, image)
    hp_console.write2Console("[INFO] saved {}".format(p))
    #image = cv2.imread(p)

    if show: # show snapshot in a new window
        # cv2.imshow('snapshot', cv2.normalize(frame_proc,  frame_proc, 0, 255, cv2.NORM_MINMAX))
        cv2.imshow('snapshot', image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
######################################################
###  updating average for background extraction    ###
######################################################

def updateAverage(no_cycl, pumptime = 1000, wait = 2000, coeff = 0.1, def_pump = pump):
    global average_updated
    global bkg_array
       
    if no_cycl >= 0:
        bkg_array = vs.read()
        avg_coeff = 1/(no_cycl + 1)

        for i in range(no_cycl-1):
            pump.On()
            if pumptime >= 0:
                sleep(pumptime/1000)
                pump.Off()
            sleep(wait/1000)
            bkg_array = cv2.addWeighted(bkg_array, 1 - avg_coeff,  vs.read(), avg_coeff, 0)
            hp_console.write2Console('Cumulative mean: ' + str(np.mean(np.mean(bkg_array))))       
             
         
        if pumptime < 0:
            pump.Off()
             
        average_updated = True
#        print(np.mean(np.mean(bkg_array)))
#        print(np.min(np.min(bkg_array)),np.max(np.max(bkg_array)))
#        cv2.imshow('background', np.multiply(bkg_array.astype(float), 1/255))
        cv2.imshow('background', bkg_array)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        hp_console.write2Console("Average updated: " + str(average_updated))
        
    elif average_updated == True:
        bkg_array = cv2.addWeighted(bkg_array, 1 - coeff,  vs.read(), coeff, 0)
    else:
        hp_console.write2Console('Background average not initialized')

######################################################
###  counting pixels of defined color  in image    ###
######################################################

def countColorPixels(rgb_bgr = 'rgb', bkg_extract = 0, R_low=100,G_low=10,B_low=0,R_high=255,G_high=35,B_high=30, bm_iterations = 2):
    
    
    if (bkg_extract or bkg_comp) and average_updated:
        img = cv2.absdiff(current_bkg.astype("uint8"), current_frame)
        #image = delta.astype("uint8")
    else:                          
        img = current_frame
        

#    print(img[500:520, 500:520, :])

    no_pixels = img.shape[0]*img.shape[1]

    if rgb_bgr == 'bgr':
        COLOR_MIN = np.array([B_low, G_low, R_low], np.uint8)
        COLOR_MAX = np.array([B_high, G_high, R_high], np.uint8)
        color = ('b', 'g', 'r')
#         GREEN_MAX = np.array([90, 255, 235], np.uint8)
#         # maximum value of green pixel in BGR order -> green
#         GREEM_MIN = np.array([0, 135, 25], np.uint8)
# 
#         RED_MAX = np.array([30, 35, 255], np.uint8)
#         # maximum value of green pixel in BGR order -> red
#         RED_MIN = np.array([0, 10, 100], np.uint8)
    else:
        COLOR_MIN = np.array([R_low, G_low, B_low], np.uint8)
        COLOR_MAX = np.array([R_high, G_high, B_high], np.uint8)
        color = ('r', 'g', 'b')
#         GREEN_MAX = np.array([235, 255, 90], np.uint8)
#         # maximum value of red pixel in BGR order -> green
#         GREEM_MIN = np.array([25, 135, 0], np.uint8)
# 
#         RED_MAX = np.array([255, 35, 30], np.uint8)
#         # maximum value of red pixel in BGR order -> red
#         RED_MIN = np.array([100, 10, 0], np.uint8)
        
#     dst_green = cv2.inRange(img, GREEM_MIN, GREEN_MAX)
#     no_green = cv2.countNonZero(dst_green)
    dst_color = cv2.inRange(img, COLOR_MIN, COLOR_MAX)
    dst_color = cv2.erode(dst_color, None, bm_iterations)
    no_color = cv2.countNonZero(dst_color)
    
 
    img_sm = imutils.resize(img, width=640)
#      dstg_sm = cv2.cvtColor(imutils.resize(dst_green, width=480), cv2.COLOR_GRAY2BGR)
    dstc_sm = cv2.cvtColor(imutils.resize(dst_color, width=640), cv2.COLOR_GRAY2BGR)
    
#    print(img_sm.shape, dstg_sm.shape, dstr_sm.shape)
   
#    hp_console.write2Console('The number of green pixels is: ' + str(no_green) + '  {:1.4f}'.format(no_green/no_pixels))
    hp_console.write2Console('The number of given color pixels is: ' + str(no_color) + '  {:1.4f}'.format(no_color/no_pixels))
    
#     hor_concat = np.concatenate((np.multiply(img_sm, 1/255), dstc_sm), axis=1)
#     cv2.imshow("Original Image and Color Channel", hor_concat)
#     cv2.waitKey(0)
    

    plt.figure(1)
    plt.imshow(img_sm)
    plt.axis('off')
    
    plt.figure(2)
    plt.imshow(dstc_sm)
    plt.axis('off')
    
    
    plt.figure(3)
    for i,col in enumerate(color):
        histr = cv2.calcHist([img],[i],None,[256],[0,256])
        plt.plot(histr,color = col)
        plt.yscale('log')
    plt.show()
#     f, axarr = plt.subplots(1, 2)
#     axarr[0].imshow(img_sm)
#     axarr[0].set_title("Original Image")
#     axarr[0].axis('off')
# 
#     axarr[1].imshow(dstc_sm)
#     axarr[1].set_title("Filtered Pixels")
#     axarr[1].axis('off')
    
#     plt.subplot(1, 2, 1)
#     plt.imshow(img_sm)
#     plt.subplot(1, 2, 2)
#     plt.imshow(dstc_sm)


     
        
