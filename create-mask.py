import cv2 as cv
import numpy as np
import os
import sys
from  PIL  import Image

path = "/home/aditasyhari/Project Python/AI/bakteri/dataset/"

for root, subdirs, files in os.walk(path):
    for file in files:
        print(os.path.join(root, file))

        img = cv.imread(os.path.join(root, file))

        #convert the image to grayscale
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

        #blur image to reduce the noise in the image while thresholding
        blur = cv.blur(gray, (10,10))

        #Apply thresholding to the image
        ret, thresh = cv.threshold(blur, 1, 255, cv.THRESH_OTSU)

        #find the contours in the image
        contours, heirarchy = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

        #draw the obtained contour lines(or the set of coordinates forming a line) on the original image
        cv.drawContours(img, contours, -1, (0,255,0), 20)

        #save image
        name_file = os.path.splitext(file)[0]

        # cv.imshow('thresh', thresh)
        # cv.imshow('result', result)
        mask_path = "/home/aditasyhari/Project Python/AI/bakteri/mask"
        cv.imwrite(os.path.join(mask_path, "mask_{}.png".format(name_file)), thresh)
        print("mask berhasil dibuat")


    #     # image_path = "/home/aditasyhari/Project Python/AI/bakteri/image"
    #     # cv.imwrite(os.path.join(image_path, file), img)
    #     # print("selesai")

    #     #show the image
    #     # cv.namedWindow('Contours',cv.WINDOW_NORMAL)
    #     # cv.namedWindow('Thresh',cv.WINDOW_NORMAL)
    #     # cv.imshow('Contours', img)
    #     # cv.imshow('Thresh', thresh)

    #     # if cv.waitKey(0):        #     cv.destroyAllWindows()