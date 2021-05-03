# import the necessary packages
from __future__ import print_function
from PIL import Image, ImageTk
import tkinter as tki
import threading
import imutils
import cv2
import subprocess
from hpnotes import HoloPiNotes
import hp_globals as hpg
#import seq_control
import sys
import RPi.GPIO as GPIO
import numpy as np
from gpio_config import GPIO_cfg_panel
from sequences import *
import importlib
from baslerstr_conf import BaslerStr_conf
from time import sleep
import console_panel as hpc
import datetime
from os import path


class HoloPiAppPi:
    def __init__(self, outputPath):
        # store the video stream object and output path, then initialize
        # the most recently read frame, thread for reading frames, and
        # the thread stop event
        self.outputPath = outputPath

        self.frame = None
        self.label_im = None
        self.thread = None
        self.stopEvent = None
        
        # initialize the background model
        self.bg = None
        self.delta = None
        self.raw = None
        # initialize the root window and image panel
        # live feed window size
        live_v_w = 960
        live_v_h = 720
        
        confpan_w = 250
        confpan_h = 590
        padding = 5
        console_height = 150
        control_width = 500 
        mainw_w = live_v_w + confpan_w + 3 * padding
        mainw_h = live_v_h + console_height + 3 * padding
        console_width = mainw_w - control_width - 3 * padding
        seqpan_h = live_v_h - confpan_h - padding

        self.root = tki.Tk()
        scr_w = self.root.winfo_screenwidth()
        scr_h = self.root.winfo_screenheight()
        x = int(scr_w/2 - mainw_w/2)
        y = int(scr_h/2 - mainw_h/2)
        
        c = 0.95 * min(scr_w/mainw_w, scr_h/mainw_h)
        
        if c > 1:
            self.live_v_w = round(c * 960) - 1
            live_v_h = round(c * 720) - 1        
            confpan_w= round(c * 250) - 1
            confpan_h = round(c * 590) - 1
            padding = round(c * 5)
            console_height = round(c * 150) - 1
            control_width = round(c * 650) - 1
            mainw_w = self.live_v_w + confpan_w + 3 * padding
            mainw_h = live_v_h + console_height + 3 * padding
            console_width = mainw_w - control_width - 3 * padding
            seqpan_h = live_v_h - confpan_h - padding
            x = int(scr_w/2 - mainw_w/2)
            y = int(scr_h/2 - mainw_h/2)
        else:
            c = 1
            
        confpan_offset = round((mainw_w - self.live_v_w - confpan_w)/2) + self.live_v_w
        
        self.root.geometry(f'{mainw_w}x{mainw_h}+{x}+{y}')

        # set a callback to handle when the window is closed
        self.root.wm_title("HoloPi PiCamera Control Panel")
        self.root.wm_protocol("WM_DELETE_WINDOW", self.onClose)

        # Set panels
        self.panel1 = tki.Frame(self.root)
        self.panel2 = tki.LabelFrame(self.root, text = "PiCamera Settings")
        self.panel3 = tki.LabelFrame(self.root, text = "Controls")
        self.panel4 = tki.LabelFrame(self.root, text = "Sequences")
        self.hp_console_w = tki.LabelFrame(self.root, text = "Console")

        self.panel1.place(x = padding, y = padding, width = live_v_w, height = live_v_h) # panel1 holding live camera fee
        self.panel2.place(x = confpan_offset, y = padding, width = confpan_w, height = confpan_h) # panel2 camera config
        self.panel3.place(x = padding, y = live_v_h + 2*padding, width = control_width, height = console_height) # panel3 control buttons
        self.panel4.place(x = confpan_offset, y = confpan_h + 2*padding, width = confpan_w, height = seqpan_h) # panel4 Sequences
        self.hp_console_w.place(x = control_width  + 2*padding, y = live_v_h + 2*padding, width = console_width, height = console_height) # panel4 Sequences

        # start a thread that constantly pools the video sensor for
        # the most recently read frame
        self.stopEvent = threading.Event()
        self.thread = threading.Thread(target=self.videoLoop, args=())
        self.thread.start()
        
