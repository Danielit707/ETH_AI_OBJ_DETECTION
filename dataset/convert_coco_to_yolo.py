import os
import json

def convert_bbox_coco_to_yolo(x, y, width, height, img_width, img_height):
    x_center = (x + width / 2) / img_width
    y_center = (y + height / 2) / img_height
    width /= img_width
    height /= img_height
    return x_center, y_center, width, height

def convert_coco_json(json_path, output_dir):
    with open(json_path, 'r') as f:
        data = json.load(f)

    images = {img['id']: img for img in data['images']}
    categories = {cat['id']: cat['name'] for cat in data['categories']}

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for ann in data['annotations']:
        image_id = ann['image_id']
        img_info = images[image_id]
        img_filename = os.path.basename(img_info['file_name'])
        img_name = os.path.splitext(img_filename)[0]
        img_width = img_info['width']
        img_height = img_info['height']

        x, y, w, h = ann['bbox']
        x_center, y_center, w_norm, h_norm = convert_bbox_coco_to_yolo(x, y, w, h, img_width, img_height)

        label_id = ann['category_id'] - 1  # YOLO class index starts at 0
        yolo_line = f"{label_id} {x_center:.6f} {y_center:.6f} {w_norm:.6f} {h_norm:.6f}\n"

        label_path = os.path.join(output_dir, f"{img_name}.txt")
        with open(label_path, 'a') as label_file:
            label_file.write(yolo_line)


