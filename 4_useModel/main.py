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

# ตัวแปรสำหรับเก็บเวลาที่เจอ object ล่าสุด
last_seen_time = None
last_object = None


def process_results(detector, servo):
    """
    ฟังก์ชันนี้ทำงานทุกเฟรม - ตรวจสอบว่าเจออะไรแล้วสั่ง servo
    """
    global last_seen_time, last_object

    results = detector.result()  # ดึงผลลัพธ์จาก detector
    current_time = time.time()

    # ถ้าเจอ object
    if results:
        print(json.dumps(results, indent=4))

        # วนดูแต่ละ object ที่เจอ
        for obj in results:
            object_name = obj['class_name']  # ชื่อของ object เช่น "battery", "motor"

            # ถ้าเจอ battery → servo ไปที่ 45 องศา
            if object_name == 'battery':
                if last_object != 'battery':  # เช็คว่าเป็น battery ใหม่หรือเปล่า
                    print("เจอ Battery! → ไปที่ 45°")
                    servo.move(45)  # ไปที่ 45 องศา (90 - 45)
                last_seen_time = current_time
                last_object = 'battery'
                break  # หยุดเช็ค object อื่น

            # ถ้าเจอ motor → servo ไปที่ 135 องศา
            elif object_name == 'motor':
                if last_object != 'motor':  # เช็คว่าเป็น motor ใหม่หรือเปล่า
                    print("เจอ Motor! → ไปที่ 135°")
                    servo.move(135)  # ไปที่ 135 องศา (90 + 45)
                last_seen_time = current_time
                last_object = 'motor'
                break

            # เพิ่ม object อื่นๆ ได้ที่นี่
            # elif object_name == 'person':
            #     print("เจอ Person!")
            #     servo.move(90)  # หมุนไปตรงกลาง
            #     last_seen_time = current_time
            #     last_object = 'person'
            #     break

    # ถ้าไม่เจออะไรเลย
    else:
        # ถ้าเคยเจอ object แล้วไม่เจออีก → รอ 1 วินาที แล้วกลับ home
        if last_seen_time is not None:
            time_passed = current_time - last_seen_time

            if time_passed > 1.0:  # รอ 1 วินาที
                print(" ไม่เจออะไรแล้ว → กลับ home")
                servo.home()  # กลับตำแหน่งกลาง (90 องศา)
                last_seen_time = None
                last_object = None

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
