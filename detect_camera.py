#!/usr/bin/env python3
"""
detect_camera.py
เปิดกล้อง แล้วใช้ best.pt (Ultralytics YOLO) ทำ object detection
รองรับการแสดงผลด้วย cv2.imshow หรือบันทึกเป็นไฟล์ถ้า run headless
"""

import sys
import time
from pathlib import Path

import cv2
from ultralytics import YOLO

# ตั้งค่า
WEIGHTS = "best.pt"  # เปลี่ยนถ้าจำเป็น
CAM_INDEX = 0        # หรือ '/dev/video0'
IMGSZ = 640          # ขนาดภาพสำหรับ inference (ยิ่งเล็ก ยิ่งเร็ว)
SHOW_WINDOW = True   # ถ้าไม่มี X server ให้ตั้งเป็น False เพื่อบันทึกวิดีโอแทน
OUT_VIDEO = "output_detect.mp4"
FPS = 20.0

def main():
    # เช็คไฟล์ weights
    w = Path(WEIGHTS)
    if not w.exists():
        print(f"[ERROR] ไม่พบไฟล์ weights: {WEIGHTS} (วางไฟล์ไว้ในไดเรคทอรีนี้)")
        sys.exit(1)

    print("[*] โหลดโมเดลจาก", WEIGHTS)
    model = YOLO(str(w))  # โหลด model

    # พยายามเลือก device อัตโนมัติ (ultralytics ใช้ torch ในเบื้องหลัง)
    # โดย default จะใช้ CPU ถ้าไม่มี GPU
    print("[*] สร้าง VideoCapture")
    cap = cv2.VideoCapture(CAM_INDEX)
    if not cap.isOpened():
        print(f"[ERROR] ไม่สามารถเปิดกล้อง index={CAM_INDEX}")
        sys.exit(1)

    # เตรียม VideoWriter ถ้าไม่แสดงหน้าจอ
    writer = None
    if not SHOW_WINDOW:
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or IMGSZ
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or IMGSZ
        writer = cv2.VideoWriter(OUT_VIDEO, fourcc, FPS, (w, h))
        print("[*] บันทึกผลเป็น:", OUT_VIDEO)

    print("[*] เริ่มจับภาพ (กด Ctrl+C เพื่อหยุด)")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("[WARN] ไม่สามารถอ่านเฟรมจากกล้องได้ — หยุด")
                break

            # ปรับขนาดสำหรับความเร็ว (ไม่บังคับ)
            h, w = frame.shape[:2]
            if max(h, w) > IMGSZ:
                scale = IMGSZ / max(h, w)
                frame_small = cv2.resize(frame, (int(w*scale), int(h*scale)))
            else:
                frame_small = frame

            # ทำ inference — คืนค่า results (list) โดย results[0] คือสำหรับภาพนี้
            # กำหนด device='cpu' หรือ 'cuda' หากมี
            results = model(frame_small, imgsz=IMGSZ, device='cpu')  # เปลี่ยน device เป็น 'cuda' ถ้ามี GPU

            # ใช้ plot() เพื่อได้ภาพที่วาดกล่องแล้ว (numpy image)
            annotated = results[0].plot()

            # ถ้เราได้ย่อภาพไว้ ให้ upscale กลับเป็นขนาดเต็ม (ไม่บังคับ)
            if annotated.shape[:2] != frame.shape[:2]:
                annotated = cv2.resize(annotated, (frame.shape[1], frame.shape[0]))

            if SHOW_WINDOW:
                cv2.imshow("Detect (press q to quit)", annotated)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    print("[*] หยุดโดยผู้ใช้ (q)")
                    break
            else:
                writer.write(annotated)

    except KeyboardInterrupt:
        print("\n[*] หยุดโดยผู้ใช้ (KeyboardInterrupt)")

    finally:
        cap.release()
        if writer:
            writer.release()
        cv2.destroyAllWindows()
        print("[*] เสร็จแล้ว")

if __name__ == "__main__":
    main()
