from tkinter import *
from os import path
# pip install pillow
from PIL import Image, ImageTk
import hp_globals as hpg

class GPIO_cfg_panel(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.master = master
        
        # create main window instance
        self.main_window = Toplevel(master)

        # configure main window
        self.main_window.title("Raspberry Pi pin-out config")
        self.main_window.geometry('595x830')
        self.main_window.wm_protocol("WM_DELETE_WINDOW", self.onClose)

        load = Image.open("./assets/GPIO_pinout.png")
        render = ImageTk.PhotoImage(load)
        img = Label(self.main_window, image=render)
        img.image = render
        img.place(x=120, y=30)
        xoffs_odd = 5
        xoffs_even = 385
        y_offs = 62
        y_diff = 35
        i = 0
        labels = []

        if path.exists(hpg.GPIO_config_file):         
                with open(hpg.GPIO_config_file,'r') as inf:
                    pin_assoc = eval(inf.read())
        else:
            print('GPIO_config_file is not found')
            

        for key in pin_assoc:
            labels.append(Label(self.main_window, text = pin_assoc[key]))
            #str_var.set(pin_assoc[key])
            if i%2 == 0:
                labels[i].place(x = xoffs_odd, y = y_offs + i/2 * y_diff)
            else:
                labels[i].place(x = xoffs_even, y = y_offs + (i - 1)/2 * y_diff)

            i += 1

        #pwm_freq_str = StringVal()

        pspeed_entry = Label(self.main_window, text = str(hpg.pspeed) + ' %')
        pspeed_entry.place(x = xoffs_even + 105, y = y_offs + 5 * y_diff )
        pwm_freq_str = str(hpg.pwm_freq) +" Hz"
        pwm_freq_entry = Label(self.main_window, text = pwm_freq_str)
        pwm_freq_entry.place(x = xoffs_even + 150, y = y_offs + 5 * y_diff )
        
    def onClose(self):       
        # set the stop event, cleanup the camera, and allow the rest of
        # the quit process to continue
        print("[INFO] closing GPIO_config...")
           
        self.main_window.destroy()

