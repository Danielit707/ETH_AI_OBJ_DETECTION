import argparse
import json
import math
import shutil
from collections import defaultdict
from pathlib import Path


CONDITIONS = ("fog", "night", "rain", "snow")
SPLITS = ("train", "val")


def convert_bbox_coco_to_yolo(bbox, image_width, image_height):
    if image_width <= 0 or image_height <= 0:
        raise ValueError("Image dimensions must be positive.")
    if len(bbox) != 4:
        raise ValueError(f"Expected a COCO bbox with four values, got {bbox!r}.")

    x, y, width, height = map(float, bbox)
    if not all(math.isfinite(value) for value in (x, y, width, height)):
        raise ValueError(f"Bounding-box values must be finite, got {bbox!r}.")
    if width <= 0 or height <= 0:
        raise ValueError(f"Bounding-box dimensions must be positive, got {bbox!r}.")

    x1 = min(max(x, 0.0), image_width)
    y1 = min(max(y, 0.0), image_height)
    x2 = min(max(x + width, 0.0), image_width)
    y2 = min(max(y + height, 0.0), image_height)
    if x2 <= x1 or y2 <= y1:
        raise ValueError(f"Bounding box lies outside the image: {bbox!r}.")

    box_width = x2 - x1
    box_height = y2 - y1
    return (
        (x1 + box_width / 2) / image_width,
        (y1 + box_height / 2) / image_height,
        box_width / image_width,
        box_height / image_height,
    )


def _read_annotations(path):
    with path.open("r", encoding="utf-8") as annotation_file:
        data = json.load(annotation_file)

    categories = data.get("categories")
    images = data.get("images")
    annotations = data.get("annotations")
    if not isinstance(categories, list) or not isinstance(images, list) or not isinstance(annotations, list):
        raise ValueError(f"{path} must contain categories, images, and annotations lists.")

    category_names = {}
    for category in categories:
        category_id = category.get("id")
        name = category.get("name")
        if (
            not isinstance(category_id, int)
            or isinstance(category_id, bool)
            or not isinstance(name, str)
            or not name.strip()
        ):
            raise ValueError(f"{path} contains an invalid category: {category!r}.")
        if category_id in category_names:
            raise ValueError(f"{path} contains duplicate category ID {category_id}.")
        category_names[category_id] = name.strip()
    if not category_names:
        raise ValueError(f"{path} does not define any detection categories.")
    return images, annotations, category_names


