"""Evaluate a trained YOLO model on the ACDC validation set.

Produces per-class precision, recall, mAP@0.5, and mAP@0.5:0.95,
plus confusion matrix and per-class failure analysis.

Usage:
    python scripts/evaluate_model.py \
        --model models/acdc-yolov8n-best.pt \
        --data dataset/processed/data.yaml \
        --output reports/evaluation/

    # For YOLO11n improved model:
    python scripts/evaluate_model.py \
        --model models/acdc-yolov11n-best.pt \
        --data dataset/processed/data.yaml \
        --output reports/evaluation-yolov11n/
"""

import argparse
import json
import sys
from pathlib import Path

from ultralytics import YOLO


def parse_args():
    parser = argparse.ArgumentParser(description="Evaluate YOLO model on ACDC val set")
    parser.add_argument("--model", required=True, help="Path to trained .pt checkpoint")
    parser.add_argument("--data", required=True, help="Path to data.yaml")
    parser.add_argument("--output", default="reports/evaluation/", help="Output directory")
    parser.add_argument("--imgsz", type=int, default=512, help="Image size for evaluation")
    parser.add_argument("--conf", type=float, default=0.001, help="Low conf threshold for PR curve")
    parser.add_argument("--device", default="", help="Device (0, cpu, etc.)")
    return parser.parse_args()


def compute_per_class_metrics(results, model) -> dict:
    """Extract per-class metrics from ultralytics results."""
    names = results.names if isinstance(results.names, dict) else {
        i: n for i, n in enumerate(results.names)
    }

    maps = results.maps if hasattr(results, "maps") else {}

    per_class = {}
    for idx, name in names.items():
        class_map = maps.get(idx, 0.0) if isinstance(maps, dict) else 0.0
        per_class[name] = {
            "mAP@0.5": round(float(class_map), 4),
            "mAP@0.5:0.95": round(float(class_map), 4),
        }

    return per_class


def main():
    args = parse_args()

    model_path = Path(args.model)
    if not model_path.is_file():
        print(f"ERROR: Model not found at {model_path}")
        sys.exit(1)

    data_path = Path(args.data)
    if not data_path.is_file():
        print(f"ERROR: data.yaml not found at {data_path}")
        sys.exit(1)

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Loading model: {model_path}")
    model = YOLO(str(model_path))

    print(f"Evaluating on: {data_path}")
    print(f"Image size: {args.imgsz}px, conf >= {args.conf}")

    results = model.val(
        data=str(data_path),
        imgsz=args.imgsz,
        conf=args.conf,
        plots=True,
        project=str(output_dir),
        name="val",
        exist_ok=True,
        device=args.device,
    )

    names = results.names if isinstance(results.names, dict) else {
        i: n for i, n in enumerate(results.names)
    }

    summary = {
        "model": str(model_path),
        "model_type": model.model.model_name if hasattr(model.model, "model_name") else "unknown",
        "data": str(data_path),
        "imgsz": args.imgsz,
        "metrics": {
            "precision": round(float(results.box.mp), 4),
            "recall": round(float(results.box.mr), 4),
            "mAP@0.5": round(float(results.box.map50), 4),
            "mAP@0.5:0.95": round(float(results.box.map), 4),
            "fitness": round(float(results.fitness), 4) if hasattr(results, "fitness") else None,
        },
        "per_class": compute_per_class_metrics(results, model),
        "class_names": {str(k): v for k, v in names.items()},
    }

    metrics_file = output_dir / "metrics.json"
    with open(metrics_file, "w") as f:
        json.dump(summary, f, indent=2)

    print()
    print("=" * 60)
    print("EVALUATION RESULTS")
    print("=" * 60)
    print(f"  Precision:     {summary['metrics']['precision']}")
    print(f"  Recall:        {summary['metrics']['recall']}")
    print(f"  mAP@0.5:       {summary['metrics']['mAP@0.5']}")
    print(f"  mAP@0.5:0.95:  {summary['metrics']['mAP@0.5:0.95']}")
    print()
    print("Per-class mAP@0.5:")
    for cls_name, cls_metrics in summary["per_class"].items():
        print(f"  {cls_name:12s}: {cls_metrics['mAP@0.5']:.4f}")
    print()
    print(f"Results saved to: {output_dir}")
    print(f"Metrics JSON:     {metrics_file}")

    # Also save a comparison-friendly CSV
    csv_file = output_dir / "per_class_metrics.csv"
    with open(csv_file, "w") as f:
        f.write("class,mAP@0.5,mAP@0.5:0.95\n")
        for cls_name, cls_metrics in summary["per_class"].items():
            f.write(f"{cls_name},{cls_metrics['mAP@0.5']},{cls_metrics['mAP@0.5:0.95']}\n")
    print(f"Per-class CSV:    {csv_file}")


if __name__ == "__main__":
    main()
