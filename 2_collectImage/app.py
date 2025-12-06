import os
import cv2
import time
import zipfile
import io
import threading
from pathlib import Path
from fastapi import FastAPI, Response, BackgroundTasks
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

# --- Camera Utilities (Adapted from main.py) ---

def find_working_device(max_index=8):
    """Try indices 0..max_index-1 and any /dev/video* - return first that works."""
    for i in range(max_index):
        cap = cv2.VideoCapture(i, cv2.CAP_V4L2)
        if cap.isOpened():
            ret, _ = cap.read()
            cap.release()
            if ret:
                return str(i)
        else:
            cap.release()

    for dev_idx in range(0, 8):
        path = f"/dev/video{dev_idx}"
        if os.path.exists(path):
            cap = cv2.VideoCapture(path, cv2.CAP_V4L2)
            if cap.isOpened():
                ret, _ = cap.read()
                cap.release()
                if ret:
                    return path
            else:
                cap.release()
    return None

def open_capture(device, w=640, h=480, fps=30):
    try:
        idx = int(device)
        device_arg = idx
    except Exception:
        device_arg = device

    cap = cv2.VideoCapture(device_arg, cv2.CAP_V4L2)
    if not cap.isOpened():
        return None

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, float(w))
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, float(h))
    cap.set(cv2.CAP_PROP_FPS, float(fps))
    return cap

# --- Global State & Configuration ---
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")

SAVE_DIR = "captures"
Path(SAVE_DIR).mkdir(parents=True, exist_ok=True)

class Camera:
    def __init__(self):
        self.device = find_working_device()
        print(f"Camera device found: {self.device}")
        self.cap = None
        if self.device is not None:
             self.cap = open_capture(self.device)
        self.lock = threading.Lock()
        self.last_frame = None

    def get_frame(self):
        with self.lock:
            if self.cap and self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret:
                    # Encode to JPEG
                    ret, buffer = cv2.imencode('.jpg', frame)
                    self.last_frame = frame
                    return buffer.tobytes(), frame
        return None, None
    
    def capture_image(self):
        with self.lock:
            if self.last_frame is not None:
                ts = datetime.now().strftime("%Y%m%d-%H%M%S")
                filename = f"capture_{ts}.jpg"
                filepath = os.path.join(SAVE_DIR, filename)
                cv2.imwrite(filepath, self.last_frame)
                return filename, filepath
        return None, None

camera = Camera()

def gen_frames():
    while True:
        frame_bytes, _ = camera.get_frame()
        if frame_bytes:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        else:
            time.sleep(0.1)

@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/video_feed")
def video_feed():
    return StreamingResponse(gen_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.post("/capture")
def capture_endpoint():
    filename, filepath = camera.capture_image()
    if filename:
        count = len(os.listdir(SAVE_DIR))
        return {"status": "success", "filename": filename, "count": count, "url": f"/captures/{filename}"}
    return {"status": "error", "message": "Could not capture frame"}

@app.get("/download")
def download_endpoint():
    # Zip all files in SAVE_DIR
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        for root, dirs, files in os.walk(SAVE_DIR):
            for file in files:
                if file.endswith(".jpg") or file.endswith(".png"):
                    zip_file.write(os.path.join(root, file), file)
    
    zip_buffer.seek(0)
    return StreamingResponse(
        zip_buffer, 
        media_type="application/zip", 
        headers={"Content-Disposition": "attachment; filename=captures.zip"}
    )

@app.get("/stats")
def stats_endpoint():
    try:
        count = len([f for f in os.listdir(SAVE_DIR) if f.endswith(('.jpg', '.png'))])
    except:
        count = 0
    return {"count": count}

@app.get("/recent")
def recent_endpoint():
    files = []
    try:
        for f in os.listdir(SAVE_DIR):
            if f.endswith(('.jpg', '.png')):
                filepath = os.path.join(SAVE_DIR, f)
                stats = os.stat(filepath)
                # Parse timestamp from filename to ensure sorting by creation time if needed, 
                # or just use file modification time
                files.append({
                    "filename": f,
                    "url": f"/captures/{f}",
                    "timestamp": stats.st_mtime,
                    "size": stats.st_size
                })
        # Sort by timestamp desc, take top 5
        files.sort(key=lambda x: x["timestamp"], reverse=True)
        return {"files": files[:5]}
    except Exception as e:
        print(f"Error getting recent files: {e}")
        return {"files": []}

@app.get("/api/all_files")
def all_files_endpoint():
    files = []
    try:
        for f in os.listdir(SAVE_DIR):
            if f.endswith(('.jpg', '.png')):
                filepath = os.path.join(SAVE_DIR, f)
                stats = os.stat(filepath)
                files.append({
                    "filename": f,
                    "url": f"/captures/{f}",
                    "timestamp": stats.st_mtime,
                    "size": stats.st_size
                })
        files.sort(key=lambda x: x["timestamp"], reverse=True)
        return {"files": files}
    except Exception as e:
        return {"files": []}

@app.delete("/delete/{filename}")
def delete_file(filename: str):
    try:
        filepath = os.path.join(SAVE_DIR, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            return {"status": "success"}
        return {"status": "error", "message": "File not found"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.delete("/delete_all")
def delete_all_files():
    try:
        for f in os.listdir(SAVE_DIR):
            if f.endswith(('.jpg', '.png')):
                os.remove(os.path.join(SAVE_DIR, f))
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/gallery")
def gallery(request: Request):
    return templates.TemplateResponse("gallery.html", {"request": request})

# Serve captured images statically to show preview?
from fastapi.staticfiles import StaticFiles
app.mount("/captures", StaticFiles(directory="captures"), name="captures")
