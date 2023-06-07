######## PiCamera2/OpenCV picture taker for the RPI IR-Cut camera #########

# Author: Petros626
# forked from/oriented on: https://github.com/EdjeElectronics/Image-Dataset-Tools/blob/main/PictureTaker/PictureTaker.py
# Date: 19.04.2023
# Description: 
# This program takes pictures (.png format - 95% quality and 0 compression) from a the RPi IR-Cut 
# camera and saves them in the specified directory. The default directory is 'images' and the
# default resolution is 1920x1080. Additionally lens undistortion with camera calibration algorithm are
# implemented.

# Example usage to save images in a directory named images at 1920x1080 resolution:
# python3 run_camera_config.py --imgdir=images --res=1920x1080

# This code is based off the Picamera2 library examples at:
# https://github.com/raspberrypi/picamera2/tree/a9f7a7d0bac726ab9b3f366ff461ddd62e885f40/examples
# https://docs.opencv.org/4.x/dc/dbb/tutorial_py_calibration.html
# https://betterprogramming.pub/how-to-calibrate-a-camera-using-python-and-opencv-23bab86ca194

from picamera2 import Picamera2
from argparse import ArgumentParser
from keyboard import is_pressed
from termios import tcflush, TCIOFLUSH
from sys import stdin, exit
from libcamera import controls
from json import load
from numpy import array, float64
from cv2 import (
    cvtColor, COLOR_RGBA2RGB, undistort, imshow, getOptimalNewCameraMatrix, destroyAllWindows,
    namedWindow, WINDOW_NORMAL, startWindowThread, resizeWindow, moveWindow
)
import cProfile

parser = ArgumentParser()
parser.add_argument("--res", help = "Required resolution in WxH. To avoid erros find out about the supported resolutions of your camera model.",
                       default = "1920x1080")
args = parser.parse_args()

if not "x" in args.res:
    print("Specify resolution with x as WxH. (Example: 1920x1080).")
    exit()
imgW, imgH = map(int, args.res.split("x"))

tuning_file = Picamera2.load_tuning_file("ov5647_custom.json")
picam2 = Picamera2(tuning=tuning_file)
# Set options for saving images
picam2.options["quality"] = 95 # best quality
picam2.options["compress_level"] = 0 # no compression

picam2.configure(picam2.create_preview_configuration(main={"format": "RGB888", "size": (1920, 1080)}, controls={"NoiseReductionMode":controls.draft.NoiseReductionModeEnum.HighQuality}))
picam2.start()

winname = "Calibrated (undistorted) Image taker"
namedWindow(winname, WINDOW_NORMAL)
resizeWindow(winname, 1000, 900)
moveWindow(winname, 915, 72)
startWindowThread()
key_flag = 0

with open("calibrate_camera.json", "r") as f:
    calibration_file = load(f)
mtx = array(calibration_file["mtx"], dtype=float64)
dist = array(calibration_file["dist"], dtype=float64)

try:
    while 1:
        if key_flag == 0:
            key_flag = 1
            # request - faster?
            #request = picam2.capture_request()
            #array = request.make_array("main")
            
            #2 direct capture -faster ?
            array = picam2.capture_array("main")
            
            #new_cv_img = cvtColor(array, COLOR_RGBA2RGB)
            h, w = array.shape[:2]
            optimal_camera_matrix, roi = getOptimalNewCameraMatrix(mtx, dist, (w, h), 0, (w, h))
            dst = undistort(array, mtx, dist, None, optimal_camera_matrix)
            cProfile.run('undistort(array, mtx, dist, None, optimal_camera_matrix)', sort='cumulative')
            imshow(winname, dst)
            #request.release()
        else:
            key_flag = 0
         
        if is_pressed("q"):
            print("\r++++++++++++++++++++++++++++++++++++++++++++++")
            print("\rInterruption: stop preview and close camera...")
            break      
finally:
    destroyAllWindows()
    picam2.stop()
    picam2.close()
    tcflush(stdin, TCIOFLUSH)
