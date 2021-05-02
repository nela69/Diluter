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

class HoloPiAppBas:
    def __init__(self, outputPath):
        # store the video stream object and output path, then initialize
        # the most recently read frame, thread for reading frames, and
        # the thread stop event
        self.outputPath = outputPath

        self.frame = None
        self.label_im = None
        self.thread = None
        self.stopEvent = None

        # initialize the root window and image panel
        # live feed window size
        live_v_w = 960
        live_v_h = 720
        
        right_pan_w= 250
        confpan_h = 590
        padding = 5
        console_height = 150
        control_width = 500 
        mainw_w = live_v_w + right_pan_w + 3 * padding
        mainw_h = live_v_h + console_height + 3 * padding
        console_width = mainw_w - control_width - 3 * padding
        seqpan_h = live_v_h - confpan_h - padding

        self.root = tki.Tk()
        scr_w = self.root.winfo_screenwidth()
        scr_h = self.root.winfo_screenheight()
        x = int(scr_w/2 - mainw_w/2)
        y = int(scr_h/2 - mainw_h/2)
        
        self.root.geometry(f'{mainw_w}x{mainw_h}+{x}+{y}')

        # set a callback to handle when the window is closed
        self.root.wm_title("HoloPi Basler Control Panel")
        self.root.wm_protocol("WM_DELETE_WINDOW", self.onClose)

        # Set panels
        self.panel1 = tki.Frame(self.root)
        self.panel2 = tki.LabelFrame(self.root, text = hpg.cam_deviceinfo + " Settings")
        self.panel3 = tki.LabelFrame(self.root, text = "Controls")
        self.panel4 = tki.LabelFrame(self.root, text = "Sequences")
        self.hp_console_w = tki.LabelFrame(self.root, text = "Console")

        self.panel1.place(x = padding, y = padding, width = live_v_w, height = live_v_h) # panel1 holding live camera fee
        self.panel2.place(x = live_v_w + 2*padding, y = padding, width = right_pan_w, height = confpan_h) # panel2 camera config
        self.panel3.place(x = padding, y = live_v_h + 2*padding, width = control_width, height = console_height) # panel3 control buttons
        self.panel4.place(x = live_v_w  + 2*padding, y = confpan_h + 2*padding, width = right_pan_w, height = seqpan_h) # panel4 Sequences
        self.hp_console_w.place(x = control_width  + 2*padding, y = live_v_h + 2*padding, width = console_width, height = console_height) # panel4 Sequences

        # start a thread that constantly pools the video sensor for
        # the most recently read frame
        self.stopEvent = threading.Event()
        self.thread = threading.Thread(target=self.videoLoop, args=())
        self.thread.start()
        
        ########################### PANEL 2 CONTROLS ########################################
        offset_y = 0.01
        spacing_y = 0.05
                      
        crop_panel = tki.LabelFrame(self.panel2, text = "Image Crop")
        crop_panel.place(relwidth = 0.95, relheight = 0.4, relx = 0.025, rely = 0.5 + offset_y)

        clabel = tki.Label(self.panel2, text = "Width:")
        clabel.place(relx = 0.01, rely = 0.012 + offset_y)
        self.sel_cam_width = tki.Spinbox(self.panel2, from_= 64, to = 9998, increment = 2)
        self.sel_cam_width.delete(0, 3)
        self.sel_cam_width.insert(0, str(hpg.cam_width))
        self.sel_cam_width.place(relwidth = 0.25, relx = 0.21, rely = 0.01 + offset_y)
        
        clabel = tki.Label(self.panel2, text = "Height:")
        clabel.place(relx = 0.48, rely = 0.012 + offset_y)
        self.sel_cam_height = tki.Spinbox(self.panel2, from_= 64, to = 999998, increment = 2)
        self.sel_cam_height.delete(0, 5)
        self.sel_cam_height.insert(0, str(hpg.cam_height))
        self.sel_cam_height.place(relwidth = 0.25, relx = 0.71, rely = 0.01 + offset_y)

        self.pf_var = tki.StringVar(self.panel2)
        self.pf_var.set(hpg.cam_pixformat)
        clabel = tki.Label(self.panel2, text = "Pixel Format:")
        clabel.place(relx = 0.01, rely = 0.07 + offset_y)
        self.sel_cam_pixformat = tki.OptionMenu(self.panel2, self.pf_var, *hpg.cam_pixformat_enum)
        self.sel_cam_pixformat.place(relwidth = 0.5, relx = 0.47, rely = 0.06 + offset_y)

        clabel = tki.Label(self.panel2, text = "Exposure Time:")
        clabel.place(relx = 0.01, rely = 0.13 + offset_y)
        self.sel_cam_exptime = tki.Spinbox(self.panel2, from_= 10, to = 999999, increment = 1000)
        self.sel_cam_exptime.insert(0, '{:1.0f}'.format(hpg.cam_exptime))
        self.sel_cam_exptime.place(relwidth = 0.35, relx = 0.62, rely = 0.13 + offset_y)

        self.ea_var = tki.StringVar(self.panel2)
        self.ea_var.set(hpg.cam_expauto)
        clabel = tki.Label(self.panel2, text = "Exposure Auto:")
        clabel.place(relx = 0.01, rely = 0.19 + offset_y)
        self.sel_cam_expauto = tki.OptionMenu(self.panel2, self.ea_var, *hpg.cam_expauto_enum)
        self.sel_cam_expauto.place(relwidth = 0.5, relx = 0.47, rely = 0.18 + offset_y)

        clabel = tki.Label(self.panel2, text = "Gain:")
        clabel.place(relx = 0.01, rely = 0.255 + offset_y)
        self.sel_cam_gain = tki.Spinbox(self.panel2, from_= 0, to = 9999)
        self.sel_cam_gain.insert(0, str(hpg.cam_gain))
        self.sel_cam_gain.place(relwidth = 0.35, relx = 0.62, rely = 0.25 + offset_y)

        self.ga_var = tki.StringVar(self.panel2)
        self.ga_var.set(hpg.cam_gainauto)
        clabel = tki.Label(self.panel2, text = "Gain Auto:")
        clabel.place(relx = 0.01, rely = 0.315 + offset_y)
        self.sel_cam_gainauto = tki.OptionMenu(self.panel2, self.ga_var, *hpg.cam_gainauto_enum)
        self.sel_cam_gainauto.place(relwidth = 0.5, relx = 0.47, rely = 0.30 + offset_y)

        self.bwa_var = tki.StringVar(self.panel2)
        self.bwa_var.set(hpg.cam_balwhiteauto)
        clabel = tki.Label(self.panel2, text = "Balance White:")
        clabel.place(relx = 0.01, rely = 0.38 + offset_y)
        self.sel_cam_balwhiteauto = tki.OptionMenu(self.panel2, self.bwa_var, *hpg.cam_balwhiteauto_enum)
        self.sel_cam_balwhiteauto.place(relwidth = 0.5, relx = 0.47, rely = 0.37 + offset_y)

        clabel = tki.Label(self.panel2, text = "Acq. Frame Rate:")
        clabel.place(relx = 0.01, rely = 0.445 + offset_y)
        self.sel_cam_acqframerate = tki.Spinbox(self.panel2, from_= 1, to = 20)
        self.sel_cam_acqframerate.delete(0, 10)
        self.sel_cam_acqframerate.insert(0, '{:1.0f}'.format(hpg.cam_exptime))
        self.sel_cam_acqframerate.place(relwidth = 0.35, relx = 0.62, rely = 0.445 + offset_y)
        
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
        
        grab_btn = tki.Button(self.panel2, text = "Update", pady = 10, command = self.updateBasSettings)
        grab_btn.place(relwidth = 0.5, relheight = 0.05, relx = 0.25, rely = 0.93)
        
        
        ########################### PANEL 3 CONTROLS ########################################
        hpg.init_GPIO_Config()
        
        # create a button, that when pressed, will take the current frame and save it to file
        btn31 = tki.Button(self.panel3, text="Snapshot!", command = lambda: hpg.takeSnapshot(False, True))
        btn31.pack(side = tki.LEFT, anchor = tki.NW)
        btn32 = tki.Button(self.panel3, text="LED 1", command = hpg.LED1.Toggle)
        btn32.pack(side = tki.LEFT, anchor = tki.NW)
        btn33 = tki.Button(self.panel3, text="LED 2", command = hpg.LED2.Toggle)
        btn33.pack(side = tki.LEFT, anchor = tki.NW)
        btn34 = tki.Button(self.panel3, text="LED 3", command = hpg.LED3.Toggle)
        btn34.pack(side = tki.LEFT, anchor = tki.NW)
        btn35 = tki.Button(self.panel3, text="GPIO Config", command = lambda : GPIO_cfg_panel(self.root))
        btn35.pack(side = tki.LEFT, anchor = tki.NW)
        
        self.check_button_var = tki.BooleanVar()
        self.check_button = tki.Checkbutton(self.panel3, text="bkg extract", variable=self.check_button_var, command = self.setBkgProc)
        self.check_button_var.set(hpg.bkg_comp)
        self.check_button.pack(side = tki.LEFT, anchor = tki.NW)
        
        btn_p = tki.Button(self.panel3, text=" start/stop pump ", command = hpg.pump.Toggle)
        btn_p.place(relx = 0.15, rely = 0.5)
        
        slider_p = tki.Scale(self.panel3, orient="horizontal", from_ = 0, to = 100, length = 200, command = self.setPumpSpeed)
        slider_p.set(hpg.pspeed)
        slider_p.place(relx = 0.45, rely = 0.42)
      
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
    def setBkgProc(self):
        hpg.bkg_comp = self.check_button_var.get()
        if hpg.bkg_comp and not(hpg.average_updated):
           self.check_button_var.set(False)
           hpg.bkg_comp = False
           hpg.hp_console.write2Console('Background average not initialized')

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
        HoloPiNotes(self.root, self.panel2, hpg.configfile).open_file()   

    def editSeq(self):
        edit_path = './sequences/' + self.om_var.get() + '.txt'
        hpg.hp_console.write2Console('Editing: ' +  edit_path)
        subprocess.call([self.PYTHON_EDITOR, edit_path])