#         ########################### PANEL 2 CONTROLS ########################################
        offset_y = 0.0
        spacing_y = 0.0
                      
        crop_panel = tki.LabelFrame(self.panel2, text = "Image Crop")
        crop_panel.place(relwidth = 0.95, relheight = 0.4, relx = 0.025, rely = 0.53 + offset_y)
        
        clabel = tki.Label(crop_panel, text = "Width:")
        clabel.place(relx = 0.28, rely = 0.4)
        self.sel_cam_width = tki.Spinbox(crop_panel, from_= 64, to = 9998, increment = 2)
        self.sel_cam_width.place(relwidth = 0.25, relx = 0.5, rely = 0.4)
        self.sel_cam_width.delete(0, tki.END)
        self.sel_cam_width.insert(0, hpg.picam_config['resolution'][0])
      
        clabel = tki.Label(crop_panel, text = "Height:")
        clabel.place(relx = 0.28, rely = 0.55)
        self.sel_cam_height = tki.Spinbox(crop_panel, from_= 64, to = 999998, increment = 2)
        self.sel_cam_height.delete(0, tki.END)
        self.sel_cam_height.insert(0, str(hpg.picam_config['resolution'][1]))
        self.sel_cam_height.place(relwidth = 0.25, relx = 0.5, rely = 0.55)        

#         clabel = tki.Label(self.panel2, text = "Width:")
#         clabel.place(relx = 0.01, rely = 0.002 + offset_y)
#         self.sel_cam_width = tki.Spinbox(self.panel2, from_= 64, to = 9998, increment = 2)
#         self.sel_cam_width.place(relwidth = 0.25, relx = 0.21, rely = offset_y)
#         self.sel_cam_width.delete(0, tki.END)
#         self.sel_cam_width.insert(0, hpg.picam_config['resolution'][0])
#       
#         clabel = tki.Label(self.panel2, text = "Height:")
#         clabel.place(relx = 0.48, rely = 0.002 + offset_y)
#         self.sel_cam_height = tki.Spinbox(self.panel2, from_= 64, to = 999998, increment = 2)
#         self.sel_cam_height.delete(0, tki.END)
#         self.sel_cam_height.insert(0, str(hpg.picam_config['resolution'][1]))
#         self.sel_cam_height.place(relwidth = 0.25, relx = 0.71, rely = offset_y)
        
        clabel = tki.Label(self.panel2, text = "Brightness:")
        clabel.place(relx = 0.01, rely = 0.031 + offset_y)
        self.set_brightness = tki.Scale(self.panel2, orient="horizontal", from_ = 0, to = 100, length = 200, command = self.eval_brightness_slide)
        self.set_brightness.set(hpg.picam_config['brightness'])
        self.set_brightness.place(relwidth = 0.6, relx = 0.38, rely =  offset_y)
        
        clabel = tki.Label(self.panel2, text = "Contrast:")
        clabel.place(relx = 0.01, rely = 0.11 + offset_y)
        self.set_contrast = tki.Scale(self.panel2, orient="horizontal", from_ = 0, to = 100, length = 200, command = self.eval_contrast_slide)
        self.set_contrast.set(hpg.picam_config['contrast'])
        self.set_contrast.place(relwidth = 0.6, relx = 0.38, rely = 0.075 + offset_y)         

