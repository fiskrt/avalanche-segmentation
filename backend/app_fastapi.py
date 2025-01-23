from typing import List 
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image
from pydantic import BaseModel
import cv2
import numpy as np
from classifiers import predict_avalanche_type, predict_spam
from inference import get_sam_predictor 
import base64
import io
from sam_utils import select_point,overlay
import shutil
import os
from helpers import *



app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global states
predictor = None
# IDEA: Just save the original image and whenever we show the image
# we apply the 'counter' number of transformations to it
original_image = None
# keeps track of how many masks there are in the image
counter = 0
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(SCRIPT_DIR, 'temp')
print(TEMP_DIR)

class Point(BaseModel):
    x: int
    y: int

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

@app.post("/spamcheck")
async def spam_classify_image(file: UploadFile = File(...)):
    try:

        global counter
        shutil.rmtree(TEMP_DIR, ignore_errors=True)
        os.makedirs(TEMP_DIR, exist_ok=True)
        counter = 0

        # Read image file
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data)).convert("RGB")

        # Classify image
        predicted_class = predict_spam(image)
        # If image is not spam we save it and add it to predictor
        if predicted_class != 0:
            global predictor, original_image
            original_image=np.array(image)
            predictor = get_sam_predictor(device='cpu', image=original_image)

        # return true or false
        return JSONResponse(content={"spam": predicted_class == 0})

    except HTTPException as e:
        print(e)
        return JSONResponse(content={"error": e.detail}, status_code=e.status_code)
    except Exception as e:
        print(e)
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/checkavalanchetype")
async def classify_avalanche_type(file: UploadFile = File(...)):
    try:
        # Read image file
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data)).convert("RGB")
        
        # Classify image
        predicted_class = predict_avalanche_type(image)
        

        # return true or false
        return JSONResponse(content={"avalanche_type": predicted_class})

    except HTTPException as e:
        return JSONResponse(content={"error": e.detail}, status_code=e.status_code)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/estimate_avalanche_size")
async def estimate_avalanche_size():
    image_path = './../images/avalanche.jpeg'
    
    ## EXAMPLE: ESTIMATION OF AVALANCHE SIZE
    camera_name = 'Xiaomi 11 Pro'
    latitude, longitude, focal_length = get_exif_data(image_path)
    sensor_size = get_sensor_size(camera_name)
    # Example positions (already given in the problem)
    photoposition = [2684500, 1173301]
    avalancheposition = [2684458, 1173135]

    # Add elevations for both positions
    photoposition.append(get_elevation(photoposition[0], photoposition[1]))
    avalancheposition.append(get_elevation(avalancheposition[0], avalancheposition[1]))

    # Check if elevations are valid before proceeding
    if photoposition[2] is None or avalancheposition[2] is None:
        print("Error: Unable to retrieve elevation data.")
    else:
        # Compute steepness angles for the avalanche position (and optionally for the photo position too)
        (angle_east_avalanche, angle_north_avalanche) = compute_steepness_angles(avalancheposition[0], avalancheposition[1], delta=5, sr=None)
        (angle_east_photo, angle_north_photo) = compute_steepness_angles(photoposition[0], photoposition[1], delta=5, sr=None)

        # Compute the 3D distance between the two positions (easting, northing, elevation)
        distance = compute_3d_distance(photoposition[0], photoposition[1], photoposition[2], avalancheposition[0], avalancheposition[1], avalancheposition[2])

        # Compute the angle differences (angles between observer and avalanche)
        angle_east_diff = angle_east_avalanche - angle_east_photo
        angle_north_diff = angle_north_avalanche - angle_north_photo
        
    #mask = getSamSegmentation(image_path)
    mask = 0.3
    finalsize = computeAvalancheSize(mask, distance, focal_length, sensor_size, (angle_east_diff,angle_north_diff))
    print(f"The distance is {distance} and the estimated size id {finalsize} square meters")
    return JSONResponse(content={"distance": distance, "finalsize": finalsize})
    


@app.post("/add_point")
async def add_point(point: Point):
    """
        When user clicks on image we do segmentation on image 
        and return the image.
    """
    global predictor, original_image, counter

    # segment point
    img = select_point(
        predictor=predictor,
        original_img=original_image,
        point=point,
        counter=counter,
    )
    
    counter += 1
    img = img[:,:,[2,1,0]]
    return {
        "image": encode_image(img),
    }

@app.post("/undo")
async def undo():
    global original_image, counter
    counter -= 1

    img = overlay(original_image, count=counter)
    img = img[:,:,[2,1,0]]
    return {"image": encode_image(img)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)