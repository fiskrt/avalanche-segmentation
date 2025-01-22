import os
from typing import List
import cv2
import gradio as gr
import numpy as np
from inference import get_sam_predictor, run_inference

# points color and marker
COLORS = [(255, 0, 0), (0, 255, 0)]
MARKERS = [1, 5]

counter = 0


def save_masks(o_masks):
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


def select_point(predictor,
                 original_img: np.ndarray,
                 display_img: np.ndarray,
                 multi_object: List,
                 sel_pix: list,
                 point_type: str,
                 evt: gr.SelectData):
    """When user clicks on the image, show points and update the mask."""
    sel_pix = []
    if point_type == 'foreground_point':
        sel_pix.append((evt.index, 1))
    elif point_type == 'background_point':
        sel_pix.append((evt.index, 0))
    else:
        sel_pix.append((evt.index, 1))
    
    # run inference on the original image
    o_masks = run_inference(predictor, original_img, sel_pix, multi_object)
    
    # Create visualization on the display image
    img = display_img.copy()
    # Draw the mask
    if o_masks:
        mask = o_masks[0][0]  # Get first mask
        img = overlay_mask(img, mask)
    
    o_files = save_masks(o_masks)
    global counter
    counter += 1
    print(f'increase counter to {counter}')
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

def reset_image(predictor, img):
    counter = 0
    preprocessed_image = img.copy()
    # Store original image for inference but set preprocessed for display
    predictor.set_image(img)  # Set the original image for inference
    return img, preprocessed_image, preprocessed_image, [], []

with gr.Blocks() as demo:
    predictor = gr.State(value=get_sam_predictor())
    selected_points = gr.State(value=[])
    original_image = gr.State(value=None)  # For inference
    display_image = gr.State(value=None)   # For display
    
    with gr.Row():
        gr.Markdown("# Avalanche locator")
        
    with gr.Row():
        # Single image that serves as both input and output
        image = gr.Image(type="numpy", label='Click to add points', height=600)
        
        with gr.Column():
            undo_button = gr.Button('Undo point')
            fg_bg_radio = gr.Radio(
                ['foreground_point', 'background_point'],
                info="Select foreground or background point",
                label='Point label')
            multi_object = gr.CheckboxGroup(
                ['Multi-object'],
                info="Whether each point corresponds to a single object",
                label='Multi-object')
            output_file = gr.File(label='Save output mask')
            
            gr.Markdown('Click on the image to add points. Default: `foreground_point`')

    image.upload(
        reset_image,
        [predictor, image,],
        [original_image, display_image, image, selected_points, output_file])

    undo_button.click(
        undo_points,
        [predictor, original_image, display_image, multi_object, selected_points],
        [image])

    image.select(
        select_point,
        [predictor, original_image, display_image, multi_object, selected_points, fg_bg_radio],
        [image])

demo.queue().launch(debug=True)