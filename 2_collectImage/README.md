# Image Collector Web App

A modern, premium web application for collecting training images for object detection.

## Features
- **Live Camera Feed**: Real-time MJPEG stream.
- **Instant Capture**: Capture images with a button click or SPACE bar.
- **Recent Gallery**: View the last 5 captured images.
- **Full Gallery**: Browse all captured images in a grid view with a Lightbox.
- **Management**: Delete individual images or reset the entire collection.
- **Export**: Download all images as a ZIP file.

## Prerequisites
- Python 3.x
- A camera device connected (USB Webcam or Raspberry Pi Camera)

## Installation

1.  **Navigate to the project directory**:
    ```bash
    cd 2_collectImage
    ```

2.  **Create a virtual environment (optional but recommended)**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install fastapi uvicorn python-multipart jinja2 opencv-python-headless
    ```

## Running the App

1.  **Start the server**:
    ```bash
    # Assuming you are in the 2_collectImage directory and venv is active
    uvicorn app:app --host 0.0.0.0 --port 8000
    ```

2.  **Access the App**:
    Open your web browser and navigate to:
    - Local: `http://localhost:8000`
    - Network: `http://<your-ip-address>:8000`

## File Structure
- `app.py`: Main FastAPI application.
- `templates/`: HTML templates (`index.html`, `gallery.html`).
- `captures/`: Directory where captured images are saved.

## Troubleshooting
- **Camera not found**: Ensure your camera is connected and not being used by another application. The app attempts to auto-detect devices `/dev/video*`.
- **Permission denied**: You might need to add your user to the `video` group: `sudo usermod -a -G video $USER`.