#         self.pf_var = tki.StringVar(self.panel2)
#         self.pf_var.set(hpg.picam_config['format'])
#         clabel = tki.Label(self.panel2, text = "Pixel Format:")
#         clabel.place(relx = 0.01, rely = 0.07 + offset_y)
#         self.sel_cam_pixformat = tki.OptionMenu(self.panel2, self.pf_var, *hpg.picam_pixformat_enum)
#         self.sel_cam_pixformat.place(relwidth = 0.5, relx = 0.47, rely = 0.05 + offset_y)

        clabel = tki.Label(self.panel2, text = "Shutter Time:")
        clabel.place(relx = 0.01, rely = 0.165 + offset_y)
        self.sel_cam_exptime = tki.Spinbox(self.panel2, from_= 10, to = 9999999, increment = 1000, command = self.eval_shutter_speed_slide)
        self.sel_cam_exptime.delete(0, tki.END)
        self.sel_cam_exptime.insert(0, str(hpg.picam_config['shutter_speed']))
        self.sel_cam_exptime.place(relwidth = 0.35, relx = 0.62, rely = 0.165 + offset_y)

        self.ea_var = tki.StringVar(self.panel2)
        self.ea_var.set(hpg.picam_config['exposure_mode'])
        clabel = tki.Label(self.panel2, text = "Exposure Auto:")
        clabel.place(relx = 0.01, rely = 0.225 + offset_y)
        self.sel_cam_expauto = tki.OptionMenu(self.panel2, self.ea_var, *hpg.exposure_mode_enum)
        self.sel_cam_expauto.place(relwidth = 0.5, relx = 0.47, rely = 0.215 + offset_y)

        clabel = tki.Label(self.panel2, text = "AWB RB Gains:")
        clabel.place(relx = 0.01, rely = 0.285 + offset_y)
        self.sel_cam_gainR = tki.Spinbox(self.panel2, from_= 0, to = 8)
        self.sel_cam_gainR.delete(0, tki.END)
        self.sel_cam_gainR.insert(0, str(hpg.picam_config['awb_gains'][0]))

        self.sel_cam_gainB = tki.Spinbox(self.panel2, width = 3, from_= 0, to = 8)
        self.sel_cam_gainB.delete(0, tki.END)
        self.sel_cam_gainB.insert(0, str(hpg.picam_config['awb_gains'][1]))
        if hpg.picam_config['awb_mode'] != 'off':
            self.sel_cam_gainR.state = tki.DISABLED
            self.sel_cam_gainB.state = tki.DISABLED
        else:
            self.sel_cam_gainR.state = tki.NORMAL
            self.sel_cam_gainB.state = tki.NORMAL
        self.sel_cam_gainR.place(relwidth = 0.25, relx = 0.44, rely = 0.285 + offset_y)    
        self.sel_cam_gainB.place(relwidth = 0.25, relx = 0.74, rely = 0.285 + offset_y)

        self.ga_var = tki.StringVar(self.panel2)
        self.ga_var.set(hpg.picam_config['awb_mode'])
        clabel = tki.Label(self.panel2, text = "AWB:")
        clabel.place(relx = 0.01, rely = 0.35 + offset_y)
        self.sel_cam_gainauto = tki.OptionMenu(self.panel2, self.ga_var, *hpg.awb_mode_enum)
        self.sel_cam_gainauto.place(relwidth = 0.5, relx = 0.47, rely = 0.335 + offset_y)

        self.meter_var = tki.StringVar(self.panel2)
        self.meter_var.set(hpg.picam_config['meter_mode'])
        clabel = tki.Label(self.panel2, text = "Meter Mode")
        clabel.place(relx = 0.01, rely = 0.415 + offset_y)
        self.sel_cam_meter = tki.OptionMenu(self.panel2, self.meter_var, *hpg.meter_mode_enum)
        self.sel_cam_meter.place(relwidth = 0.5, relx = 0.47, rely = 0.405 + offset_y)

        clabel = tki.Label(self.panel2, text = "Acq. Frame Rate:")
        clabel.place(relx = 0.01, rely = 0.48 + offset_y)
        self.sel_cam_acqframerate = tki.Spinbox(self.panel2, from_= 1, to = 20)
        self.sel_cam_acqframerate.place(relwidth = 0.35, relx = 0.62, rely = 0.48 + offset_y)
        self.sel_cam_acqframerate.delete(0, tki.END)
        self.sel_cam_acqframerate.insert(0, str(hpg.picam_config['framerate']))

        
        self.set_cropx_low = tki.Scale(crop_panel, orient="horizontal", from_ = 0, to = 100, length = 200, command = self.eval_cropx_low_slide)
        self.set_cropx_low.set(hpg.cropx_low)
        self.set_cropx_low.place(relwidth = 0.6, relx = 0.25, rely = 0)
        
        self.set_cropx_high = tki.Scale(crop_panel, orient="horizontal", from_ = 0, to = 100, length = 200, command = self.eval_cropx_high_slide)
        self.set_cropx_high.set(hpg.cropx_high)
        self.set_cropx_high.place(relwidth = 0.6, relx = 0.25, rely = 0.77)
        
        self.set_cropy_low = tki.Scale(crop_panel, orient="vertical", from_ = 0, to = 100, length = 200, command = self.eval_cropy_low_slide)
        self.set_cropy_low.set(hpg.cropy_low)
        self.set_cropy_low.place(relheight = 0.55, relx = 0, rely = 0.235)
        
        self.set_cropy_high = tki.Scale(crop_panel, orient="vertical", from_ = 0, to = 100, length = 200, command = self.eval_cropy_high_slide)
        self.set_cropy_high.set(hpg.cropy_high)
        self.set_cropy_high.place(relheight = 0.55, relx = 0.75, rely = 0.235)
        
        grab_btn = tki.Button(self.panel2, text = "Update", pady = 10, command = self.updatePiSettings)
        grab_btn.place(relwidth = 0.42, relheight = 0.05, relx = 0.05, rely = 0.94)
        
         ########################### PANEL 2 file editor CONTROLS ########################################
