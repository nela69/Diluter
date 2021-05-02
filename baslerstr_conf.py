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
#     
# def grabBasler(filename_wo_extension, countOfImagesToGrab):
#     # Number of images to be grabbed.


from pypylon import pylon
from pypylon import genicam
from threading import Thread
#from PIL import Image
import hp_globals as hpg

import sys

class BaslerStr_conf:
    def __init__(self, **kwargs):
     
        # The exit code of the sample application.
        exitCode = 0
        self.frame = None
        self.stopped = False  

        try:
            # Create an instant camera object with the camera device found first.
            hpg.bas_camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
            hpg.bas_camera.Open()
            hpg.getBasSettings()
            
            # Set Acquisition frame rate of the camera to 15 frames per second
            # if too high, otherwise bandwidth error
            if int(hpg.cam_acqframerate) > 15:
                hpg.bas_camera.AcquisitionFrameRate.SetValue(15)
                hpg.cam_acqframerate = 15
# 
#             # The parameter MaxNumBuffer can be used to control the count of buffers
#             # allocated for grabbing. The default value of this parameter is 10.
#             self.camera.MaxNumBuffer = 10
            
        except genicam.GenericException as e:
            # Error handling.
            hpg.p_console.write2Console("An exception occurred.")
            hpg.p_console.write2Console(e.GetDescription())
            exitCode = 1
            sys.exit(exitCode)

    def start(self):

        # start the thread to read frames from the video stream
        hpg.t = Thread(target=self.update, args=())
        #hpg.t.daemon = True
        hpg.t.start()
        self.stopped = False
        return self
            # Start the grabbing of c_countOfImagesToGrab images.
            # The camera device is parameterized with a default configuration which
            # sets up free-running continuous acquisition.
            # Camera.StopGrabbing() is called automatically by the RetrieveResult() method
            # when c_countOfImagesToGrab images have been retrieved.
            
    def update(self):
        
        hpg.bas_camera.StartGrabbing()
            
        while hpg.bas_camera.IsGrabbing():
            # Wait for an image and then retrieve it. A timeout of 5000 ms is used.
            grabResult = hpg.bas_camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

            # Image grabbed successfully?
            if grabResult.GrabSucceeded():
                image_bayer = grabResult.GetArray(raw = True)

                # create and configure ImageFormatConverter
                converter = pylon.ImageFormatConverter()
                converter.OutputPixelFormat = pylon.PixelType_RGB8packed

                # convert image to RGB, create NumPy array
                # and save RGB image as color BMP
                converted = converter.Convert(grabResult)
                self.frame = converted.GetArray()

            else:
                print("Error: ", grabResult.ErrorCode, grabResult.ErrorDescription)
                grabResult.Release()
                hpg.bas_camera.Close()
                
            if self.stopped:
                hpg.bas_camera.StopGrabbing()
                grabResult.Release()
                print('Stop grabbing')
                  # hpg.bas_camera.close()
                return


    def read(self):
        # return the frame most recently read
        return self.frame

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True
        

