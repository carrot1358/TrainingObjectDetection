import shutil
import os
from ultralytics import YOLO

# ========================================
# Export NCNN หลายขนาด
# ========================================
model_path = f'{os.environ["HOME"]}/runs/detect/train/weights/best.pt'
model = YOLO(model_path)
base_dir = os.path.dirname(model_path)

for size in [480, 640, 800]:
    print(f"🔄 Exporting NCNN {size}...")
    model.export(format='ncnn', imgsz=size, half=True)
    
    # Rename folder
    os.rename(
        f'{base_dir}/best_ncnn_model',
        f'{base_dir}/best_ncnn_{size}'
    )
    print(f"✅ Saved: best_ncnn_{size}/")

# ========================================
# Zip โฟลเดอร์ weights ทั้งหมด
# ========================================
weights_dir = f'{os.environ["HOME"]}/runs/detect/train/weights'
zip_output = f'{os.environ["HOME"]}/runs/detect/train/weights_exported'

shutil.make_archive(zip_output, 'zip', weights_dir)
print(f"📦 Zip สำเร็จ: {zip_output}.zip")