#        HoloPiNotes(self.root, self.panel2, edit_path).open_file()
    
    def setPumpSpeed(self, speed):
        hpg.pspeed = int(speed) # slider_p.get()
        hpg.pump.setSpeed(hpg.pspeed)
        
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
            
    def updateBasSettings(self):
        # stopping grabbing thread
        hpg.vs.stop()
        hpg.t.join()
        hpg.hp_console.write2Console('Stop grabbing')
        
        hpg.cam_width = int(self.sel_cam_width.get())
        hpg.bas_camera.Width.SetValue(int(hpg.cam_width / 2) * 2)
        hpg.cam_height = int(self.sel_cam_height.get())
        hpg.bas_camera.Height.SetValue(int(hpg.cam_height / 2) * 2)
        hpg.hp_console.write2Console("width: " + str(hpg.cam_width) + ' height: ' + str(hpg.cam_height))
        
        hpg.cam_pixformat = self.pf_var.get()
        hpg.hp_console.write2Console("pixelformat: " + hpg.cam_pixformat)
        hpg.bas_camera.PixelFormat.SetValue(hpg.cam_pixformat)
        
        hpg.cam_exptime = float(self.sel_cam_exptime.get())
        hpg.hp_console.write2Console("cam_exptime: " + str(hpg.cam_exptime))
        hpg.bas_camera.ExposureTime.SetValue(hpg.cam_exptime)
        
        hpg.cam_expauto = self.ea_var.get()
        hpg.hp_console.write2Console("cam_expauto: " + hpg.cam_expauto)
        hpg.bas_camera.ExposureAuto.SetValue(hpg.cam_expauto)
        
        hpg.cam_gain = float(self.sel_cam_gain.get())
        hpg.hp_console.write2Console("cam_gain: " + str(hpg.cam_gain))
        hpg.bas_camera.Gain.SetValue(hpg.cam_gain)
        
        hpg.cam_gainauto = self.ga_var.get()
        hpg.hp_console.write2Console("cam_gainauto: " + hpg.cam_gainauto)
        hpg.bas_camera.GainAuto.SetValue(hpg.cam_gainauto)
        
        hpg.cam_balwhiteauto = self.bwa_var.get()
        hpg.hp_console.write2Console("cam_balwhiteauto: " + hpg.cam_balwhiteauto)
        hpg.bas_camera.BalanceWhiteAuto.SetValue(hpg.cam_balwhiteauto)
        
        hpg.cam_acqframerate = float(self.sel_cam_acqframerate.get())
        hpg.hp_console.write2Console("cam_acqframerate: " + str(hpg.cam_acqframerate))
        hpg.bas_camera.AcquisitionFrameRate.SetValue(hpg.cam_acqframerate)
        
       
        cropped_width = int((hpg.cropx_high - hpg.cropx_low) * hpg.cam_width / 200) * 2
        cropped_height = int((hpg.cropy_high - hpg.cropy_low) * hpg.cam_height / 200) * 2
        hpg.hp_console.write2Console('cropped_width: ' + str(cropped_width) + ' cropped_height: ' + str(cropped_height))
        
