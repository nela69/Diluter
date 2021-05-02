from picamera import PiCamera
from pypylon import pylon
import tkinter as tk
import hp_globals as hpg

class selectCamera:
    def __init__(self):
        
        try:
            pi_camera = PiCamera()
            self.picam = True
            pi_camera.close()
        except:
            self.picam = False
            print('No pi camera')
            
        try:
            self.bas_camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
            self.cam_deviceinfo = self.bas_camera.GetDeviceInfo().GetModelName()
            self.bascam = True
            if self.picam:
                self.popUpSelect()
            else:
                hpg.selected_cam = 2
        except:
            self.bascam = False
            print('No basler camera')
            if self.picam:
                hpg.selected_cam = 1
            else:
                self.popUpSelect()

    def popUpSelect(self):

        self.root = tk.Tk()

        app_w = 275
        app_h = 150
        scr_w = self.root.winfo_screenwidth()
        scr_h = self.root.winfo_screenheight()
        x = int(scr_w/2 - app_w/2)
        y = int(scr_h/2 - app_h/2)
        
        self.root.geometry(f'{app_w}x{app_h}+{x}+{y}')

        self.v = tk.StringVar(self.root, "0")
        self.root.wm_title("Camera Selector")
        self.root.wm_protocol("WM_DELETE_WINDOW", self.returnVal)
        
        tk.Label(self.root, text = 'Please Select Camera').pack(ipady = 10)

        if self.picam and self.bascam:
            tk.Radiobutton(self.root, text = 'Pi Camera', width = 20, height = 1, variable = self.v,  
                        value = '1', indicator = 0, command = self.returnVal).pack(ipady = 10) 
            tk.Radiobutton(self.root, text = self.cam_deviceinfo, width = 20, height = 1, variable = self.v,  
                        value = '2', indicator = 0, command = self.returnVal).pack(ipady = 10)
            
        elif not(self.picam) and not(self.bascam):
            tk.Button(self.root, text = "No available camera, exiting...", width = 30,
                      height = 1, command = self.returnVal).pack(ipady = 15)
               
           
        self.root.mainloop()
        
    def returnVal(self):
        global selected_cam
        hpg.selected_cam = int(self.v.get())
        self.root.destroy()
          