#         # open Pi cam config file for editing
        edit_cfg_btn = tki.Button(self.panel2, text="Edit Config", pady = 10, justify = "left", height = 1,command = self.editConfig)
        edit_cfg_btn.place(relwidth = 0.42, relheight = 0.05, relx = 0.52, rely = 0.94)
#         
#         # update config panel when config has been changed
#        hpg.updateConfPanel2(self)
#         hpg.updateConfPanel(self.panel2)
#         
#         self.om_var = tki.StringVar(self.panel4)
#         self.om_var.set(hpg.sequences[0])
# 
#         # initialize python editor
#        self.PYTHON_EDITOR = '/usr/bin/thonny'
#        editor = os.environ.get('EDITOR', PYTHON_EDITOR)
        
        ########################### PANEL 3 CONTROLS ########################################
        hpg.init_GPIO_Config()
        
        # create a button, that when pressed, will take the current frame and save it to file
        btn31 = tki.Button(self.panel3, text="Snapshot!", command = lambda: hpg.takeSnapshot())
        btn31.pack(side = tki.LEFT, anchor = tki.NW)
        btn32 = tki.Button(self.panel3, text="LED 1", command = hpg.LED1.Toggle)
        btn32.pack(side = tki.LEFT, anchor = tki.NW)
        btn33 = tki.Button(self.panel3, text="LED 2", command = hpg.LED2.Toggle)
        btn33.pack(side = tki.LEFT, anchor = tki.NW)
#         btn34 = tki.Button(self.panel3, text="LED 3", command = hpg.LED3.Toggle)
#         btn34.pack(side = tki.LEFT, anchor = tki.NW)
        btn35 = tki.Button(self.panel3, text="GPIO Config", command = lambda: GPIO_cfg_panel(self.root))
        btn35.pack(side = tki.LEFT, anchor = tki.NW)
        
        self.check_button_var = tki.BooleanVar()
        self.check_button = tki.Checkbutton(self.panel3, text="bkg extract", variable=self.check_button_var, command = self.setBkgProc)
        self.check_button_var.set(hpg.bkg_comp)
        self.check_button.pack(side = tki.LEFT, anchor = tki.NW)
        
        btn_p = tki.Button(self.panel3, text=" start/stop pump ", command = lambda: hpg.pump.On(hpg.pumpDir))
        btn_p.place(relx = 0, rely = 0.32)
        
        slider_p = tki.Scale(self.panel3, orient="horizontal", from_ = 0, to = 100, length = 200, command = self.setPumpSpeed)
        slider_p.set(hpg.pspeed)
        slider_p.place(relx = 0.35/c, rely = 0.25)
        
        self.btn_pdir = tki.Button(self.panel3, text=" ==> ", command = self.changePumpDir)
        self.btn_pdir.place(relx = 0.78/c, rely = 0.32)
 
        btn_p = tki.Button(self.panel3, text=" run stepper motor ", command = self.runStepper)
        btn_p.place(relx = 0, rely = 0.69)
        
        self.set_st_speed = tki.Scale(self.panel3, orient="horizontal", from_ = 0, to = 100, length = 200)
        self.set_st_speed.set(hpg.st_speed)
        self.set_st_speed.place(relx = 0.35/c, rely = 0.6)
        
        clabel = tki.Label(self.panel3, text = "Rotation angle:")
        clabel.place(relx = 0.78/c, rely = 0.6)
        self.set_st_angle = tki.Spinbox(self.panel3, from_= -9999, to = 9999)
        self.set_st_angle.place(relwidth = 0.13, relx = 0.78/c, rely = 0.76)
        self.set_st_angle.delete(0, tki.END)
        self.set_st_angle.insert(0, str(hpg.st_angle))
        
        steppertype = ['unipolar', 'bipolar']
        self.st_var = tki.StringVar(self.panel3)
        self.st_var.set(steppertype[0])
        self.steppertype_menu = tki.OptionMenu(self.panel3, self.st_var, *steppertype)
        self.steppertype_menu.place(relwidth = 0.15, relx=0.95/c, rely = 0.72)
        
