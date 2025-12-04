import sys
import time
from pathlib import Path
import cv2
from ultralytics import YOLO

class ObjectDetector:
    def __init__(self, weights="best.pt", cam_index=0, imgsz=640, conf_threshold=0.25, show_window=True, out_video="output_detect.mp4", fps=20.0, debug=False):
        self.weights = weights
        self.cam_index = cam_index
        self.imgsz = imgsz
        self.conf_threshold = conf_threshold
        self.show_window = show_window
        self.out_video = out_video
        self.fps = fps
        self.debug = debug
        
        self.model = None
        self.cap = None
        self.writer = None
        self.latest_detections = [] # เก็บผลลัพธ์ล่าสุด
        
        self._load_model()
        self._init_camera()
        self._init_writer()

    def _load_model(self):
        w = Path(self.weights)
        if not w.exists():
            print(f"[ERROR] ไม่พบไฟล์ weights: {self.weights} (วางไฟล์ไว้ในไดเรคทอรีนี้)")
            sys.exit(1)

        print("[*] โหลดโมเดลจาก", self.weights)
        self.model = YOLO(str(w))

    def _init_camera(self):
        print("[*] สร้าง VideoCapture")
        self.cap = cv2.VideoCapture(self.cam_index)
        if not self.cap.isOpened():
            print(f"[ERROR] ไม่สามารถเปิดกล้อง index={self.cam_index}")
            sys.exit(1)

    def _init_writer(self):
        if not self.show_window:
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or self.imgsz
            h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or self.imgsz
            self.writer = cv2.VideoWriter(self.out_video, fourcc, self.fps, (w, h))
            print("[*] บันทึกผลเป็น:", self.out_video)

    def result(self):
        """
        คืนค่าผลลัพธ์การตรวจจับล่าสุด
        Returns:
            list of dict: [{ 'class_id': int, 'class_name': str, 'conf': float, 'box': [x1, y1, x2, y2] }, ...]
        """
        return self.latest_detections

    def run(self, callback=None):
        """
        เริ่มการทำงานของ detector
        Args:
            callback (function): ฟังก์ชันที่จะถูกเรียกในแต่ละเฟรม (รับ argument เป็น instance ของ ObjectDetector)
        """
        print("[*] เริ่มจับภาพ (กด Ctrl+C เพื่อหยุด)")
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    print("[WARN] ไม่สามารถอ่านเฟรมจากกล้องได้ — หยุด")
                    break

                # ปรับขนาดสำหรับความเร็ว (ไม่บังคับ)
                h, w = frame.shape[:2]
                if max(h, w) > self.imgsz:
                    scale = self.imgsz / max(h, w)
                    frame_small = cv2.resize(frame, (int(w*scale), int(h*scale)))
                else:
                    frame_small = frame
                    scale = 1.0

                # ทำ inference
                # verbose=False เพื่อปิด log ของ YOLO
                results = self.model(frame_small, imgsz=self.imgsz, conf=self.conf_threshold, device='cpu', verbose=False)

                # ประมวลผลผลลัพธ์เพื่อเก็บใน self.latest_detections
                self.latest_detections = []
                if len(results) > 0:
                    for box in results[0].boxes:
                        # box.xyxy[0] คือพิกัด [x1, y1, x2, y2] บนภาพ frame_small
                        x1, y1, x2, y2 = box.xyxy[0].tolist()
                        conf = float(box.conf[0])
                        cls = int(box.cls[0])
                        class_name = self.model.names[cls]
                        
                        # แปลงพิกัดกลับเป็นขนาดภาพจริงถ้ามีการย่อ
                        if scale != 1.0:
                            x1, x2 = x1 / scale, x2 / scale
                            y1, y2 = y1 / scale, y2 / scale

                        self.latest_detections.append({
                            'class_id': cls,
                            'class_name': class_name,
                            'conf': conf,
                            'box': [x1, y1, x2, y2]
                        })

                # Debug print
                if self.debug:
                    if len(self.latest_detections) > 0:
                        print(f"[DEBUG] Found {len(self.latest_detections)} objects")
                    else:
                        print("[DEBUG] No detections")

                # เรียก callback ถ้ามี
                if callback:
                    callback(self)

                # ใช้ plot() เพื่อได้ภาพที่วาดกล่องแล้ว
                annotated = results[0].plot()

                # upscale กลับเป็นขนาดเต็ม (ถ้าจำเป็น)
                if annotated.shape[:2] != frame.shape[:2]:
                    annotated = cv2.resize(annotated, (frame.shape[1], frame.shape[0]))

                if self.show_window:
                    cv2.imshow("Detect (press q to quit)", annotated)
                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        print("[*] หยุดโดยผู้ใช้ (q)")
                        break
                else:
                    self.writer.write(annotated)

        except KeyboardInterrupt:
            print("\n[*] หยุดโดยผู้ใช้ (KeyboardInterrupt)")
        finally:
            self.cleanup()

    def cleanup(self):
        if self.cap:
            self.cap.release()
        if self.writer:
            self.writer.release()
        cv2.destroyAllWindows()
        print("[*] เสร็จแล้ว")
