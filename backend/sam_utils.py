import cv2
import numpy as np
from inference import run_inference
from typing import List
import os

def save_masks(o_masks, counter):
    o_files = []
    for mask, name in o_masks:
        o_mask = np.uint8(mask * 255)
        o_file = os.path.join('temp', name) + str(counter) + '.png'
        cv2.imwrite(o_file, o_mask)
        o_files.append(o_file)
    return o_files


def overlay_mask(image: np.ndarray, mask: np.ndarray, alpha: float = 0.5):
    """Overlay mask on image with transparency."""
    overlay = image.copy()

    if mask.any():
        overlay[mask > 0] = [255, 0, 0]  # Red overlay for mask
    return cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0)


def select_point(
    predictor,
    original_img: np.ndarray,
    display_img: np.ndarray,
    point,
    counter:int,
):
    """When user clicks on the image, show points and update the mask."""
    point = [point.x, point.y]
    sel_pix = [(point, 1)]
    
    # run inference on the original image
    o_masks = run_inference(predictor, original_img, sel_pix, [])
    
    # Create visualization on the display image
    img = display_img.copy()
    # Draw the mask
    if o_masks:
        mask = o_masks[0][0]  # Get first mask
        img = overlay_mask(img, mask)
    
    o_files = save_masks(o_masks, counter=counter)
    img = overlay(img, counter)
    return img
  
def overlay(image, count: int):
    # loop through masks in temp from 0 to count,
    # and overlay each
    image = image.copy()
    for c in range(count):
        o_file = os.path.join('temp', 'mask_0') + str(c) + '.png'
        mask = cv2.imread(o_file)
        mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
        image = overlay_mask(image, mask)
    return image


def undo_points(predictor, orig_img, display_img, multi_object, sel_pix):
    global counter
    counter -= 1
    
    img = display_img.copy()
    img = overlay(img, counter) 
    return img 