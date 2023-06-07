### Camera Calibration with PiCamera2 and/or OpenCV

The new camera stack of the systems Bullseye 32-bit and 64-bit does not work with [OpenCV](https://github.com/opencv/opencv) for video applications, for this you have to activate the old camera stack, but with mismatch of the function of the new library [PiCamera2](https://github.com/raspberrypi/picamera2). 

In principle, it is possible to configure the camera for the [PiCamera2](https://github.com/raspberrypi/picamera2) library using a `tuning_file` (https://www.raspberrypi.com/documentation/computers/camera_software.html#more-about-libcamera). These files are .json files which allow to adjust the adjustable parameters for the specific camera model. The parameters have been determined specifically for each camera sensor, so that a manual calibration (chapter 6 https://datasheets.raspberrypi.com/camera/raspberry-pi-camera-guide.pdf) is normally not necessary. 
If you do, you can consult the documentation of the parameters and experiment with them yourself.

The adjustment of the camera used with this `tuning_file` offers a lot of adjustment, but you cannot fix lens distortion like radial/tangential distortion with it. For this purpose, however, the special camera calibration using [Camera Calibration](https://docs.opencv.org/4.x/dc/dbb/tutorial_py_calibration.html) can be used. 

Thus it is theoretically possible to use the tuning parameters as well as the non-distortion for the camera recording.

### Current options to use a camera with different API's

|    PiCamera2              |      OpenCV                   |   PiCamera2&OpenCV
|---------------------------|-------------------------------|-------------------|
| - use the .json tuning_file  with a lot of algorithms (12) for RPi cameras | - Enable the old camera-stack for RPi and use the camera calibration for undistortion with the [OpenCV](https://github.com/opencv/opencv) provided algorithms (16) (more than [PiCamera2](https://github.com/raspberrypi/picamera2)) | - works, but the stream is very slow (suggestions for improvement welcome [github_calibtest.py](https://github.com/Petros626/Camera-Calibration-with-PiCamera2-OpenCV/blob/main/github_calibtest.py) [ir_cut_picamera2_array.py] (https://github.com/Petros626/Camera-Calibration-with-PiCamera2-OpenCV/blob/main/camera_calibration/ir_cut_picamera2_array.py)) |   