def _find_image(acdc_root, condition, split, file_name):
    relative_path = Path(file_name)
    candidates = (
        acdc_root / relative_path,
        acdc_root / "rgb_anon" / condition / split / relative_path.name,
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate

    image_root = acdc_root / "rgb_anon" / condition / split
    matches = list(image_root.rglob(relative_path.name)) if image_root.is_dir() else []
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        raise FileNotFoundError(
            f"Image {file_name!r} matches multiple files under {image_root}; "
            "place it at the path recorded in the COCO annotation."
        )
    raise FileNotFoundError(
        f"Could not find image {file_name!r}. Expected it under {acdc_root} or "
        f"{image_root}. Download the anonymized ACDC images and preserve their directory structure."
    )


def _write_data_yaml(output_dir, class_names):
    lines = [
        "train: images/train",
        "val: images/val",
        "",
        f"nc: {len(class_names)}",
        "names:",
    ]
    lines.extend(f"  {index}: {json.dumps(name, ensure_ascii=True)}" for index, name in enumerate(class_names))
    (output_dir / "data.yaml").write_text("\n".join(lines) + "\n", encoding="utf-8")


def convert_acdc_dataset(acdc_root, output_dir):
    acdc_root = Path(acdc_root).expanduser().resolve()
    output_dir = Path(output_dir).expanduser().resolve()
    if not acdc_root.is_dir():
        raise FileNotFoundError(f"ACDC root does not exist: {acdc_root}")

    output_files = {
        split: (
            output_dir / "images" / split,
            output_dir / "labels" / split,
        )
        for split in SPLITS
    }
    for image_dir, label_dir in output_files.values():
        image_dir.mkdir(parents=True, exist_ok=True)
        label_dir.mkdir(parents=True, exist_ok=True)

    class_ids = None
    class_names = None
    total_images = 0
    for split in SPLITS:
        image_dir, label_dir = output_files[split]
        for condition in CONDITIONS:
            annotation_path = (
                acdc_root
                / "gt_detection"
                / condition
                / f"instancesonly_{condition}_{split}_gt_detection.json"
            )
            images, annotations, categories = _read_annotations(annotation_path)
            ordered_categories = sorted(categories.items())
            if class_ids is None:
                class_ids = {category_id: index for index, (category_id, _) in enumerate(ordered_categories)}
                class_names = [name for _, name in ordered_categories]
            elif ordered_categories != sorted(
                (category_id, class_names[index])
                for category_id, index in class_ids.items()
            ):
                raise ValueError(
                    f"{annotation_path} has a different category mapping from the other ACDC splits."
                )

            annotations_by_image = defaultdict(list)
            image_ids = set()
            for annotation in annotations:
                image_id = annotation.get("image_id")
                category_id = annotation.get("category_id")
                if category_id not in class_ids:
                    raise ValueError(
                        f"{annotation_path} references unknown category ID {category_id!r}."
                    )
                annotations_by_image[image_id].append(annotation)

            for image in images:
                image_id = image.get("id")
                file_name = image.get("file_name")
                width = image.get("width")
                height = image.get("height")
                if not isinstance(image_id, int) or isinstance(image_id, bool) or not isinstance(file_name, str):
                    raise ValueError(f"{annotation_path} contains an invalid image entry: {image!r}.")
                if image_id in image_ids:
                    raise ValueError(f"{annotation_path} contains duplicate image ID {image_id!r}.")
                image_ids.add(image_id)
                if (
                    not isinstance(width, (int, float))
                    or not isinstance(height, (int, float))
                    or not math.isfinite(width)
                    or not math.isfinite(height)
                    or width <= 0
                    or height <= 0
                ):
                    raise ValueError(f"{annotation_path} has invalid dimensions for image {image_id!r}.")

                source_image = _find_image(acdc_root, condition, split, file_name)
                image_stem = f"{condition}_{image_id}"
                shutil.copy2(source_image, image_dir / f"{image_stem}{source_image.suffix.lower()}")

                label_lines = []
                for annotation in annotations_by_image.pop(image_id, []):
                    box = convert_bbox_coco_to_yolo(annotation.get("bbox", []), width, height)
                    class_index = class_ids[annotation["category_id"]]
                    label_lines.append(
                        f"{class_index} " + " ".join(f"{coordinate:.6f}" for coordinate in box)
                    )
                (label_dir / f"{image_stem}.txt").write_text(
                    "\n".join(label_lines) + ("\n" if label_lines else ""),
                    encoding="utf-8",
                )
                total_images += 1

            if annotations_by_image:
                unknown_image_ids = sorted(map(str, annotations_by_image))
                raise ValueError(
                    f"{annotation_path} has annotations for missing image IDs: "
                    f"{', '.join(unknown_image_ids[:10])}."
                )

    _write_data_yaml(output_dir, class_names)
    print(f"Converted {total_images} images into {output_dir}")
    print(f"Detected {len(class_names)} classes: {', '.join(class_names)}")


def main():
    parser = argparse.ArgumentParser(
        description="Convert ACDC COCO object-detection annotations to a combined YOLO dataset."
    )
    parser.add_argument(
        "--acdc-root",
        type=Path,
        required=True,
        help="Local ACDC dataset root containing gt_detection/ and rgb_anon/.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "processed",
        help="Generated YOLO dataset directory (default: dataset/processed).",
    )
    args = parser.parse_args()
    convert_acdc_dataset(args.acdc_root, args.output_dir)


if __name__ == "__main__":
    main()
