# -*- coding: utf-8 -*-
"""
Created on Wed Dec 22 15:49:55 2021

@author: bardi
"""

import os
import pandas as pd
from matplotlib import pyplot as plt
import cv2
import numpy as np






#%% Load and preprocess images as an array for the deep learning models   
def im_preprocess(im_data_in, im_newsize = (224, 224), pp_case = 0, debugging = False):
    
    # make it grayscale  
    im_data_in = cv2.cvtColor(im_data_in, cv2.COLOR_BGR2GRAY)

    
    # Enhancing the edges
    if pp_case == 1:
        # Edge Detection
        img_blur = cv2.GaussianBlur(im_data_in, (3,3), sigmaX=0, sigmaY=0)
        im_data_enhanced = auto_canny(img_blur)
        
        # Blend Images
        alpha = 0.5
        beta = (1.0 - alpha)
        im_blend = cv2.addWeighted(im_data_in, alpha, im_data_enhanced, beta, 0.0)
        
        im_data_in = im_blend
        
        
    # Resize and Pad
    im_data_out = cv2_resize_with_padding(im_data_in, im_newsize)
    
    
    if debugging:
        fig, ax = plt.subplot_mosaic([['input', 'preprocessed']], figsize=(8, 4))
    
        ax['input'].imshow(im_data_in, cmap='gray')
        ax['input'].set_title('Input (B&W)')
        ax['input'].axis('off')  # clear x-axis and y-axis
    
        ax['preprocessed'].imshow(im_data_out, cmap='gray')
        ax['preprocessed'].set_title('Preprocessed')
        ax['preprocessed'].axis('off')  # clear x-axis and y-axis

        plt.show()
    
    return im_data_out
    



#%% Edge Detection - OpenCV
def auto_canny(image, sigma=0.33):
	# compute the median of the single channel pixel intensities
	v = np.median(image)
	# apply automatic Canny edge detection using the computed median
	lower = int(max(0, (1.0 - sigma) * v))
	upper = int(min(255, (1.0 + sigma) * v))
	edged = cv2.Canny(image, lower, upper)
	# return the edged image
	return edged


def cv2_resize_with_padding(img, expected_size):
    expected_size = np.asarray(expected_size)
    
    if img.shape[0] > img.shape[1]:        
        wpercent = (expected_size[0]/float(img.shape[0]))
        hsize = int((float(img.shape[1])*float(wpercent)))
            
        img = cv2.resize(img, (hsize, expected_size[0]))
    else:        
        hpercent = (expected_size[1]/float(img.shape[1]))
        wsize = int((float(img.shape[0])*float(hpercent)))
            
        img = cv2.resize(img, (expected_size[0], wsize))
    
    
    delta_w = expected_size[0] - img.shape[1]
    delta_h = expected_size[1] - img.shape[0]
    top, bottom = delta_h//2, delta_h-(delta_h//2)
    left, right = delta_w//2, delta_w-(delta_w//2)

    color = [0, 0, 0]
    new_im = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)

    return new_im

