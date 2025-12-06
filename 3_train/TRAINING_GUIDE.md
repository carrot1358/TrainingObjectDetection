# คู่มือเทรน YOLOv11 สำหรับ Raspberry Pi

## 🎯 การตั้งค่าที่แนะนำ

ใช้ **YOLO11n (Nano)** ที่ resolution **480px** พร้อม export เป็น **NCNN** และ **TFLite**

---

## 📝 แก้ไขใน Notebook

### 1. Training Command

แก้ไขใน cell ที่ train model (Section 5.2) จาก:
```bash
!yolo detect train data=/content/data.yaml model=yolo11s.pt epochs=60 imgsz=640
```

เป็น:
```bash
!yolo detect train data=/content/data.yaml model=yolo11n.pt epochs=60 imgsz=480
```

---

### 2. Export เป็น NCNN และ TFLite

**เพิ่ม cell ใหม่** หลังจากเทรนเสร็จ (หลัง Section 6 Test Model):

```python
from ultralytics import YOLO

# โหลดโมเดลที่เทรนแล้ว
model = YOLO('/content/runs/detect/train/weights/best.pt')

# ========================================
# Export 1: NCNN (เร็วที่สุดบน Raspberry Pi)
# ========================================
model.export(
    format='ncnn',
    imgsz=480,
    half=True  # FP16 สำหรับ ARM
)
print("✅ Export NCNN สำเร็จ!")

# ========================================
# Export 2: TFLite + int8 (เล็กที่สุด)
# ========================================
model.export(
    format='tflite',
    imgsz=480,
    int8=True  # int8 quantization
)
print("✅ Export TFLite สำเร็จ!")
```

---

### 3. Download Model สำหรับ Raspberry Pi

```python
# สร้างโฟลเดอร์เก็บโมเดล
!mkdir -p /content/my_model

# Copy ทุก format
!cp /content/runs/detect/train/weights/best.pt /content/my_model/
!cp -r /content/runs/detect/train/weights/best_ncnn_model /content/my_model/
!cp /content/runs/detect/train/weights/best_int8.tflite /content/my_model/

# Zip ทั้งหมด
%cd /content
!zip -r my_model.zip my_model/
```

---

## 🍓 การใช้งานบน Raspberry Pi

### ติดตั้ง Dependencies

```bash
pip install ultralytics opencv-python
```

### รัน Detector

```python
from modules.detector import ObjectDetector

# ========================================
# ทางเลือก 1: PyTorch (พัฒนา/ทดสอบ)
# ========================================
detector = ObjectDetector(weights="my_model/best.pt")

# ========================================
# ทางเลือก 2: NCNN (เร็วที่สุด - แนะนำ!)
# ========================================
detector = ObjectDetector(weights="my_model/best_ncnn_model")

# ========================================
# ทางเลือก 3: TFLite (เล็กที่สุด, รองรับ Coral TPU)
# ========================================
detector = ObjectDetector(weights="my_model/best_int8.tflite")

# เริ่มทำงาน
detector.run()
```

---

## 📊 เปรียบเทียบประสิทธิภาพ (YOLO11n @ 480px, RPi 5)

| Format | Size | FPS | หมายเหตุ |
|--------|------|-----|----------|
| PyTorch (.pt) | ~2.5 MB | ~10-15 | พัฒนา/ทดสอบ |
| **NCNN (FP16)** | **~2.5 MB** | **~25-35** | ✅ เร็วที่สุด |
| TFLite (int8) | ~1.5 MB | ~20-28 | เล็กที่สุด |
| TFLite + Coral TPU | ~1.5 MB | ~60-100 | ต้องมี hardware |

---

## ⚠️ หมายเหตุ

- **แนะนำ**: ใช้ **NCNN** สำหรับ Raspberry Pi เปล่าๆ
- **TFLite**: ดีถ้ามี Google Coral TPU หรือต้องการไฟล์เล็กที่สุด
- Resolution 480 เหมาะสำหรับวัตถุขนาดกลาง-ใหญ่