#         hpg.bas_camera.CenterX.SetValue(False)
#         hpg.bas_camera.CenterY.SetValue(False)
        hpg.bas_camera.Width.SetValue(cropped_width)
        hpg.bas_camera.Height.SetValue(cropped_height)
        hpg.bas_camera.OffsetX.SetValue(int(hpg.cropx_low / 2) * 2)
        hpg.bas_camera.OffsetY.SetValue(int(hpg.cropy_low / 2) * 2)       
              
        sleep(1)
        # starting grabbing thread
        hpg.vs.start()
        hpg.hp_console.write2Console('Start grabbing')
        
    ########################### CAMERA CONTROL FUNCTIONS ####################################
    def videoLoop(self):
        # This try/except statement is a pretty ugly hack to get around
        # a RunTime error that Tkinter throws due to threading
        try:
        # keep looping over frames until we are instructed to stop
            while not self.stopEvent.is_set():
                # grab the frame from the video stream and resize it to
                # have a maximum width of 300 pixels
                self.frame_orig = hpg.vs.read()
                self.frame = imutils.resize(self.frame_orig, width=960)

                # OpenCV represents images in BGR order; however PIL
                # represents images in RGB order, so we need to swap
                # the channels, then convert to PIL and ImageTk format
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
        self.stopEvent.set()
        hpg.vs.stop()
        hpg.t.join()
        self.root.destroy()
        GPIO.cleanup()
        sys.exit()
