# Public Avalanche Reporting Tool

## Overview

This web application is designed to improve the accuracy and reliability of public avalanche reporting by addressing key challenges in existing reporting systems.

## Problem Statement

Current public avalanche reporting tools face several significant challenges:
- Complicated user experience leading to incomplete reports
- Inaccurate avalanche mapping
- Potential spam or irrelevant image submissions
- Inconsistent avalanche size and type reporting

## Features

### Image Validation
- **Spam Detection**: Advanced image classification to filter out irrelevant or inappropriate images
- Prevents misuse of the reporting system

### Avalanche Classification
- Automatic prediction of avalanche type using machine learning
- Supports classification of:
  - No avalanche
  - Slab avalanche
  - Loose avalanche
  - Glide avalanche

### Interactive Segmentation
- Allow users to precisely mark avalanche areas in their images
- Uses Segment Anything Model (SAM) for accurate image segmentation
- Enables point-based interaction for highlighting specific regions

### Size and Type Selection
- Dropdown menus for selecting:
  - Avalanche Size (Small, Medium, Large, Very Large)
  - Avalanche Type

## Technical Architecture

### Backend
- FastAPI server
- Machine learning models for:
  - Spam detection
  - Avalanche type classification
- Segment Anything Model for image segmentation

### Frontend
- Next.js React application
- Interactive user interface
- State management for image upload and processing

## Key Technologies

- Python
- FastAPI
- PyTorch
- OpenCV
- Next.js
- React
- Tailwind CSS

## Installation

### Prerequisites
- Python 3.8+
- Node.js 14+
- pip
- npm/yarn

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python app_fastapi.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## Future Improvements
- Enhanced machine learning models
- More granular avalanche classification
- Improved user guidance
- Geospatial data integration