import json
import tempfile
import unittest
from types import SimpleNamespace
from pathlib import Path

from dataset.convert_coco_to_yolo import convert_acdc_dataset, convert_bbox_coco_to_yolo
from dataset.yolo_train import _sync_training_artifacts


class ACDCConversionTests(unittest.TestCase):
    def test_bbox_is_normalized_and_clipped_to_image(self):
        box = convert_bbox_coco_to_yolo([-2, 2, 8, 8], 10, 10)
        self.assertEqual(box, (0.3, 0.6, 0.6, 0.8))

    def test_bbox_rejects_zero_area(self):
        with self.assertRaises(ValueError):
            convert_bbox_coco_to_yolo([0, 0, 0, 1], 10, 10)

    def test_conversion_combines_conditions_and_generates_matching_class_map(self):
        conditions = ("fog", "night", "rain", "snow")
        splits = ("train", "val")
        categories = [{"id": 4, "name": "car"}, {"id": 9, "name": "person"}]

        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory) / "acdc"
            output = Path(temporary_directory) / "processed"
            for condition in conditions:
                for split in splits:
                    image_dir = root / "rgb_anon" / condition / split / "sequence"
                    image_dir.mkdir(parents=True)
                    (image_dir / "frame.png").write_bytes(b"image")

                    annotation_dir = root / "gt_detection" / condition
                    annotation_dir.mkdir(parents=True, exist_ok=True)
                    annotations = []
                    if condition == "fog" and split == "train":
                        annotations.append(
                            {
                                "image_id": 1,
                                "category_id": 9,
                                "bbox": [-2, 2, 8, 8],
                            }
                        )
                    annotation_data = {
                        "categories": categories,
                        "images": [
                            {
                                "id": 1,
                                "file_name": f"{condition}/{split}/sequence/frame.png",
                                "width": 10,
                                "height": 10,
                            }
                        ],
                        "annotations": annotations,
                    }
                    annotation_path = (
                        annotation_dir
                        / f"instancesonly_{condition}_{split}_gt_detection.json"
                    )
                    annotation_path.write_text(json.dumps(annotation_data), encoding="utf-8")

            convert_acdc_dataset(root, output)

            self.assertEqual(
                (output / "labels" / "train" / "fog_1.txt").read_text(encoding="utf-8"),
                "1 0.300000 0.600000 0.600000 0.800000\n",
            )
            self.assertEqual(
                (output / "labels" / "val" / "night_1.txt").read_text(encoding="utf-8"),
                "",
            )
            self.assertTrue((output / "images" / "train" / "fog_1.png").is_file())
            self.assertEqual(
                (output / "data.yaml").read_text(encoding="utf-8"),
                'train: images/train\n'
                'val: images/val\n'
                '\n'
                'nc: 2\n'
                'names:\n'
                '  0: "car"\n'
                '  1: "person"\n',
            )

    def test_training_artifacts_are_synced_to_backup_directory(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            run_dir = root / "run"
            backup_dir = root / "drive_backup"
            run_dir.mkdir()
            checkpoint_paths = [run_dir / "last.pt", run_dir / "best.pt", run_dir / "results.csv"]
            for path in checkpoint_paths:
                path.write_text(path.name, encoding="utf-8")

            trainer = SimpleNamespace(
                last=checkpoint_paths[0],
                best=checkpoint_paths[1],
                csv=checkpoint_paths[2],
                epoch=2,
                epochs=50,
            )
            _sync_training_artifacts(trainer, backup_dir)

            for path in checkpoint_paths:
                self.assertEqual(
                    (backup_dir / path.name).read_text(encoding="utf-8"),
                    path.name,
                )


if __name__ == "__main__":
    unittest.main()
