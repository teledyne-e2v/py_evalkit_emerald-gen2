# py_evalkit_emerald-gen2
A python code to play with Emerald-Gen2 EVK

## Requirements
Works with Python3.12

Please install the packages list available in `requirements.txt`  

Install `opencv_python` to use `live_preview.py`

Before starting, make sure this path is  correct in the file `sensor.py`:

```DEFAULT_BIN_DIR = r"C:\Program Files\Teledyne e2v\Evalkit-Emeraldgen2\1.0\pigentl\bin"```

## Image Acquisition
The main project file is `image_acquisition.py`

The number of images to acquire can be set with the variable `NIMAGES`

That is also possible to sweep a parameter like the exposure time (in ms). In this case the number of images is valid for each parameter step.

The example saves RAW image + TIFF image and generates some statistics like Mean or StandardDeviation.
Images are displayed and profiles calculated.

For external trigger use, please uncomment lines 40/41 and define a number of frames you want to acquire in total with the variable `NIMAGES`

Feel free to comment the unnecessary functions and add your own processing !

## Live Preview
The main project file is `live_preview.py`

Video stream is started and a window is opened to display the images with some statistics in overlay.
After drawing a rectangle on the image, the statics are calculated for the selected ROI.

That is possible to adjust the exposure time (in ms) with the parameter `EXPOSURE_TIME`

The pixel format can be selected between 8, 10 or 12b with the parameter `PIXEL_FORMAT`

Press `S` to save a RAW image

Press `Q` or `ESC` to stop properly the live preview application