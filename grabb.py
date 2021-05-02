# ===============================================================================
#    This sample illustrates how to grab and process images using the CInstantCamera class.
#    The images are grabbed and processed asynchronously, i.e.,
#    while the application is processing a buffer, the acquisition of the next buffer is done
#    in parallel.
#
#    The CInstantCamera class uses a pool of buffers to retrieve image data
#    from the camera device. Once a buffer is filled and ready,
#    the buffer can be retrieved from the camera object for processing. The buffer
#    and additional image data are collected in a grab result. The grab result is
#    held by a smart pointer after retrieval. The buffer is automatically reused
#    when explicitly released or when the smart pointer object is destroyed.
# ===============================================================================
from pypylon import pylon
from pypylon import genicam
#from PIL import Image
from datetime import datetime
import os
import imageio
import tkinter as tki
import cv2
import sys

cam_width = None
cam_height =None
cam_pixformat = None
cam_exptime = None
cam_expauto = None
cam_gain = None
cam_gainauto = None
cam_balwhiteauto = None
cam_acqframerate = None

cam_pixformat_enum = ['RGB8', 'YCbCr422_8', 'BayerGR8', 'BayerGR12']
cam_expauto_enum = ['Off', 'Once', 'Continuous']
cam_gainauto_enum = ['Off', 'Once', 'Continuous']
cam_balwhiteauto_enum = ['Off', 'Once', 'Continuous']

cropx_low = 0
cropy_low = 0
cropx_high = 100
cropy_high = 100


def grabBasler(filename_wo_extension, countOfImagesToGrab):
    # Number of images to be grabbed.

    # The exit code of the sample application.
    exitCode = 0

    try:
        # Create an instant camera object with the camera device found first.
        camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
        camera.Open()

        
        cam_deviceinfo = camera.GetDeviceInfo().GetModelName()
        cam_width = camera.Width.GetValue()
        cam_height = camera.Height.GetValue()
        cam_pixformat = camera.PixelFormat.GetValue()
        cam_exptime = camera.ExposureTime.GetValue()
        cam_expauto = camera.ExposureAuto.GetValue()
        cam_gain = camera.Gain.GetValue()
        cam_gainauto = camera.GainAuto.GetValue()
        cam_balwhiteauto = camera.BalanceWhiteAuto.GetValue()
        cam_acqframerate = camera.AcquisitionFrameRate.GetValue()

        # Print the model name of the camera.
        print("Using device ", camera.GetDeviceInfo().GetModelName())
        print("width: " + str(cam_width) + 'height: ' + str(cam_height))
        print("pixelformat: " + cam_pixformat)
        print("cam_exptime: " + str(cam_exptime))
        print("cam_expauto: " + cam_expauto)
        print("cam_gain: " + str(cam_gain))
        print("cam_gainauto: " + cam_gainauto)
        print("cam_balwhiteauto: " + cam_balwhiteauto)
        print("cam_acqframerate: " + str(cam_acqframerate))

        # demonstrate some feature access
        # new_width = camera.Width.GetValue() - camera.Width.GetInc()

        # camera.Width.SetValue(1280)
        # camera.Height.SetValue(960)

        # print("Increments to change Width and Height:", camera.Width.GetInc(), camera.Height.GetInc())

        #PixelFormat_RGB8, PixelFormat_YCbCr422_8, PixelFormat_BayerGR8, PixelFormat_BayerGR12
        # camera.PixelFormat.SetValue(YCbCr422_8)

        # ExposureAuto_Off, ExposureAuto_Once, ExposureAuto_Continuous
        # camera.ExposureAuto.SetValue(Off)
        # camera.ExposureTime.SetValue(100000)

        # Off, GainAuto_Once,GainAuto_Continuous
        # camera.GainAuto.SetValue(Continuous)
        # camera.Gain.SetValue(4.0484)

        # Off, BalanceWhiteAuto_Once,BalanceWhiteAuto_Continuous
        # camera.BalanceWhiteAuto.SetValue(Continuous)

        # Acquisition frame rate of the camera in frames per second
        # camera.AcquisitionFrameRate.SetValue(100000);

    #     if new_width >= camera.Width.GetMin():
    #         camera.Width.SetValue(new_width)

        # The parameter MaxNumBuffer can be used to control the count of buffers
        # allocated for grabbing. The default value of this parameter is 10.
        camera.MaxNumBuffer = 10

        # Start the grabbing of c_countOfImagesToGrab images.
        # The camera device is parameterized with a default configuration which
        # sets up free-running continuous acquisition.
        camera.StartGrabbingMax(countOfImagesToGrab)

        # Camera.StopGrabbing() is called automatically by the RetrieveResult() method
        # when c_countOfImagesToGrab images have been retrieved.
        while camera.IsGrabbing():
            # Wait for an image and then retrieve it. A timeout of 5000 ms is used.
            grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

            # Image grabbed successfully?
            if grabResult.GrabSucceeded():
                # Access the image data.
    #             print("SizeX: ", grabResult.Width)
    #             print("SizeY: ", grabResult.Height)
    #             img = Image.fromarray(grabResult.Array)

                # create NumPy array from BayerBG8 grab result
                # and save Bayer raw image as grayscale BMPid
                now = datetime.now()
                timestamp = str(int(10 * datetime.timestamp(now)))


                image_bayer = grabResult.GetArray(raw = True)
                filename = timestamp +'.bmp'
                print(filename)
    #            imageio.imsave(timestamp + '.bmp', image_bayer)

                # create and configure ImageFormatConverter
                converter = pylon.ImageFormatConverter()
                converter.OutputPixelFormat = pylon.PixelType_RGB8packed

                # convert image to RGB, create NumPy array
                # and save RGB image as color BMP
                converted = converter.Convert(grabResult)
                image_rgb = converted.GetArray()