########################### PANEL 4 CONTROLS ########################################
        self.om_var = tki.StringVar(self.panel4)
        self.om_var.set(hpg.sequences[0])

        # initialize python editor
        self.PYTHON_EDITOR = '/usr/bin/thonny'
        #editor = os.environ.get('EDITOR', PYTHON_EDITOR)
        
        self.sequences_menu = tki.OptionMenu(self.panel4, self.om_var, *hpg.sequences)
        self.sequences_menu.place(relwidth = 0.9, relx=0.05, rely = 0)

        self.no_of_cycles = tki.Spinbox(self.panel4, from_= 1, to = 99)
        self.no_of_cycles.place(relwidth = 0.25, relheight = 0.25, relx=0.05, rely =0.35)
        
        btn41 = tki.Button(self.panel4, text="Run Sequence", pady = 10, command=self.runSequence)
        btn41.place(relwidth = 0.6, relheight = 0.25, relx=0.35, rely =0.35)

        btn42 = tki.Button(self.panel4, text="Edit Sequence", pady = 10, command = self.editSeq)
        btn42.place(relwidth = 0.9, relheight = 0.25, relx=0.05, rely =0.66)
        
        ##################################### CONSOLE  ########################################
        
        hpg.hp_console = hpc.hpConsole(self.hp_console_w)
        # hpg.camsettings2console()
             
    ############################### END OF INIT ##############################################    
    ########################### CONTROL COMMAND FUNCTIONS ####################################
    def updateBkg(self, image):
        # if the background model is None, initialize it
        if hpg.current_bkg is None:
            hpg.current_bkg = image.copy().astype("float")
            return
        # update the background model by accumulating the weighted
        # average
        cv2.accumulateWeighted(image, hpg.current_bkg, hpg.accumWeight)
        hpg.average_updated = True

    def setBkgProc(self):
        hpg.bkg_comp = self.check_button_var.get()
#         print(str(hpg.average_updated))
#         if hpg.bkg_comp and not(hpg.average_updated):
#            self.check_button_var.set(False)
#            hpg.bkg_comp = False
#            hpg.hp_console.write2Console('Background average not initialized')

    def runSequence(self):
        seq_module = self.om_var.get()
        hpg.hp_console.write2Console('Running: ' + seq_module)
        hpg.readControlBatch(hpg.sequences_path + '/' + seq_module + '.txt', hpg.GPIO_config)
#         fp_seq_module = importlib.import_module('sequences.' + seq_module)
#         importlib.invalidate_caches()
#         importlib.reload(fp_seq_module)
#         cmd_str = seq_module + '(self.takeSnapshot,' + self.no_of_cycles.get() + ')'
#        hpg.hp_console.write2Console(cmd_str)
#        exec(cmd_str)
        #seq_control.runSeqence(self.om_var.get())
        
    def editConfig(self):
        HoloPiNotes(self, hpg.configfile).open_file()   

    def editSeq(self):
        edit_path = './sequences/' + self.om_var.get() + '.txt'
        hpg.hp_console.write2Console('Editing: ' +  edit_path)
        subprocess.call([self.PYTHON_EDITOR, edit_path])
