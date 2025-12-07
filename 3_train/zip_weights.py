!mkdir -p /content/my_model

# Copy ทุก format

!cp -r /content/runs/detect/train/weights /content/my_model/


# Zip ทั้งหมด
%cd /content
!zip -r my_model.zip my_model/