#                imageio.imsave(filename_wo_extension + timestamp + '_rgb.bmp', image_rgb)

    #            os.system('xdg-open '+ filename)
                # os.system('xdg-open ' + filename_wo_extension + timestamp + '_rgb.bmp')

                # print("Gray value of first pixel: ", img[0, 0])

                return image_rgb
            else:
                print("Error: ", grabResult.ErrorCode, grabResult.ErrorDescription)
            grabResult.Release()
        camera.Close()

    except genicam.GenericException as e:
        # Error handling.
        print("An exception occurred.")
        print(e.GetDescription())
        exitCode = 1

    sys.exit(exitCode)

def onClose():
    root.destroy()

def grab():
    bas_frame = grabBasler('images/holopiBas', 1)
    cv2.imshow('grab', bas_frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
        
def eval_cropx_low_slide(s_cropx_low):
    cropx_low = int(s_cropx_low)
    cropx_high = set_cropx_high.get()
    
    if cropx_high < cropx_low + 16:
        set_cropx_high.set(cropx_low + 16)
        
def eval_cropy_low_slide(s_cropy_low):
    cropy_low = int(s_cropy_low)
    cropy_high = set_cropy_high.get()
    
    if cropy_high < cropy_low + 16:
        set_cropy_high.set(cropy_low + 16)
        
def eval_cropx_high_slide(s_cropx_high):
    cropx_high = int(s_cropx_high)
    cropx_low = set_cropx_low.get()
    
    if cropx_high - 16 < cropx_low:
        set_cropx_low.set(cropx_high - 16)
        
def eval_cropy_high_slide(s_cropy_high):
    cropy_high = int(s_cropy_high)
    cropy_low = set_cropy_low.get()
    
    if cropy_high - 16 < cropy_low:
        set_cropy_low.set(cropy_high - 16)

if __name__ == '__main__':

    root = tki.Tk()
    root.geometry("250x620")
    root.wm_protocol("WM_DELETE_WINDOW", onClose)

    offset_y = 0.02
    spacing_y = 0.05
    
    
    panel2 = tki.LabelFrame(root, text = "Camera Settings")
    panel2.place(x = 5, y = 5, width = 240, height = 610)
    
    crop_panel = tki.LabelFrame(panel2, text = "Image Crop")
    crop_panel.place(relwidth = 0.95, relheight = 0.4, relx = 0.025, rely = 0.5 + offset_y)

    clabel = tki.Label(panel2, text = "Width:")
    clabel.place(relx = 0, rely = 0.012 + offset_y)
    sel_cam_width = tki.Spinbox(panel2, from_= 64, to = 9998, increment = 2)
    # sel_cam_width.insert(0, str(cam_width))
    sel_cam_width.place(relwidth = 0.25, relx = 0.21, rely = 0.01 + offset_y)
    clabel = tki.Label(panel2, text = "Height:")
    clabel.place(relx = 0.48, rely = 0.012 + offset_y)
    sel_cam_height = tki.Spinbox(panel2, from_= 64, to = 999998, increment = 2)
    sel_cam_height.place(relwidth = 0.25, relx = 0.71, rely = 0.01 + offset_y)

    pf_var = tki.StringVar(panel2)
    pf_var.set(cam_pixformat_enum[0])
    clabel = tki.Label(panel2, text = "Pixel Format:")
    clabel.place(relx = 0, rely = 0.07 + offset_y)
    sel_cam_pixformat = tki.OptionMenu(panel2, pf_var, *cam_pixformat_enum)
    sel_cam_pixformat.place(relwidth = 0.5, relx = 0.47, rely = 0.06 + offset_y)

    clabel = tki.Label(panel2, text = "Exposure Time:")
    clabel.place(relx = 0, rely = 0.13 + offset_y)
    sel_cam_exptime = tki.Spinbox(panel2, from_= 10, to = 9999999, increment = 1000)
    sel_cam_exptime.place(relwidth = 0.35, relx = 0.62, rely = 0.13 + offset_y)

    ea_var = tki.StringVar(panel2)
    ea_var.set(cam_expauto_enum[0])
    clabel = tki.Label(panel2, text = "Exposure Auto:")
    clabel.place(relx = 0, rely = 0.19 + offset_y)
    sel_cam_expauto = tki.OptionMenu(panel2, ea_var, *cam_expauto_enum)
    sel_cam_expauto.place(relwidth = 0.5, relx = 0.47, rely = 0.18 + offset_y)

    clabel = tki.Label(panel2, text = "Gain:")
    clabel.place(relx = 0, rely = 0.255 + offset_y)
    sel_cam_gain = tki.Spinbox(panel2, from_= 0, to = 9999)
    sel_cam_gain.place(relwidth = 0.35, relx = 0.62, rely = 0.25 + offset_y)

    ga_var = tki.StringVar(panel2)
    ga_var.set(cam_gainauto_enum[0])
    clabel = tki.Label(panel2, text = "Gain Auto:")
    clabel.place(relx = 0, rely = 0.315 + offset_y)
    sel_cam_gainauto = tki.OptionMenu(panel2, ga_var, *cam_gainauto_enum)
    sel_cam_gainauto.place(relwidth = 0.5, relx = 0.47, rely = 0.30 + offset_y)

    bwa_var = tki.StringVar(panel2)
    bwa_var.set(cam_balwhiteauto_enum[0])
    clabel = tki.Label(panel2, text = "Balance White:")
    clabel.place(relx = 0, rely = 0.38 + offset_y)
    sel_cam_balwhiteauto = tki.OptionMenu(panel2, bwa_var, *cam_balwhiteauto_enum)
    sel_cam_balwhiteauto.place(relwidth = 0.5, relx = 0.47, rely = 0.37 + offset_y)

    clabel = tki.Label(panel2, text = "Acq. Frame Rate:")
    clabel.place(relx = 0, rely = 0.445 + offset_y)
    sel_cam_acqframerate = tki.Spinbox(panel2, from_= 0, to = 999)
    sel_cam_acqframerate.place(relwidth = 0.35, relx = 0.62, rely = 0.445 + offset_y)

     
    set_cropx_low = tki.Scale(crop_panel, orient="horizontal", from_ = 0, to = 100, length = 200, command = eval_cropx_low_slide)
    set_cropx_low.set(cropx_low)
    set_cropx_low.place(relwidth = 0.6, relx = 0.25, rely = 0)
    
    set_cropx_high = tki.Scale(crop_panel, orient="horizontal", from_ = 0, to = 100, length = 200, command = eval_cropx_high_slide)
    set_cropx_high.set(cropx_high)
    set_cropx_high.place(relwidth = 0.6, relx = 0.25, rely = 0.77)
    
    set_cropy_low = tki.Scale(crop_panel, orient="vertical", from_ = 0, to = 100, length = 200, command = eval_cropy_low_slide)
    set_cropy_low.set(cropy_low)
    set_cropy_low.place(relheight = 0.55, relx = 0, rely = 0.235)
    
    set_cropy_high = tki.Scale(crop_panel, orient="vertical", from_ = 0, to = 100, length = 200, command = eval_cropy_high_slide)
    set_cropy_high.set(cropy_high)
    set_cropy_high.place(relheight = 0.55, relx = 0.75, rely = 0.235)
    
    grab_btn = tki.Button(panel2, text = "Update", pady = 10, command = lambda: print(cropx_low,cropy_low,cropx_high,cropy_high))
    grab_btn.place(relwidth = 0.5, relheight = 0.05, relx = 0.25, rely = 0.93)
    
    root.mainloop()