#        HoloPiNotes(self.root, self.panel2, edit_path).open_file()

    def eval_brightness_slide(self, pic_brightness):
        hpg.picam_config['brightness'] = int(pic_brightness)
        hpg.pi_camera.brightness = hpg.picam_config['brightness']
        
    def eval_contrast_slide(self, pic_contrast):
        hpg.picam_config['contrast'] = int(pic_contrast)
        hpg.pi_camera.contrast = hpg.picam_config['contrast']
        
    def eval_shutter_speed_slide(self):
        hpg.picam_config['shutter_speed'] = int(self.sel_cam_exptime.get())
        hpg.hp_console.write2Console("cam_exptime: " + str(hpg.picam_config['shutter_speed']))
        hpg.pi_camera.shutter_speed = hpg.picam_config['shutter_speed']
    
    def setPumpSpeed(self, speed):
        hpg.pspeed = int(speed) # slider_p.get()
        hpg.pump.setSpeed(hpg.pspeed)

    def changePumpDir(self):
        hpg.pumpDir = -hpg.pumpDir
        if hpg.pumpDir == 1:
            self.btn_pdir.config(text=" ==> ")
        else:
            self.btn_pdir.config(text=" <== ")

    def setStepperSpeed(self, speed):
        hpg.st_speed = int(speed) # slider_p.get()
        
    def runStepper(self):
        hpg.st_speed = int(self.set_st_speed.get())
        hpg.st_angle = int(self.set_st_angle.get())
        hpg.hp_console.write2Console('Running stepper motor @speed:' + str(hpg.st_speed) + ' step/s angle:' + str(hpg.st_angle) + ' degree')
        steppertype = self.st_var.get()
        hpg.stepper.runStepper(hpg.st_speed, hpg.st_angle, steppertype)
        
    def eval_cropx_low_slide(self, s_cropx_low):
        hpg.cropx_low = int(s_cropx_low)
        hpg.cropx_high = self.set_cropx_high.get()
        
        if hpg.cropx_high < hpg.cropx_low + 16:
            self.set_cropx_high.set(hpg.cropx_low + 16)
            
    def eval_cropy_low_slide(self, s_cropy_low):
        hpg.cropy_low = int(s_cropy_low)
        hpg.cropy_high = self.set_cropy_high.get()
        
        if hpg.cropy_high < hpg.cropy_low + 16:
            self.set_cropy_high.set(hpg.cropy_low + 16)
            
    def eval_cropx_high_slide(self, s_cropx_high):
        hpg.cropx_high = int(s_cropx_high)
        hpg.cropx_low = self.set_cropx_low.get()
        
        if hpg.cropx_high - 16 < hpg.cropx_low:
            self.set_cropx_low.set(hpg.cropx_high - 16)
            
    def eval_cropy_high_slide(self, s_cropy_high):
        hpg.cropy_high = int(s_cropy_high)
        hpg.cropy_low = self.set_cropy_low.get()
        
        if hpg.cropy_high - 16 < hpg.cropy_low:
            self.set_cropy_low.set(hpg.cropy_high - 16)
            
    def updatePiSettings(self):
        # stopping grabbing thread
#         hpg.vs.stop()
#         hpg.t.join()
#         hpg.hp_console.write2Console('Stop grabbing')
        
        hpg.picam_config['resolution'] = [int(self.sel_cam_width.get()), int(self.sel_cam_height.get())]
        hpg.pi_camera.resolution = hpg.picam_config['resolution']
        hpg.hp_console.write2Console('width, height: ' + str(hpg.picam_config['resolution']))
        
#         hpg.picam_config['format'] = self.pf_var.get()
#         hpg.hp_console.write2Console("pixelformat: " + hpg.picam_config['format'])
#        hpg.pi_camera.format = hpg.picam_config['format']

        hpg.picam_config['shutter_speed'] = int(self.sel_cam_exptime.get())
        hpg.hp_console.write2Console("cam_exptime: " + str(hpg.picam_config['shutter_speed']))
        hpg.pi_camera.shutter_speed = hpg.picam_config['shutter_speed']
       
        hpg.picam_config['exposure_mode'] = self.ea_var.get()
        hpg.hp_console.write2Console("cam_expauto: " + hpg.picam_config['exposure_mode'])
        hpg.pi_camera.exposure_mode = hpg.picam_config['exposure_mode']
        
        hpg.picam_config['awb_gains'] = [float(self.sel_cam_gainR.get()), float(self.sel_cam_gainB.get())]
        hpg.hp_console.write2Console("cam_gain: " + str(hpg.picam_config['awb_gains']))
        hpg.pi_camera.awb_gains = hpg.picam_config['awb_gains']
        
        hpg.picam_config['awb_mode'] = self.ga_var.get()
        hpg.hp_console.write2Console("cam_gainauto: " + hpg.picam_config['awb_mode'])
        hpg.pi_camera.awb_mode = hpg.picam_config['awb_mode']
        if hpg.picam_config['awb_mode'] != 'off':
            self.sel_cam_gainR.state = tki.DISABLED
            self.sel_cam_gainB.state = tki.DISABLED
        else:
            self.sel_cam_gainR.state = tki.NORMAL
            self.sel_cam_gainB.state = tki.NORMAL
