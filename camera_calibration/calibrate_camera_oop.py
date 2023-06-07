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

# TODO: add comments for code

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


# Define CameraCalibrator class to calibrate the used camera
class CameraCalibrator():
    # Constructor with instance attributes
    def __init__(self, imgdir, savedir, board):
        self.imgdir = imgdir
        self.savedir = savedir
        self.dirpath = None
        self.board = board
        self.dirname = imgdir
        self.objp = None
        self.images = glob(self.dirname + "/*.png")
        self.img_dist = None
        self.gray = None
        self.ret = None
        self.corners = None
        self.flags = CALIB_CB_ADAPTIVE_THRESH + CALIB_CB_FAST_CHECK + CALIB_CB_NORMALIZE_IMAGE
        self.objpoints = []
        self.criteria = (TERM_CRITERIA_EPS + TERM_CRITERIA_MAX_ITER, 30, 0.001)
        self.imgpoints = []
        self.corners_ = None
        self.img_draw = None
        self.mtx = None
        self.dist = None
        self.rvecs = None
        self.tvecs = None
        self.optimal_camera_matrix = None
        self.roi = None
        self.mean_error = 0
        self.filename = "calibrate_camera.json"
        self.calibrate_camera = {}
        self.dst = None
        self.save_name = "undistorted"
        self.imgnum = 1
        self.calib_flag = 1
     
    # Function to check/initialize given board dimensions 
    def check_board_dimensions(self):
        if not "x" in self.board:
            print("Specify dimensions with x as WxH. (Example: 9x6)")
            exit()
        self.number_squares_x, self.number_squares_y = map(int, self.board.split("x"))
        # set chessboard dimensions
        self.CHECKERBOARD = (self.number_squares_x, self.number_squares_y)
        
        
    # Function to output the user hints    
    def preview(self):
        print("\n#########################")
        print("### Camera calibrater ###")
        print("#########################")
        print("For help run the script with the '--help' option.")
        print("To quit the application press 'q'.\n")
    
    
    # Function to set all directories
    def set_dirs(self):
        cwd = getcwd()
        self.savedir = args.savedir
        self.dirpath = path.join(cwd, self.savedir)
        if not path.exists(self.dirpath):
            makedirs(self.dirpath)    
     
     
    # Function to setup the object points and their grid   
    def setup_3d_points(self):
        self.check_board_dimensions()
        self.objp = zeros((1, self.CHECKERBOARD[0] * self.CHECKERBOARD[1], 3),float32)
        self.objp[0,:,:2] = mgrid[0:self.CHECKERBOARD[0], 0:self.CHECKERBOARD[1]].T.reshape(-1, 2)
        
    
    # Function find/draw the corners on chessboard
    def find_draw_corners(self):
        self.setup_3d_points()
        self.preview()
        print(f"{len(self.images)} images for calibration found.")
        print(f"Start calibration with the {len(self.images)} calibration images...")
        
        for fname in self.images:
            self.img_dist = imread(fname)
            self.gray = cvtColor(self.img_dist, COLOR_BGR2GRAY)
            self.ret, self.corners = findChessboardCorners(self.gray, (self.number_squares_x, self.number_squares_y), self.flags)
            # print("status before: ",self.ret) # debug print
            
            if self.ret == True:
                self.objpoints.append(self.objp)
                # Refining pixel coordinates for given 2D points
                self.corners_ = cornerSubPix(self.gray, self.corners, (11, 11), (-1, -1), self.criteria)
                self.imgpoints.append(self.corners_)
                self.img_draw = drawChessboardCorners(self.img_dist, (self.number_squares_x, self.number_squares_y), self.corners_, self.ret)
                imshow("Pattern draw on Checkerboard", self.img_draw)
                
            if waitKey(750) == ord('q'):
                print("++++++++++++++++++++++++++++++++++++++++++++++")
                print("Interruption: stop preview and calibration...")
                break
        destroyAllWindows()


    # Function execute the camera calibration and output their accuracy
    def run_calibration(self):
        self.find_draw_corners()
        self.ret, self.mtx, self.dist, self.rvecs, self.tvecs= calibrateCamera(self.objpoints, self.imgpoints, self.gray.shape[::-1], None, None)
        h, w = self.img_dist.shape[:2]
        # set alpha=0 keep minimum unwanted pixels, also comment l. 186-187
        self.optimal_camera_matrix, self.roi = getOptimalNewCameraMatrix(self.mtx, self.dist, (w, h), 1, (w, h))
        
        # Calculate the re-projection error (accuracy of found parameters)
        for i in range(len(self.objpoints)):
            imgpoints2, _ = projectPoints(self.objpoints[i], self.rvecs[i], self.tvecs[i], self.mtx, self.dist)
            error = norm(self.imgpoints[i], imgpoints2, NORM_L2) / len(imgpoints2)
            self.mean_error += error  
        self.print_results()
     
     
    # Function output the results of the calibration
    def print_results(self):
        print("Camera matrix: \n\n", self.mtx)
        print("\n")
        print("Distortion coefficient: \n\n", self.dist)
        print("\n")
        print("Rotation vectors: \n\n", self.rvecs)
        print("\n")
        print("Translation vectors: \n\n", self.tvecs)
        print("\n")
        print("New optimal camera matrix: \n\n", self.optimal_camera_matrix)
        sleep(1.5)
        print("\n\nEstimated error how accurate parameters are: \n\n{}\n".format(self.mean_error/len(self.objpoints)))
    
    
    # Function to save the calculated parameters
    def save_calib_params(self):
        print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        print("Save the parameters to -> {}.\n".format(self.filename))
        
        for variable in ["ret", "mtx", "dist", "rvecs", "tvecs"]:
            # Dynamically access the attribute
            self.calibrate_camera[variable] = asarray(getattr(self, variable)).tolist() 
        with open(self.filename, "w") as f:
            dump(self.calibrate_camera, f, indent=4) 
        sleep(1.5)


    # Function to apply the parameters on all images
    def undistort_images_save(self):
        self.set_dirs()
        print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        print("Create the undistorted images in preview window and save them.\n")
                
        for fname in self.images:
            self.img_dist = imread(fname)  
            # Method 1: Compensate lens distortion (Renunciation of remapping method 2)
            self.dst = undistort(self.img_dist, self.mtx, self.dist, None, self.optimal_camera_matrix)
            # Crop the image. Uncomment these following two lines to remove black lines on the edge of the undistorted image
            x, y, w, h = self.roi
            self.dst = self.dst[y:y+h, x:x+w]
            filename = "".join([self.save_name, "_", str(self.imgnum), ".png"])
            savepath = path.join(self.dirpath, filename)
            imwrite(savepath, self.dst)
            print("Save undistorted image as -> {}.".format(filename))
            imshow("Undistorted images preview", self.dst)
            self.imgnum  += 1

            if waitKey(750) == ord('q'):
                self.calib_flag = 0
                print("++++++++++++++++++++++++++++++++++++++++++++++")
                print("Interruption: stop preview and calibration...")
                break
            
        if self.calib_flag == 1:
            print("\nCalibration finished succesfully!")      
destroyAllWindows()         



if __name__ == "__main__":
    # Fetch script arguments
    parser = ArgumentParser()
    parser.add_argument("--imgdir", required=True, help = "Folder where the taken images for calibration are located.",
                    default = "calib_images")
    parser.add_argument("--savedir", required=True, help = "Folder where the undistorted images are saved.",
                    default = "undistorted_images")
    parser.add_argument("--board", help = "Dimensions of your checkerboard on which the calibration shall be applied.",
                    default = "9x6")
    args = parser.parse_args()
    
    # Create an object calibrator of the class
    calibrator = CameraCalibrator(args.imgdir, args.savedir, args.board)
    calibrator.run_calibration()
    calibrator.save_calib_params()
    calibrator.undistort_images_save()