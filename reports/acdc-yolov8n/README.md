# ACDC YOLOv8n training run

Trained on the ACDC adverse-weather object-detection train/validation split.
The ACDC dataset is licensed for non-commercial use; follow its terms when
redistributing or using this checkpoint.

## Artifacts

- `models/acdc-yolov8n-best.pt`: best Ultralytics checkpoint, retained locally
  and intentionally excluded from Git.
- [`results.csv`](results.csv): per-epoch training and validation metrics.
- [`data.yaml`](data.yaml): class-index mapping used by the run.

The model checkpoint is not required to understand the project or reproduce
the reported metrics. Retrain it using the Colab workflow and a separately
downloaded ACDC dataset if you need the weights.

## Configuration

The Colab run used the project's faster training profile: YOLOv8n pretrained
initialization, 512-pixel images, batch size 32, up to 30 epochs, patience 10,
and the first 10 layers frozen. Training stopped after epoch 30. The CSV
reports 4,476.52 seconds of cumulative training time.

## Validation results

| Metric | Best value | Epoch |
| --- | ---: | ---: |
| Precision (best epoch) | 0.5737 | 19 |
| Recall (best epoch) | 0.2561 | 28 |
| mAP@0.5 | 0.2664 | 24 |
| mAP@0.5:0.95 | 0.1538 | 24 |

These are early baseline results, not a production-ready detector. Precision
and recall above are their independent maxima; use the per-epoch CSV and
validation plots to assess tradeoffs and class-specific performance.

## Loading the checkpoint

Install the project requirements, then load the model with Ultralytics:

```python
from ultralytics import YOLO

model = YOLO("models/acdc-yolov8n-best.pt")
results = model.predict("path/to/image.png", imgsz=512)
```
