# Public Avalanche Reporting Tool 🏔️🚨

## Overview

Web application designed to improve avalanche reporting accuracy and reliability.

## Problem Statement

Current public avalanche reporting tools face challenges:
- Complicated user experience
- Inaccurate avalanche mapping
- Potential spam or irrelevant images
- Inconsistent avalanche reporting

## Features 🚀

### Image Validation
- **Spam Detection**: Advanced image classification
- Prevents system misuse

### Avalanche Classification
- Machine learning prediction of avalanche type
- Supports classification of:
  - No avalanche
  - Slab avalanche
  - Loose avalanche
  - Glide avalanche

### Interactive Segmentation 
- Precise avalanche area marking in images
- Uses Segment Anything Model (SAM)
- Point-based interaction for region highlighting

### Size and Type Selection
- Dropdown menus for:
  - Avalanche Size
  - Avalanche Type

## Technical Architecture 🏗️

### Backend 💻
- FastAPI server
- Machine learning models for:
  - Spam detection
  - Avalanche classification
- Segment Anything Model

### Frontend 🎨
- Next.js React application
- Interactive user interface
- State management for image processing

## Key Technologies 🛠️
- Python
- FastAPI
- PyTorch
- OpenCV
- Next.js
- React
- Tailwind CSS

## Installation 🔧

### Prerequisites 📋
- Python 3.10+
- Node.js 14+
- uv
- npm/yarn

### Backend Setup 🖥️
```bash
cd backend
uv sync
python app_fastapi.py
```

### Frontend Setup 🌐
```bash
cd frontend
npm install
npm run dev
```

## Future Improvements 🔮
- Enhanced machine learning models
- More granular avalanche classification
- Improved user guidance
- Geospatial data integration
