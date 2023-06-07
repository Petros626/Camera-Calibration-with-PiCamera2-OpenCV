######## Camera calibration for RPI IR-Cut camera #########

# Author: Petros626
# forked from/oriented on: https://learnopencv.com/camera-calibration-using-opencv/
#                          https://automaticaddison.com/how-to-perform-camera-calibration-using-opencv/
# Date: 26.03.2023
# Description: 
# This program takes the calibration images and uses them to calibrate the camera used.
# The calculated parameters to obtain a distortion-free image are saved as a .json file.
# The default directory is 'calib_images' and the default 'board' dimension is '6x9'.

# Example usage to calibrate the camera with ckeckerboard images and defined dimensions:
# python3 calibrate_camera.py --imgdir=calib_images --board=6x9

# This code is based off the OpenCV-Python tutorials at:
# https://docs.opencv.org/4.x/dc/dbb/tutorial_py_calibration.html

from cv2 import (
    TERM_CRITERIA_EPS, TERM_CRITERIA_MAX_ITER, COLOR_BGR2GRAY, CALIB_CB_ADAPTIVE_THRESH, CALIB_CB_FAST_CHECK, CALIB_CB_NORMALIZE_IMAGE, NORM_L2,
    imread, imwrite, imshow, waitKey, destroyAllWindows, cvtColor, undistort, findChessboardCorners, cornerSubPix,
    drawChessboardCorners, calibrateCamera, getOptimalNewCameraMatrix, projectPoints, norm
)
from numpy import mgrid, zeros, float32, asarray
from glob import glob
from time import sleep
from os import getcwd, path, makedirs
from argparse import ArgumentParser
from json import JSONEncoder, dump

#### Parser safety request #####
# Fetch script arguments and define directory names
parser = ArgumentParser()
parser.add_argument("--imgdir", required=True, help = "Folder where the taken images for calibration are located.",
                    default = "calib_images")
parser.add_argument("--savedir", required=True, help = "Folder where the undistorted images are saved.",
                    default = "undistorted_images")
parser.add_argument("--board", help = "Dimensions of your checkerboard on which the calibration shall be applied.",
                    default = "9x6")
args = parser.parse_args()

# Check if dimensions are specified correct
if not "x" in args.board:
    print("Specify dimensions with x as WxH. (Example: 9x6).")
    exit()
number_squares_x, number_squares_y = map(int, args.board.split("x"))

# Set save directory and directory path
cwd = getcwd()
save_dir = args.savedir
dirpath = path.join(cwd, save_dir)
if not path.exists(dirpath):
    makedirs(dirpath)
    
# --imgdir
dirname = args.imgdir
# Set save name
save_name = "undistorted"

#### Setup the real world coordinates of 3D points ####
# Define chessboard dimensions
# Termination criteria with termination type, number of iterations and the accuracy (ε)
CHECKERBOARD = (number_squares_x, number_squares_y)
criteria = (TERM_CRITERIA_EPS + TERM_CRITERIA_MAX_ITER, 30, 0.001)
flags = CALIB_CB_ADAPTIVE_THRESH + CALIB_CB_FAST_CHECK + CALIB_CB_NORMALIZE_IMAGE
# Creating arrays to store vectors of 3D points / 2D points for each checkerboard image
objpoints  = [] # 3D - real world  
imgpoints = [] # 2D - on image
# Setup the object points and create an array 1x54x3
# Create a meshgrid with the size of the checkerboard dimensions 
objp = zeros((1, CHECKERBOARD[0] * CHECKERBOARD[1], 3), float32)
objp[0,:,:2] = mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2) 

#### Get the images and apply find corner algorithm ####
# Print program hints
print("\n#########################")
print("### Camera calibrater ###")
print("#########################")
print("For help run the script with the '--help' option.")
print("To quit the application press 'q'.\n")