#         self.sel_cam_gainR.place(relwidth = 0.25, relx = 0.74, rely = 0.285 + offset_y)
#         self.sel_cam_gainB.place(relwidth = 0.25, relx = 0.74, rely = 0.285 + offset_y)
        
        hpg.picam_config['meter_mode'] = self.meter_var.get()
        hpg.hp_console.write2Console("meter_mode: " + hpg.picam_config['meter_mode'])
        hpg.pi_camera.meter_mode = hpg.picam_config['meter_mode']
        
        hpg.picam_config['framerate'] = int(self.sel_cam_acqframerate.get())
        hpg.hp_console.write2Console("cam_acqframerate: " + str(hpg.picam_config['framerate']))
        hpg.pi_camera.framerate = hpg.picam_config['framerate']
        
     
        hpg.picam_config['zoom'] = (hpg.cropx_low/100, hpg.cropy_low/100, hpg.cropx_high/100, hpg.cropy_high/100)
        hpg.pi_camera.zoom = hpg.picam_config['zoom']
        #print(hpg.picam_config['zoom'])
        
        hpg.savePiCamConfig()
        
#        sleep(1)
        # starting grabbing thread
#         hpg.vs.start()
#         hpg.hp_console.write2Console('Start grabbing')
        
    ########################### CAMERA CONTROL FUNCTIONS ####################################
    def videoLoop(self):
        # set interval for backgroud update
        nframes = hpg.bkginterval
        
        # This try/except statement is a pretty ugly hack to get around
        # a RunTime error that Tkinter throws due to threading    
        try:
        # keep looping over frames until we are instructed to stop
            while not self.stopEvent.is_set():
                # grab the frame from the video stream and resize it to
                # have a maximum width of 960 pixels
                hpg.current_frame = hpg.vs.read()
                self.updateBkg(hpg.current_frame)

                self.frame = imutils.resize(hpg.current_frame, width=self.live_v_w)
                self.current_bkg = imutils.resize(hpg.current_bkg, width=self.live_v_w)

                # OpenCV represents images in BGR order; however PIL
                # represents images in RGB order, so we need to swap
                # the channels, then convert to PIL and ImageTk format
                if nframes == 0:
                    bkgavg = self.current_bkg.astype("uint8")
                    nframes = hpg.bkginterval                
                nframes -= 1
                
               
                if hpg.bkg_comp and hpg.average_updated:
                    self.delta = cv2.absdiff(bkgavg, self.frame)
                    image = cv2.cvtColor(self.delta.astype("uint8"), cv2.COLOR_BGR2RGB)
                else:                          
                    image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                    
                image = Image.fromarray(image)
                    
                image = ImageTk.PhotoImage(image)

                # if the panel is not None, we need to initialize it
                if self.label_im is None:
                    self.label_im = tki.Label(self.panel1,image=image)
                    self.label_im.image = image
                    self.label_im.pack(side="left", padx=5, pady=5)
                # otherwise, simply update the panel
                else:
                    self.label_im.configure(image=image)
                    self.label_im.image = image
        except RuntimeError:
            print("[INFO] caught a RuntimeError")

        
    ########################### CLOSING HOLOPI APP ####################################

    def onClose(self):
        # set the stop event, cleanup the camera, and allow the rest of
        # the quit process to continue
        hpg.hp_console.write2Console("[INFO] closing...")
        hpg.pi_camera.shutter_speed = 0
        self.stopEvent.set()
        hpg.vs.stop()
        self.root.destroy()
        GPIO.cleanup()
        sys.exit()
