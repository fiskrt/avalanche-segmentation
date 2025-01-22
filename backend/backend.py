import os
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import cv2
import numpy as np
from inference import SamPredictor, get_sam_predictor
import base64

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
predictor = get_sam_predictor()
current_image = None
display_image = None
masks = []
points = []

class Point(BaseModel):
    x: int
    y: int
    label: int  # 1 for foreground, 0 for background

def encode_image(image_array: np.ndarray) -> str:
    """Convert numpy array to base64 string."""
    success, encoded_image = cv2.imencode('.png', image_array)
    if success:
        return base64.b64encode(encoded_image.tobytes()).decode('utf-8')
    return ""

def decode_image(base64_string: str) -> np.ndarray:
    """Convert base64 string to numpy array."""
    img_data = base64.b64decode(base64_string)
    img_array = np.frombuffer(img_data, np.uint8)
    return cv2.imdecode(img_array, cv2.IMREAD_COLOR)

def overlay_mask(image: np.ndarray, mask: np.ndarray, alpha: float = 0.5):
    """Overlay mask on image with transparency."""
    overlay = image.copy()
    if mask.any():
        overlay[mask > 0] = [255, 0, 0]  # Red overlay for mask
    return cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0)

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    global current_image, display_image, masks, points
    
    # Reset state
    masks = []
    points = []
    
    # Read and process image
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # Store images
    current_image = img.copy()
    display_image = img.copy()
    
    # Set image in predictor
    predictor.set_image(current_image)
    
    return {"image": encode_image(display_image)}

@app.post("/add_point")
async def add_point(point: Point, multi_object: bool = False):
    global display_image, masks, points
    
    # Add point to list
    points.append((point.x, point.y))
    
    # Run inference with just the new point
    current_point = [((point.x, point.y), point.label)]
    o_masks = predictor.predict([(point.x, point.y)], point.label, multi_object)
    
    if o_masks:
        # Save mask
        masks.append(o_masks[0][0])
        
        # Update display image with new mask
        display_image = overlay_mask(display_image, o_masks[0][0])
    
    # Draw all points
    for px, py in points:
        cv2.drawMarker(display_image, (px, py), (255, 0, 0), 
                      markerType=1, markerSize=5, thickness=2)
    
    return {
        "image": encode_image(display_image),
        "mask": encode_image(o_masks[0][0] * 255) if o_masks else None
    }

@app.post("/undo")
async def undo():
    global display_image, masks, points
    
    if points:
        # Remove last point and mask
        points.pop()
        if masks:
            masks.pop()
        
        # Recreate display image from scratch
        display_image = current_image.copy()
        
        # Redraw all masks
        for mask in masks:
            display_image = overlay_mask(display_image, mask)
        
        # Redraw all points
        for px, py in points:
            cv2.drawMarker(display_image, (px, py), (255, 0, 0), 
                          markerType=1, markerSize=5, thickness=2)
    
    return {"image": encode_image(display_image)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)