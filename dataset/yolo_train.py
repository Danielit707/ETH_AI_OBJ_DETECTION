import argparse
import shutil
from pathlib import Path


def _sync_training_artifacts(trainer, backup_dir):
    backup_dir.mkdir(parents=True, exist_ok=True)
    for attribute in ("last", "best", "csv"):
        source = getattr(trainer, attribute, None)
        if source is not None:
            source = Path(source)
            destination = backup_dir / source.name
            if source.is_file():
                source_stat = source.stat()
                destination_stat = destination.stat() if destination.exists() else None
                if (
                    destination_stat is None
                    or source_stat.st_size != destination_stat.st_size
                    or source_stat.st_mtime_ns != destination_stat.st_mtime_ns
                ):
                    shutil.copy2(source, destination)

    completed_epochs = trainer.epoch + 1
    print(
        f"[progress] Finished epoch {completed_epochs}/{trainer.epochs}; "
        f"checkpoint synced to {backup_dir}",
        flush=True,
    )


def main():
    default_dataset = Path(__file__).resolve().parent / "processed"
    parser = argparse.ArgumentParser(
        description="Train a YOLO detector on the converted ACDC dataset."
    )
    parser.add_argument(
        "--dataset-dir",
        type=Path,
        default=default_dataset,
        help=f"Converted dataset directory (default: {default_dataset}).",
    )
    parser.add_argument(
        "--model", default="yolov8n.pt", help="YOLO model or checkpoint to fine-tune."
    )
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--imgsz", type=int, default=512)
    parser.add_argument("--batch", type=int, default=32)
    parser.add_argument("--patience", type=int, default=10)
    parser.add_argument(
        "--freeze",
        type=int,
        default=10,
        help=(
            "Freeze the first N model layers for faster transfer learning; "
            "use 0 to train all layers."
        ),
    )
    parser.add_argument(
        "--backup-dir",
        type=Path,
        help="Copy the latest/best checkpoints and metrics here at every completed epoch.",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume training from --model, which must be an Ultralytics last.pt checkpoint.",
    )
    args = parser.parse_args()

    dataset_dir = args.dataset_dir.expanduser().resolve()
    data_yaml = dataset_dir / "data.yaml"
    if not data_yaml.is_file():
        parser.error(
            f"{data_yaml} does not exist. "
            "Run dataset/run_conversion.py first to prepare the dataset."
        )
    if (
        args.epochs <= 0
        or args.imgsz <= 0
        or args.batch <= 0
        or args.patience < 0
        or args.freeze < 0
    ):
        parser.error(
            "--epochs, --imgsz, and --batch must be positive; "
            "--patience and --freeze cannot be negative."
        )
    if args.resume and args.model == "yolov8n.pt":
        parser.error("--resume requires --model to point to an existing training checkpoint.")
    if args.resume and not Path(args.model).expanduser().is_file():
        parser.error(f"Resume checkpoint does not exist: {args.model}")

    from ultralytics import YOLO

    model = YOLO(args.model)
    if args.backup_dir:
        backup_dir = args.backup_dir.expanduser().resolve()
        model.add_callback(
            "on_fit_epoch_end",
            lambda trainer: _sync_training_artifacts(trainer, backup_dir),
        )
    model.train(
        data=str(data_yaml),
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        patience=args.patience,
        freeze=args.freeze or None,
        project=str(dataset_dir / "runs"),
        name="acdc",
        resume=args.resume,
    )


if __name__ == "__main__":
    main()
