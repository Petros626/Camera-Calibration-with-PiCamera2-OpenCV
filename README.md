### Camera Calibration with PiCamera2 and/or OpenCV


![combined](https://github.com/Petros626/Camera-Calibration-with-PiCamera2-OpenCV/assets/62354721/6f1f7cef-93df-42df-b728-15e5cc0c9f66)


The new camera stack of the systems Bullseye 32-bit and 64-bit does not work with [OpenCV](https://github.com/opencv/opencv) for video applications, for this you have to activate the old camera stack, but with mismatch of the function of the new library [PiCamera2](https://github.com/raspberrypi/picamera2). 

In principle, it is possible to configure the camera for the [PiCamera2](https://github.com/raspberrypi/picamera2) library using a `tuning_file` (https://www.raspberrypi.com/documentation/computers/camera_software.html#more-about-libcamera). These files are .json files which allow to adjust the adjustable parameters for the specific camera model. The parameters have been determined specifically for each camera sensor, so that a manual calibration (chapter 6 https://datasheets.raspberrypi.com/camera/raspberry-pi-camera-guide.pdf) is normally not necessary. 
If you do, you can consult the documentation of the parameters and experiment with them yourself.

The adjustment of the camera used with this `tuning_file` offers a lot of adjustment, but you cannot fix lens distortion like radial/tangential distortion with it. For this purpose, however, the special camera calibration using [Camera Calibration](https://docs.opencv.org/4.x/dc/dbb/tutorial_py_calibration.html) can be used. 

Thus it is theoretically possible to use the tuning parameters with [PiCamera2](https://github.com/raspberrypi/picamera2) as well as the non-distortion of [OpenCV](https://github.com/opencv/opencv) for the camera recording.

### Current options to use a camera with different API's

|    PiCamera2              |      OpenCV                   |   PiCamera2&OpenCV
|---------------------------|-------------------------------|-------------------|
| - use the .json tuning_file  with a lot of algorithms (12) for RPi cameras | - Enable the old camera-stack for RPi and use the camera calibration for undistortion with the [OpenCV](https://github.com/opencv/opencv) provided algorithms (16) (more than [PiCamera2](https://github.com/raspberrypi/picamera2)) | - works, but the stream is very slow (suggestions for improvement welcome [github_calibtest.py](https://github.com/Petros626/Camera-Calibration-with-PiCamera2-OpenCV/blob/main/github_calibtest.py) [ir_cut_picamera2_array.py](https://github.com/Petros626/Camera-Calibration-with-PiCamera2-OpenCV/blob/main/camera_calibration/ir_cut_picamera2_array.py)) |   


### Howto: camera calibration

If you intend to calibrate your camera independently of [PiCamera2](https://github.com/raspberrypi/picamera2) due to strong distortion, I provide the following scripts. The first script is used for capturing with a 5 second timer, which is basically used for creating the images for the camera calibration.

Take and save pictures with self-triggered timer:
```python
ir_cut_picamera2_timer.py: 
```

This second script loads the calibration images of the default folder "calib_images" you have taken with the `ir_cut_picamera2_timer.py`script. Further you must give the folder, where the undistorted images after calibration get saved. The last argument is the board dimension, which must be given correctly, because many people make a mistake here, which causes that the algorithms can't find all corners and return `False` for some calibration images. 

```python
python3 calibrate_camera.py --imgdir=calib_imabes --savedir=undistorted_images --board=9x6
```

The script needs the destination, where the calibration images for [OpenCV](https://github.com/opencv/opencv) [Camera Calibration](https://docs.opencv.org/4.x/dc/dbb/tutorial_py_calibration.html) get saved. Additionally you can adjust the time before a picture is taken, to position the chessboard before taking the image. To achieve a sufficient accuracy it's recommended to take between 10-20 (or more) images of the chessboard.

```python
sudo python3 ir_cut_picamera2_timer.py --imgdir=calibration_images --res=1920x1080 --time=5
```

__Note__: Further information here [Camera Calibration](https://docs.opencv.org/4.x/dc/dbb/tutorial_py_calibration.html).
