from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

import cv2
import os
import uuid
import numpy as np

from PIL import Image
from transformers import pipeline

app = FastAPI(
    title="AI Video Detector",
    description="AI Video Detection Hackathon Project",
    version="1.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


print("Loading AI detector...")

detector = pipeline(
    "image-classification",
    model="Hemg/Deepfake-Detection"
)

print("AI detector loaded successfully!")



@app.get("/")
def home():
    return {
        "status": "online",
        "message": "AI Video Detector API is running"
    }


@app.post("/analyze")
async def analyze_video(file: UploadFile = File(...)):

 
    if not file.content_type or not file.content_type.startswith("video/"):
        return {
            "success": False,
            "message": "Please upload a valid video file."
        }

    filename = f"{uuid.uuid4()}_{file.filename}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    contents = await file.read()

    with open(filepath, "wb") as video_file:
        video_file.write(contents)



    video = cv2.VideoCapture(filepath)

    if not video.isOpened():

        if os.path.exists(filepath):
            os.remove(filepath)

        return {
            "success": False,
            "message": "Could not read the video."
        }


    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

    fps = video.get(cv2.CAP_PROP_FPS)

    if fps > 0:
        duration = frame_count / fps
    else:
        duration = 0


    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))

    max_samples = 12

    if frame_count > 0:
        sample_count = min(max_samples, frame_count)
    else:
        sample_count = 0


    if sample_count > 0:

        sample_positions = np.linspace(
            0,
            frame_count - 1,
            sample_count,
            dtype=int
        )

    else:
        sample_positions = []


    fake_scores = []
    real_scores = []

    analyzed_frames = 0

    for position in sample_positions:

        video.set(cv2.CAP_PROP_POS_FRAMES, int(position))

        success, frame = video.read()

        if not success:
            continue


        # OpenCV uses BGR
        # PIL uses RGB

        frame_rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        image = Image.fromarray(frame_rgb)


        try:

            results = detector(image)

            fake_score = 0.0
            real_score = 0.0

            for result in results:

                label = result["label"].lower()
                score = float(result["score"])

                if label == "fake":
                    fake_score = score

                elif label == "real":
                    real_score = score


            fake_scores.append(fake_score)
            real_scores.append(real_score)

            analyzed_frames += 1


        except Exception as error:

            print(
                f"Frame analysis error: {error}"
            )


    video.release()


    if analyzed_frames == 0:

        if os.path.exists(filepath):
            os.remove(filepath)

        return {
            "success": False,
            "message": "Could not analyze any video frames."
        }


    average_fake = float(
        np.mean(fake_scores)
    )

    average_real = float(
        np.mean(real_scores)
    )


    # Convert to percentage

    ai_probability = round(
        average_fake * 100,
        2
    )

    real_probability = round(
        average_real * 100,
        2
    )


    if average_fake >= average_real:

        prediction = "AI-GENERATED"

    else:

        prediction = "REAL"


    confidence = round(
        max(average_fake, average_real) * 100,
        2
    )


    if os.path.exists(filepath):
        os.remove(filepath)




    return {

        "success": True,

        "filename": file.filename,

        "prediction": prediction,

        "ai_probability": ai_probability,

        "real_probability": real_probability,

        "confidence": confidence,

        "analyzed_frames": analyzed_frames,

        "total_frames": frame_count,

        "fps": round(fps, 2),

        "duration": round(duration, 2),

        "resolution": f"{width}x{height}",

        "message": "Video analyzed successfully."
    }