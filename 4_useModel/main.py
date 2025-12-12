#!/usr/bin/env python3
"""
main.py
ไฟล์หลักสำหรับ object detection + servo control
Raspberry Pi 5 ONLY
"""

# Setup GPIO for Raspberry Pi 5 (required!)
from gpiozero import Device
from gpiozero.pins.lgpio import LGPIOFactory

Device.pin_factory = LGPIOFactory()
print("[✓] lgpio initialized for Raspberry Pi 5")

from modules.detector import ObjectDetector
from modules.servo_controller import ServoController
import json
import time


def process_results(detector, servo):
    """
    ฟังก์ชันนี้ทำงานทุกเฟรม - ตรวจสอบว่าเจออะไรแล้วสั่ง servo
    """

    results = detector.result()  # ดึงผลลัพธ์จาก detector

    # ถ้าเจอ object
    if results:
        print(json.dumps(results, indent=4))

def main():
    print("=" * 50)
    print(" เริ่ม Object Detection + Servo Control")
    print("=" * 50)

    # 1. สร้าง detector สำหรับตรวจจับ object
    detector = ObjectDetector(
        weights="model/my_model/weights/best_ncnn_model",
        cam_index=0,
        imgsz=640,
        conf_threshold=0.7,
        show_window=True,
        debug=True
    )

    # 2. สร้าง servo controller
    print("\nเริ่มต้น Servo...")
    servo = ServoController(
        gpio_pin=18,      # ขา GPIO 18
        home_angle=90,    # ตำแหน่ง home = 90 องศา (ตรงกลาง)
        debug=True
    )

    # 3. เริ่มทำงาน
    try:
        print("\nพร้อมแล้ว! กด Ctrl+C เพื่อหยุด\n")

        # เริ่ม detect + ส่ง servo เข้าไปด้วย
        detector.run(callback=lambda d: process_results(d, servo))

    except KeyboardInterrupt:
        print("\nหยุดโดยผู้ใช้ (Ctrl+C)")

    finally:
        # ปิด servo
        print("ปิด Servo...")
        servo.cleanup()
        print("เสร็จสิ้น!")


if __name__ == "__main__":
    main()
