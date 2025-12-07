#!/usr/bin/env python3
"""
main.py
Main entry point for object detection.
"""

from modules.detector import ObjectDetector
import json

def process_results(detector):
    """
    Callback function ที่จะถูกเรียกทุกเฟรม
    """
    results = detector.result()
    if results:
        # ถ้าอยาก print เฉพาะตอนเจอของ ก็ทำได้ที่นี่
        # แต่ถ้าเปิด debug=True ใน ObjectDetector มันจะ print บอกว่าเจอเท่าไหร่ให้อยู่แล้ว
        
        print(json.dumps(results, indent=4))
        # ตัวอย่างการดึงค่า
        # for item in results:
        #     print(f"   -> {item['class_name']} ({item['conf']:.2f})")
    else:
        pass

def main():
    # สามารถปรับค่า config ได้ที่นี่
    detector = ObjectDetector(
        weights="model/my_model/best.pt",
        cam_index=0,
        imgsz=640,
        conf_threshold=0.1,
        show_window=True,
        debug=True # ตั้งเป็น False ถ้าไม่อยากเห็น log อะไรเลย (นอกจากที่สั่ง print เอง)
    )
    
    # ส่ง function callback เข้าไปทำงานด้วย
    detector.run(callback=process_results)

if __name__ == "__main__":
    main()
