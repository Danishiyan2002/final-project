# main.py
# Minimal FastAPI backend: /predict proxies to Roboflow; CORS allows your user site on port 5502.
# No templates, no auth, no admin — just the AI function.

from fastapi import FastAPI, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import requests
import os

# Roboflow Hosted API — ensure this is EXACT for your model (note the zero in "mv0ln")
MODEL_URL = os.getenv("MODEL_URL", "https://detect.roboflow.com/mammogram-project-mvoln/1")
API_KEY = os.getenv("API_KEY", "wk68dlo6nWqOpMys42K3")  # replace with your Private API Key in production

app = FastAPI()

# CORS: allow your frontend (http://localhost:5502)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health():
    return {"status": "ok"}

@app.post("/predict")
async def predict(file: UploadFile, conf: float = 0.15):
    # Read file
    content = await file.read()
    if not content:
        return JSONResponse({"error": "Empty file"}, status_code=400)

    # Prepare Roboflow request
    files = {
        "file": (
            file.filename or "upload.jpg",
            content,
            file.content_type or "application/octet-stream",
        )
    }
    params = {
        "api_key": API_KEY,
        "confidence": conf,
        "format": "json",
    }

    # Call Roboflow
    try:
        resp = requests.post(MODEL_URL, files=files, params=params, timeout=60, allow_redirects=False)
    except requests.exceptions.RequestException as e:
        return JSONResponse({"error": f"Network error calling Roboflow: {e}"}, status_code=502)

    if resp.status_code != 200:
        # Helpful log for debugging 403/4xx issues
        print("Roboflow error:", resp.status_code, resp.text)
        return JSONResponse({"error": "Roboflow error", "status_code": resp.status_code, "body": resp.text}, status_code=resp.status_code)

    # Parse JSON and convert boxes to [x1,y1,x2,y2]
    try:
        data = resp.json()
    except Exception:
        return JSONResponse({"error": "Failed to parse Roboflow response", "raw": resp.text[:2000]}, status_code=500)

    preds = []
    for p in data.get("predictions", []):
        x1 = p["x"] - p["width"] / 2
        y1 = p["y"] - p["height"] / 2
        x2 = p["x"] + p["width"] / 2
        y2 = p["y"] + p["height"] / 2
        preds.append({
            "bbox": [x1, y1, x2, y2],
            "class": p.get("class", "unknown"),
            "confidence": p.get("confidence", 0.0)
        })

    return JSONResponse({"predictions": preds})
