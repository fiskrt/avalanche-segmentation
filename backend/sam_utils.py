import cv2
import numpy as np
from inference import run_inference
from typing import List
import os
from PIL import Image
import os
from inference import run_inference
from typing import List

# Create temp directory in the same directory as the script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(SCRIPT_DIR, 'temp')
os.makedirs(TEMP_DIR, exist_ok=True)

def save_masks(o_masks, counter):
    o_files = []
    for mask, name in o_masks:
        o_mask = np.uint8(mask * 255)
        o_file = os.path.join(TEMP_DIR, f'{name}{counter}.png')
        cv2.imwrite(o_file, o_mask)
        o_files.append(o_file)
    return o_files


def overlay_mask(image: np.ndarray, mask: np.ndarray, alpha: float = 0.6):
    """Overlay mask on image with transparency."""
    overlay = image.copy()

    if mask.any():
        overlay[mask > 0] = [255, 0, 0]  # Red overlay for mask
    return cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0)


def select_point(
    predictor,
    original_img: np.ndarray,
    point,
    counter:int,
):
    """When user clicks on the image, show points and update the mask."""
    point = [point.x, point.y]
    sel_pix = [(point, 1)]
    input_img = original_img.copy() 
    # run inference on the original image
    o_masks = run_inference(predictor, input_img, sel_pix, [])
    
    # Create visualization on the display image
    img = original_img.copy()
    # Draw the mask
    if o_masks:
        mask = o_masks[0][0]  # Get first mask
        img = overlay_mask(img, mask)
    
    o_files = save_masks(o_masks, counter=counter)
    img = overlay(img, counter)
    return img

def overlay(image, count: int):
    image = image.copy()
    for c in range(count):
        o_file = os.path.join(TEMP_DIR, f'mask_0{c}.png')
        if os.path.exists(o_file):
            mask = Image.open(o_file).convert("L")
            mask = np.array(mask)
            image = overlay_mask(image, mask)
    return image

def undo_points(predictor, orig_img, display_img, multi_object, sel_pix):
    global counter
    counter -= 1
    
    img = display_img.copy()
    img = overlay(img, counter) 
    return img 