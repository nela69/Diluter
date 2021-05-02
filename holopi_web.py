# OpenCV - Stream video to web browser/HTML page
# import the necessary packages
from imutils.video import VideoStream
import socket
from flask import Response
from flask import Flask
from flask import render_template
# import argparse
import time
import cv2

# initialize the output frame and a lock used to ensure thread-safe
# exchanges of the output frames (useful when multiple browsers/tabs
# are viewing the stream)
outputFrame = None

# getting local ip address
ips = []
ips.append([l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] 
if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), 
s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, 
socket.SOCK_DGRAM)]][0][1]]) if l][0][0])

host= ips[0]
port = 8000

# initialize a flask object
app = Flask(__name__)
# initialize the video stream and allow the camera sensor to
# warmup
#vs = VideoStream(usePiCamera=1).start()
vs = VideoStream(src=0).start()
time.sleep(2.0)

@app.route("/")
def index():
	# return the rendered template
	return render_template("index.html")

def generate():
	# grab global references to the output frame
	global outputFrame
	# loop over frames from the output stream
	while True:
		# the iteration of the loop
		frame = vs.read()
		outputFrame = frame.copy()
		# check if the output frame is available, otherwise skip
		if outputFrame is None:
			continue

		# encode the frame in JPEG format
		(flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
		# ensure the frame was successfully encoded
		if not flag:
			continue
		# yield the output frame in the byte format
		yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
					bytearray(encodedImage) + b'\r\n')
		# wait until the lock is acquired

@app.route("/video_feed")
def video_feed():
	# return the response generated along with the specific media
	# type (mime type)
	return Response(generate(),
		mimetype = "multipart/x-mixed-replace; boundary=frame")

# check to see if this is the main thread of execution
if __name__ == '__main__':
	# start the flask app
	app.run(host, port, debug=True,
			threaded=True, use_reloader=False)

# release the video stream pointer
vs.stop()