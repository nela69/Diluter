from picamera import PiCamera
from picamera.array import PiRGBArray
from threading import Thread
import cv2
from os import path
from fractions import Fraction
import hp_globals as hpg

class PiVidStr_Conf:
    def __init__(self, **kwargs):
        # initialize the camera
        hpg.pi_camera = PiCamera()

# set camera parameters
# self.camera.resolution = resolution
# self.camera.framerate = framerate

# set optional camera parameters (refer to PiCamera docs)
# for (arg, value) in kwargs.items():
# setattr(self.camera, arg, value)
        
#        hpg.getPiCamSettings()
        hpg.picam_config = hpg.setPiCamConfig()
        
        print('format: ' + hpg.picam_config['format'])
        print('use video port = ' + str(hpg.picam_config['use_video_port']))

        # initialize the stream
        self.rawCapture = PiRGBArray(hpg.pi_camera, size=hpg.pi_camera.resolution)
        self.stream = hpg.pi_camera.capture_continuous(self.rawCapture,
            format = hpg.picam_config['format'], use_video_port = hpg.picam_config['use_video_port'])

        # initialize the frame and the variable used to indicate
        # if the thread should be stopped
        self.frame = None
        self.stopped = False
    
    def start(self):
        # start the thread to read frames from the video stream
        hpg.t = Thread(target=self.update, args=())
        hpg.t.daemon = True
        hpg.t.start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        for f in self.stream:
            # grab the frame from the stream and clear the stream in
            # preparation for the next frame
            self.frame = f.array
            self.rawCapture.truncate(0)

            # if the thread indicator variable is set, stop the thread
            # and resource camera resources
        if self.stopped:
            self.stream.close()
            self.rawCapture.close()
            hpg.pi_camera.close()
            return

    def read(self):
        # return the frame most recently read
        return self.frame

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True