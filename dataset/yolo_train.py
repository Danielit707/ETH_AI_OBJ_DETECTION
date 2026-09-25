import argparse
from pathlib import Path


def main():
    default_dataset = Path(__file__).resolve().parent / "processed"
    parser = argparse.ArgumentParser(description="Train a YOLO detector on the converted ACDC dataset.")
    parser.add_argument(
        "--dataset-dir",
        type=Path,
        default=default_dataset,
        help=f"Converted dataset directory (default: {default_dataset}).",
    )
    parser.add_argument("--model", default="yolov8n.pt", help="YOLO model or checkpoint to fine-tune.")
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--imgsz", type=int, default=640)
    args = parser.parse_args()

    dataset_dir = args.dataset_dir.expanduser().resolve()
    data_yaml = dataset_dir / "data.yaml"
    if not data_yaml.is_file():
        parser.error(
            f"{data_yaml} does not exist. Run dataset/run_conversion.py first to prepare the dataset."
        )
    if args.epochs <= 0 or args.imgsz <= 0:
        parser.error("--epochs and --imgsz must be positive integers.")

    from ultralytics import YOLO

    model = YOLO(args.model)
    model.train(
        data=str(data_yaml),
        epochs=args.epochs,
        imgsz=args.imgsz,
        project=str(dataset_dir / "runs"),
        name="acdc",
    )


if __name__ == "__main__":
    main()
