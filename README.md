# ETH AI Object Detection

Train an object detector to recognize road users in adverse-weather images
using the ACDC dataset and YOLOv8. The target is to detect objects such as
people, cars, and other road users in fog, night, rain, and snow—not to classify
the weather itself.

## Project status

- The ACDC COCO-to-YOLO conversion and YOLO training steps are implemented.
- `api/` provides a FastAPI health endpoint and image inference endpoint.
- `main.py` is a desktop client that submits images to the running API.
- ACDC data, converted images, and full training runs remain local; only the
  small training report and metrics are retained in the repository. Model
  checkpoints stay local and are ignored by Git.
- The completed baseline checkpoint and its metrics are documented under
  [`reports/acdc-yolov8n/`](reports/acdc-yolov8n/); the checkpoint itself is
  kept locally and excluded from Git.
- Docker packages the API without bundling the model; mount your local
  checkpoint at runtime.

## Setup

Use Python 3.10 or newer and install the project dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### Run the inference API with Docker

The API expects your local checkpoint at
`models/acdc-yolov8n-best.pt`. The trained model is intentionally not in Git;
train it with the Colab workflow above or place your own compatible checkpoint
at that path. Build and run the container:

```powershell
docker compose up --build
```

Check health at `http://localhost:8000/health` and interactive API docs at
`http://localhost:8000/docs`. Upload an image for prediction:

```powershell
curl.exe -X POST "http://localhost:8000/predict?confidence=0.25&image_size=512" `
  -F "image=@D:\path\to\scene.png"
```

The JSON response includes image dimensions and detections with the class ID,
class name, confidence, and pixel-coordinate bounding box. Uploads are limited
to 10 MiB and JPEG, PNG, or WebP. If the model is missing or fails to load,
prediction returns HTTP 503 with the reason; `/health` reports whether the
model is loaded.

Run the desktop client in another terminal:

```powershell
python main.py
```

Set `DETECTION_API_URL` if the API is not at `http://127.0.0.1:8000`. The
container is CPU-based by default; CPU inference may be slow. GPU-enabled
Docker requires a compatible NVIDIA driver and NVIDIA Container Toolkit.

If you only want the desktop client in a local virtual environment (with the
API running in Docker), install its smaller dependency set instead:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-ui.txt
python main.py
```

### Run tests

```powershell
python -m pip install -r requirements-test.txt
python -m pytest -q
```

## Dataset and training

ACDC is distributed separately and requires registration. Download it from
the [official ACDC website](https://acdc.vision.ee.ethz.ch) and follow its
license and citation requirements. The source dataset documentation and
license are kept in [`dataset/`](dataset/).

### Train with Google Colab

For training from Google Drive, open
[`notebooks/train_acdc_colab.ipynb`](notebooks/train_acdc_colab.ipynb) in
Google Colab and select a GPU runtime. Put the downloaded archives in
`My Drive/datasets/ACDC/`:

```text
datasets/ACDC/
  gt_detection/gt_detection_trainval.zip
  rgb_anon/rgb_anon_trainvaltest.zip
```

Run the notebook from top to bottom. It extracts the labeled adverse-weather
train/validation data to Colab's temporary disk, converts and trains there,
then saves the best checkpoint under
`My Drive/datasets/ACDC/training_output/models/` and the training metrics and
class config under `My Drive/datasets/ACDC/training_output/reports/`. The large
dataset archives and model weights do not need to be copied into this Git
repository.

Training output is streamed into the notebook. At each completed epoch, the
latest and best checkpoints plus metrics are synchronized to
`training_output/checkpoints_512px_batch32_30epochs_freeze10/`. This
configuration-specific folder avoids accidentally resuming checkpoints created
with the previous, slower settings. If the Colab runtime disconnects mid-training,
rerun the notebook; after dataset conversion, its training cell resumes from
the last checkpoint saved to Drive.

### Completed baseline

The first 30-epoch run reached mAP@0.5 of 0.2664 and mAP@0.5:0.95 of 0.1538
(both at epoch 24). See the [training report](reports/acdc-yolov8n/README.md)
and [epoch metrics](reports/acdc-yolov8n/results.csv). The trained checkpoint
is kept locally at `models/acdc-yolov8n-best.pt` and intentionally excluded
from Git. To obtain or reproduce a checkpoint, train on your separately
downloaded ACDC dataset using the Colab notebook. Because ACDC is
non-commercially licensed, follow the dataset terms for checkpoint
redistribution and usage.

### Train locally

The ACDC directory supplied to the scripts must contain:

```text
<acdc-root>/
  gt_detection/{fog,night,rain,snow}/
  rgb_anon/{fog,night,rain,snow}/{train,val}/
```

Convert the four weather conditions into one YOLO dataset. The converter reads
the category IDs and names from the ACDC annotations, checks that they agree
across conditions and splits, and writes the matching `data.yaml`:

```powershell
python dataset/run_conversion.py --acdc-root "D:\datasets\ACDC"
```

The converted dataset is written to `dataset/processed/` by default and
contains separate train/validation images and labels. Original data and
generated files are ignored by Git. To use another output directory, pass
`--output-dir`.

Train the nano model for up to 30 epochs at 512 pixels, with batch size 32,
early stopping after 10 unimproved epochs, and the first 10 layers frozen:

```powershell
python dataset/yolo_train.py
```

Set `--dataset-dir`, `--model`, `--epochs`, `--imgsz`, `--batch`, `--patience`,
and/or `--freeze` to override the defaults. Use `--freeze 0` to train all
layers. Training results are saved under `dataset/processed/runs/`.

## Next development steps

1. Run the API container locally with the private checkpoint mounted; verify
   health and predictions on representative images from each weather condition.
2. Add an annotated-image response or a web UI so detections can be inspected
   visually, not just as JSON.
3. Improve the baseline using per-class metrics and failure analysis before
   describing it as production-ready.
