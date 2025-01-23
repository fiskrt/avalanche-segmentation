
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from torchvision import models, transforms
from PIL import Image
import torch
import io
import numpy as np
import torch.nn as nn


# Load ResNet model (assumes model is saved locally as 'resnet_model.pth')
try:
    # Load pretrained ResNet50
    binary_model = models.resnet50(pretrained=True)


    # Modify the final layer for binary classification
    num_features = binary_model.fc.in_features
    binary_model.fc = nn.Sequential(
        nn.Linear(num_features, 256),
        nn.ReLU(),
        nn.Dropout(0.5),
        nn.Linear(256, 2)  # 2 classes: avalanche / no avalanche
    )
    binary_model.load_state_dict(torch.load("checkpoints/best_avalanche_model.pth", map_location=torch.device('cpu')))
    binary_model.eval()
except FileNotFoundError:
    raise RuntimeError("Model file 'resnet_model.pth' not found. Ensure it is in the current directory.")




try:
    # Load pretrained ResNet50
    avalanchetype_model = models.resnet50(pretrained=True)


    # Modify the final layer for binary classification
    num_features = avalanchetype_model.fc.in_features
    avalanchetype_model.fc = nn.Sequential(
        nn.Linear(num_features, 256),
        nn.ReLU(),
        nn.Dropout(0.5),
        nn.Linear(256, 4)  # 2 classes: avalanche / no avalanche
    )
    avalanchetype_model.load_state_dict(torch.load("checkpoints/best_avalanche_multiclass_model.pth", map_location=torch.device('cpu')))
    avalanchetype_model.eval()
except FileNotFoundError:
    raise RuntimeError("Model file 'resnet_model.pth' not found. Ensure it is in the current directory.")



# Define image preprocessing transforms
preprocess_binary = transforms.Compose([
    transforms.Resize(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

preprocess_multiclass = transforms.Compose([
    transforms.Resize(704),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

# Function to predict the class of an image
def predict_spam(image: Image.Image):
    try:
        # Preprocess image
        input_tensor = preprocess_binary(image).unsqueeze(0)
        # Perform inference
        with torch.no_grad():
            outputs = binary_model(input_tensor)
        # Get predicted class
        _, predicted_class = outputs.max(1)
        print(predicted_class)
        return predicted_class.item()
    except Exception as e:
        raise RuntimeError(f"Error in prediction: {str(e)}")
    

# Function to predict the class of an image
def predict_avalanche_type(image: Image.Image):
    try:
        # Preprocess image
        input_tensor = preprocess_multiclass(image).unsqueeze(0)
        # Perform inference
        with torch.no_grad():
            outputs = avalanchetype_model(input_tensor)
        # Get predicted class
        _, predicted_class = outputs.max(1)
        print(outputs)
        print(predicted_class)
        return predicted_class.item()
    except Exception as e:
        raise RuntimeError(f"Error in prediction: {str(e)}")
    

if __name__ == "__main__":
    predict_spam(Image.open("temp/sample_image.png"))
    predict_avalanche_type(Image.open("temp/sample_image.png"))
