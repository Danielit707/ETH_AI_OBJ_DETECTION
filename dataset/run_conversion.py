import os
print("Conversion started")
from convert_coco_to_yolo import convert_coco_json

base_dir = "gt_detection"
weather_types = ["fog", "night", "rain", "snow"]
splits = ["train", "val"]

for weather in weather_types:
    for split in splits:
        json_path = os.path.join(base_dir, weather, f"instancesonly_{weather}_{split}_gt_detection.json")
        labels_path = os.path.join(base_dir, weather, split, "labels")
        convert_coco_json(json_path, labels_path)

print("Conversion finished")


