# -*- coding: utf-8 -*-
"""
Created on July 2025

@author: Teledyne E2V
"""
from sensor import *
from utils import *
from time import sleep
from PIL import Image

# USER PARAMETERS
from sensor import Sensor

# FOR LIVE PREVIEW
import cv2
import numpy as np


INTERVAL_PLOT = 0.0001  # Refresh rate in ms
EXPOSURE_TIME = 100     # Integration time in ms
PIXEL_FORMAT = 12        # 8=8b / 10=10b / 12=12b

#Mouse drag & drop
drawing = False
start_point = None
end_point = None
roi = None


def mouse_callback(event, x, y, flags, param):
    # click start corner and release end corner / right click to reset
    global start_point, end_point, drawing

    if event == cv2.EVENT_LBUTTONDOWN:
        start_point = (x, y)
        end_point = (x+1, y+1)
        drawing = True

    elif event == cv2.EVENT_MOUSEMOVE and drawing:
        end_point = (x, y)

    elif event == cv2.EVENT_LBUTTONUP:
        end_point = (x, y)
        drawing = False
        print(f"Selected ROI : {start_point} -> {end_point} | width={abs(start_point[0]-end_point[0])}, height={abs(start_point[1]-end_point[1])}")

    elif event == cv2.EVENT_RBUTTONDOWN:
        start_point = None
        end_point = None
        print(f"Reset ROI")

#  SIMPLE OBJECT CREATION AND IMAGE ACQUISITION
if __name__ == "__main__":
    print("*******************************************************************")
    print("************** Running Eval Kit Liv preview main loop *************")
    print("*******************************************************************")

    # Open connection
    camera = Sensor()

    if camera is not None:
        # sensor chip-ID check
        addr = 0x7F
        rval = camera.read_sensor_reg(addr)  # Read chipID
        print("RD 0x{:02x} = 0x{:04x}".format(addr, rval))
        sleep(0.5)

        # Setup camera format
        camera.set_camera_format(PIXEL_FORMAT)

        # Sensor parameters
        camera.exposure_time= EXPOSURE_TIME

        # Pixel format and acquisition image size
        if camera.pixel_format == "RGB24":
            shape = (camera.sensor_height, camera.sensor_width * 3)
        else:
            shape = (camera.sensor_height, camera.sensor_width)

        # Get current setting
        print_info(camera)

        print("\nLive preview start")
        preview = True

        if camera.start_acquisition() == 0:
            NBImageAcquired = 0
            NBImageSaved = 0
            # fig = init_figure(camera)
            cv2.namedWindow('Live preview', cv2.WINDOW_AUTOSIZE)
            cv2.setMouseCallback('Live preview', mouse_callback)

            while preview:
                # Get image from internal buffer
                im = camera.get_image()[1]
                NBImageAcquired += 1

                """
                Insert your processing code here
                image is the current image acquired
                """
                # IMAGE PROCESS
                if(roi and (not drawing)):
                    mean = np.mean(imageRoi(im,roi))
                    sigma = np.std(imageRoi(im,roi))
                    # sharp = sharpness(imageRoi(im,roi))
                    sharp = 1
                else:
                    mean = np.mean(im)
                    sigma = np.std(im)
                    # sharp = sharpness(im)
                    sharp = 1

                # DISPLAY
                if(PIXEL_FORMAT==12):
                    image_8bit = cv2.convertScaleAbs(im, alpha=(255.0 / 4095.0))
                elif(PIXEL_FORMAT==10):
                    image_8bit = cv2.convertScaleAbs(im, alpha=(255.0 / 1023.0))
                else:
                    image_8bit = im
                image_rgb = cv2.cvtColor(image_8bit, cv2.COLOR_BGR2RGB)
                display_scale = 4
                image_rgb = cv2.resize(image_rgb, (int(camera.sensor_width/display_scale), int(camera.sensor_height/display_scale)), interpolation=cv2.INTER_AREA)

                # STATISTICS OVERLAY
                text = "Mean={:.2f} | StdDev={:.2f} | Sharpness={:.2f}".format(mean, sigma, sharp)
                cv2.putText(image_rgb, text, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)

                # ROI selection
                if start_point and end_point:
                    roi_start_point=(start_point[0]*display_scale, start_point[1]*display_scale)
                    roi_end_point = (end_point[0] * display_scale, end_point[1] * display_scale)
                    roi=[roi_start_point, roi_end_point]
                    cv2.rectangle(image_rgb, start_point, end_point, (0, 255, 0), 2)
                else:
                    roi = None
                cv2.imshow('Live preview', image_rgb)

                k=cv2.waitKey(1)
                if k == ord('q') or k == 27:
                    print("Live preview stop: {} images".format(NBImageAcquired))
                    preview = False
                elif k == ord('s'):
                    imgName = "EK-image_" + str(NBImageSaved) + ".raw"
                    NBImageSaved += 1
                    with open(imgName, "wb") as f:
                        f.write(im.tobytes())

                # imageProfile(im)
                # update_figure(fig, im, INTERVAL_PLOT, NBImageAcquired)

            # Terminate acquisition
            cv2.destroyAllWindows()
            if camera.stop_acquisition() == 0:
                NBImageAcquired = 0

        else:
            raise Exception("Image acquisition error. Please reboot the camera")

        # Terminate connection
        camera.close()
    else:
        raise Exception("Camera initialization error. Please reboot the camera")
