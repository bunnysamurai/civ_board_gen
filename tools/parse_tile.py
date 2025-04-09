#!/usr/bin/env python

'''
    So, what does this do?

    Reads a tile .jpg

    segregates the 4 tiles in the image by cropping a square shape around them

    displays the results for inspection
    
    resizes the square crops to the same size

    writes all 4 to disk as separate images
'''
import os
import argparse
from PIL import Image
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from skimage.filters import threshold_otsu
from skimage.segmentation import clear_border
from skimage.measure import label, regionprops
from skimage.morphology import closing, footprint_rectangle
from skimage.color import rgb2gray, rgb2hsv

FINAL_SIZE = 300

def read_image(filename):
    return Image.open(filename)

def my_convert(image: np.ndarray):
    return image[...,1]

def crop_tiles(image: Image):
    '''
    modified from the example on scikit-image:
        https://scikit-image.org/docs/stable/auto_examples/segmentation/plot_label.html#sphx-glr-auto-examples-segmentation-plot-label-py
    '''

    # apply threshold
    grayimg = my_convert(np.asarray(image))
    bw = grayimg < 240

    # label image regions
    label_image = label(bw)

    TRIM = 0
    result = []
    for region in regionprops(label_image):
        if region.area > 200**2:
            minr, minc, maxr, maxc = region.bbox
            result.append([minc+TRIM, minr+TRIM, maxc-TRIM, maxr-TRIM])

    assert(len(result)>=4)
    return result


def display_results(image: Image, crops):
   
    plt.figure(1)
    for idx, c in enumerate(crops):
        if idx > 3:
            break
        plt.subplot(2,2,idx+1)
        plt.imshow(image.crop(c))

    plt.figure(2)
    plt.imshow(image)

    plt.show()


def write_results(image: Image, crops, name: str):
    assert(len(crops)>=4)
    for idx, c in enumerate(crops):
        image.crop(c).resize([FINAL_SIZE, FINAL_SIZE]).save(f"{name}_{idx}.png")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="STUB")
    parser.add_argument("FILE", type=str, help="Image file of the tile")
    parser.add_argument("--debug", action="store_true", help="Just output figures.  Don't write to file.")

    args = parser.parse_args()

    input_img = read_image(args.FILE)

    tiles = crop_tiles(input_img)

    if args.debug is True:
        display_results(input_img, tiles)
    else:
        base, ext = os.path.splitext(args.FILE)
        write_results(input_img, tiles, base)

else:
    # pass explicitly
    pass


