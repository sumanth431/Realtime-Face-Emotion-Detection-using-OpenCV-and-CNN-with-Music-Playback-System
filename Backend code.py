from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
import logging
from pathlib import Path
import os

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(_name_)

# Initialize FastAPI
app = FastAPI()

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Constants
MODEL_PATH = Path(_file_).parent / "backend/models/emotion_model.h5"
MUSIC_DIR = Path("static/music")
EMOTION_LABELS = ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']

# Music mapping
MUSIC_MAPPING = {
    'happy': ["happy1.mp3"],
    'sad': ["sad1.mp3"],
    'neutral': ["neutral1.mp3"],
    'angry': ["angry1.mp3"],
    'fear': ["fear1.mp3"],
    'surprise': ["surprise1.mp3"],
    'disgust': ["disgust1.mp3"]
}

# Load model
model = load_model(MODEL_PATH)

def preprocess_image(frame):
    """Preprocess image for emotion detection"""
    try:
        # Convert to RGB and resize
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        resized = cv2.resize(rgb, (224, 224))
        normalized = resized.astype('float32') / 255.0
        return np.expand_dims(normalized, axis=0)
    except Exception as e:
        logger.error(f"Preprocessing error: {str(e)}")
        raise

def detect_emotion(frame):
    """Detect emotion from image frame"""
    try:
        # Face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        if len(faces) == 0:
            return "neutral"
            
        # Crop face and predict
        (x,y,w,h) = faces[0]
        face = frame[y:y+h, x:x+w]
        processed = preprocess_image(face)
        predictions = model.predict(processed)
        return EMOTION_LABELS[np.argmax(predictions)]
    except Exception as e:
        logger.error(f"Detection error: {str(e)}")
        return "neutral"

@app.post("/detect_emotion")
async def detect_emotion_api(file: UploadFile = File(...)):
    """API endpoint for emotion detection"""
    try:
        contents = await file.read()
        frame = cv2.imdecode(np.frombuffer(contents, np.uint8), cv2.IMREAD_COLOR)
        
        if frame is None:
            raise HTTPException(400, detail="Invalid image")
        
        emotion = detect_emotion(frame)
        music_file = MUSIC_MAPPING.get(emotion, ["neutral1.mp3"])[0]
        
        return {
            "emotion": emotion,
            "music_file": music_file,
            "music_url": f"/static/music/{music_file}"
        }
        
    except Exception as e:
        logger.error(f"API error: {str(e)}")
        raise HTTPException(500, detail=str(e))

if _name_ == "_main_":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
