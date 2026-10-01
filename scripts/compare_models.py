"""Compare two trained models side-by-side.

Usage:
    python scripts/compare_models.py \
        --baseline reports/evaluation/metrics.json \
        --improved reports/evaluation-yolov11n/metrics.json
"""

import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Compare two model evaluation results")
    parser.add_argument("--baseline", required=True, help="Baseline metrics.json")
    parser.add_argument("--improved", required=True, help="Improved metrics.json")
    args = parser.parse_args()

    baseline = json.loads(Path(args.baseline).read_text())
    improved = json.loads(Path(args.improved).read_text())

    b_metrics = baseline["metrics"]
    i_metrics = improved["metrics"]

    print("=" * 70)
    print("MODEL COMPARISON")
    print("=" * 70)
    print(f"{'Metric':<20} {'Baseline':>12} {'Improved':>12} {'Delta':>12}")
    print("-" * 70)

    for key in ["precision", "recall", "mAP@0.5", "mAP@0.5:0.95"]:
        b_val = b_metrics.get(key, 0)
        i_val = i_metrics.get(key, 0)
        delta = i_val - b_val
        sign = "+" if delta >= 0 else ""
        print(f"{key:<20} {b_val:>12.4f} {i_val:>12.4f} {sign}{delta:>11.4f}")

    print()
    print("Per-class mAP@0.5 comparison:")
    print(f"{'Class':<12} {'Baseline':>12} {'Improved':>12} {'Delta':>12}")
    print("-" * 70)

    b_per_class = baseline.get("per_class", {})
    i_per_class = improved.get("per_class", {})
    all_classes = sorted(set(list(b_per_class.keys()) + list(i_per_class.keys())))

    for cls in all_classes:
        b_val = b_per_class.get(cls, {}).get("mAP@0.5", 0)
        i_val = i_per_class.get(cls, {}).get("mAP@0.5", 0)
        delta = i_val - b_val
        sign = "+" if delta >= 0 else ""
        print(f"{cls:<12} {b_val:>12.4f} {i_val:>12.4f} {sign}{delta:>11.4f}")


if __name__ == "__main__":
    main()
