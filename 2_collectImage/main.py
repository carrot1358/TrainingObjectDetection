#!/usr/bin/env python3
"""
image_collector.py

Robust V4L2 capture using OpenCV with GUI fallback and terminal-control fallback.

Features:
- Auto-detects camera device
- Default resolution 640x480
- Preview with cv2.imshow() if available
- Save frame with 's' in preview window OR type 's' + Enter in the terminal
- Quit with 'q' or Esc in preview window, or Ctrl-C in terminal

Usage:
  python image_collector.py --preview
  python image_collector.py --save-every 5   # saves every 5 seconds headless
"""
import argparse
import os
import sys
import time
import threading
from pathlib import Path
from queue import SimpleQueue

import cv2
import numpy as np

SAVE_DIR_DEFAULT = "captures"

def ensure_dir(path: str):
    Path(path).mkdir(parents=True, exist_ok=True)

def find_working_device(max_index=5):
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

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--device", type=str, default=None,
                   help="Device index (0,1,...) or path (/dev/video0). If omitted the script tries to auto-detect.")
    p.add_argument("--width", type=int, default=640, help="Requested capture width")
    p.add_argument("--height", type=int, default=480, help="Requested capture height")
    p.add_argument("--fps", type=int, default=30, help="Requested FPS (best-effort)")
    p.add_argument("--preview", action="store_true", help="Show preview window (if GUI available)")
    p.add_argument("--save-dir", type=str, default=SAVE_DIR_DEFAULT, help="Directory to save frames")
    p.add_argument("--save-every", type=float, default=0.0, help="If >0, automatically save a frame every N seconds")
    return p.parse_args()

def open_capture(device, w, h, fps):
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

def can_show_gui():
    """Return True if cv2.imshow() seems to work in this environment."""
    try:
        # Try creating a window and destroying it
        cv2.namedWindow(".__test__", cv2.WINDOW_NORMAL)
        cv2.destroyWindow(".__test__")
        return True
    except Exception:
        return False

def stdin_reader(queue: SimpleQueue, stop_event: threading.Event):
    """
    Read lines from stdin in a thread. Put the stripped input into queue.
    This allows the user to type 's' + Enter to save even when GUI is broken.
    """
    try:
        while not stop_event.is_set():
            line = sys.stdin.readline()
            if not line:
                # EOF
                break
            queue.put(line.strip())
    except Exception:
        pass
    finally:
        stop_event.set()

def save_frame(frame, save_dir, prefix="capture"):
    ts = time.strftime("%Y%m%d-%H%M%S")
    filename = os.path.join(save_dir, f"{prefix}_{ts}.jpg")
    cv2.imwrite(filename, frame)
    print(f"Saved {filename}")

def main():
    args = parse_args()
    ensure_dir(args.save_dir)

    device = args.device
    if device is None:
        print("Auto-detecting camera device...")
        device = find_working_device()
        if device is None:
            print("No working V4L2 camera found. Please provide --device (e.g. /dev/video0 or 0).")
            return
        print(f"Using device: {device}")
    else:
        print(f"Using device provided: {device}")

    cap = open_capture(device, args.width, args.height, args.fps)
    if cap is None or not cap.isOpened():
        print(f"Failed to open device {device}. Make sure it's accessible and exposed as a V4L2 device.")
        return

    use_gui = args.preview and can_show_gui()
    if args.preview and not use_gui:
        print("Warning: GUI preview requested but cv2.imshow() isn't available. Running in headless mode.")
        print("You can still save frames by typing 's' + Enter in this terminal.")

    # start stdin reader thread for terminal commands
    stdin_queue = SimpleQueue()
    stop_event = threading.Event()
    stdin_thread = threading.Thread(target=stdin_reader, args=(stdin_queue, stop_event), daemon=True)
    stdin_thread.start()

    last_save_time = time.time()
    frame_counter = 0
    start_time = time.time()
    print("Controls: press 's' in window OR type 's' + Enter in terminal to save. Quit with 'q' in window or Ctrl-C.")

    try:
        while not stop_event.is_set():
            ret, frame = cap.read()
            if not ret or frame is None:
                time.sleep(0.05)
                continue

            frame_counter += 1

            key = 0xFF

            if use_gui:
                try:
                    cv2.imshow("camera_preview", frame)
                    key = cv2.waitKey(1) & 0xFF
                except Exception as e:
                    # GUI failed during runtime; switch to headless/terminal control
                    print("GUI error during preview, switching to headless mode:", e)
                    use_gui = False

            # check stdin queue for terminal commands
            while not stdin_queue.empty():
                cmd = stdin_queue.get()
                if cmd.lower() == "s":
                    save_frame(frame, args.save_dir, prefix="terminal")
                elif cmd.lower() in ("q", "quit", "exit"):
                    stop_event.set()
                    break
                else:
                    print("Unknown command from terminal:", repr(cmd))

            # manual save via window key
            if key == ord("s"):
                save_frame(frame, args.save_dir, prefix="capture")

            # auto-save every N seconds
            if args.save_every and args.save_every > 0:
                now = time.time()
                if now - last_save_time >= args.save_every:
                    save_frame(frame, args.save_dir, prefix="auto")
                    last_save_time = now

            # quit key in window
            if key == ord("q") or key == 27:
                break

            if not use_gui:
                # avoid busy spin when headless
                time.sleep(1.0 / max(1, args.fps))

    except KeyboardInterrupt:
        print("Interrupted by user")

    finally:
        stop_event.set()
        try:
            cap.release()
        except Exception:
            pass
        if use_gui:
            try:
                cv2.destroyAllWindows()
            except Exception:
                pass
        elapsed = time.time() - start_time
        avg_fps = frame_counter / elapsed if elapsed > 0 else 0.0
        print(f"Exiting. Captured frames: {frame_counter}, avg FPS: {avg_fps:.2f}")

if __name__ == "__main__":
    main()