# Get the file path for images in the current directory
images = glob(dirname + "/*.png")
print(f"{len(images)} images for calibration found.")
print(f"Start calibration with the {len(images)} calibration images...")

# Iterate through all images
for fname in images:
    img_dist = imread(fname)
    gray = cvtColor(img_dist, COLOR_BGR2GRAY)
    # Find corners on the chessboard
    ret, corners = findChessboardCorners(gray, (number_squares_x, number_squares_y), flags)
    # If found, add object points&image points (after refining them)
    # print("status before: ",ret) # debug print
    
    if ret == True:
        objpoints.append(objp)
        # Refining pixel coordinates for given 2D points
        corners_ = cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        imgpoints.append(corners_)
        # Draw and display the corners and delay the preview
        img_draw = drawChessboardCorners(img_dist, (number_squares_x,number_squares_y), corners_, ret)
        imshow("Pattern draw on Checkerboard", img_draw)
    
    # termination condition    
    if waitKey(750) == ord('q'):
        print("++++++++++++++++++++++++++++++++++++++++++++++")
        print("Interruption: stop preview and calibration...")
        break
    
destroyAllWindows()


#### Calibrate camera, show parameters and show the accuracy ####
# Apply the calibrate algorithm and print them
ret, mtx, dist, rvecs, tvecs= calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
# Refine camera matrix, return optimal camera matrix and rectangular ROI (alpha=1, all pixels retained)
# set alpha=0 keep minimum unwanted pixels, also comment l. 166-167
h, w = img_dist.shape[:2]
optimal_camera_matrix, roi = getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))

# Re-projection error (accuracy of found parameters)
mean_error = 0
for i in range(len(objpoints)):
    imgpoints2, _ = projectPoints(objpoints[i], rvecs[i], tvecs[i], mtx, dist)
    error = norm(imgpoints[i], imgpoints2, NORM_L2) / len(imgpoints2)
    mean_error += error

#Show the parameters output
print("Camera matrix: \n\n", mtx)
print("\n")
print("Distortion coefficient: \n\n",dist)
print("\n")
print("Rotation vectors: \n\n",rvecs)
print("\n")
print("Translation vectors: \n\n",tvecs)
print("\n")
print("New optimal camera matrix: \n\n", optimal_camera_matrix)
sleep(1.5)
print("\n\nEstimated error how accurate parameters are: \n\n{}\n".format(mean_error/len(objpoints)))

#### Save parameters ####
# Dictionary for parameters
calibrate_camera = {}
filename = "calibrate_camera.json"
print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
print("Save the camera parameters to -> {}.\n".format(filename))

for variable in ["ret", "mtx", "dist", "rvecs", "tvecs"]:
    calibrate_camera[variable] = asarray(eval(variable)).tolist() 
with open(filename, "w") as f:
    dump(calibrate_camera, f, indent=4)
 
sleep(1.5)

#### Undistort the image ####
imgnum  = 1
calib_flag = 1
print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
print("Create the undistorted images in preview window and save them.\n")

for fname in images:
    img_dist = imread(fname)  
    # Method 1: Compensate lens distortion (Renunciation of remapping method 2)
    dst = undistort(img_dist, mtx, dist, None, optimal_camera_matrix)
    # Crop the image. Uncomment these following two lines to remove black lines on the edge of the undistorted image
    x, y, w, h = roi
    dst = dst[y:y+h, x:x+w]
    filename = "".join([save_name, "_", str(imgnum), ".png"])
    savepath = path.join(dirpath, filename)
    imwrite(savepath, dst)
    print("Save undistorted image as -> {}.".format(filename))
    imshow("Undistorted images preview", dst)
    imgnum  += 1

    # termination condition
    if waitKey(750) == ord('q'):
        calib_flag = 0
        print("++++++++++++++++++++++++++++++++++++++++++++++")
        print("Interruption: stop preview and calibration...")
        break
    
if calib_flag == 1:
    print("\nCalibration finished succesfully!")
    
destroyAllWindows()  
