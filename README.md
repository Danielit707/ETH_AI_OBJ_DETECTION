# ETH AI Object Detection

[![CI](https://github.com/Danielit707/ETH_AI_OBJ_DETECTION/actions/workflows/ci.yml/badge.svg)](https://github.com/Danielit707/ETH_AI_OBJ_DETECTION/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Next.js 14](https://img.shields.io/badge/next.js-14-black.svg)](https://nextjs.org)
[![License: ACDC Non-Commercial](https://img.shields.io/badge/license-ACDC%20Non--Commercial-red.svg)](License.pdf)

Object detection for road users in adverse-weather conditions. Trains a
YOLO model on the ACDC dataset and deploys it through a FastAPI inference
service with both a desktop client and a modern Next.js web interface.

![Example detection](images/val_batch0_pred.jpg)

## What this project does

- **Converts** ACDC COCO-format annotations to YOLO format (all 4 weather conditions)
- **Trains** YOLO11n on ~37,000 adverse-weather road images (8 classes: person, rider, car, truck, bus, train, motorcycle, bicycle)
- **Deploys** a FastAPI inference API with Docker (CPU or GPU)
- **Provides** a Next.js web UI with visual bounding-box overlay, confidence controls, and class filtering
- **Supports** test-time augmentation (TTA) for improved accuracy

## Quick start

### Run the API

```powershell
docker compose up --build
```

- Health check: `http://localhost:8000/health`
- API docs: `http://localhost:8000/docs`

### Run the web UI

```powershell
cd web
npm install
npm run dev
```

Open `http://localhost:3000` — the UI includes real ACDC sample images for
one-click testing.

### Run the desktop client

```powershell
python -m pip install -r requirements-ui.txt
python main.py
```

## Deploy a public web app

The recommended setup hosts the FastAPI inference service on Render and the
Next.js frontend on Vercel. The model checkpoints in `models/` are local-only
and are not committed to Git, so the API downloads its checkpoint from a
private Hugging Face model repository on its first prediction.

1. Create a **private model repository** on Hugging Face and upload
   `models/acdc-yolov11n-best.pt`. Create a read token with access to that
   repository. Keep the repository private and the token secret.
2. In Render, choose **New > Blueprint**, connect this GitHub repository, and
   deploy the `render.yaml` blueprint. It creates a Docker API service with a
   persistent disk. The blueprint uses Render's paid Standard instance for
   CPU inference; check Render's current pricing before deploying.
3. In the Render service's environment settings, set:
   - `MODEL_URL` to the Hugging Face file URL:
     `https://huggingface.co/<account>/<private-repo>/resolve/main/acdc-yolov11n-best.pt`
   - `MODEL_DOWNLOAD_TOKEN` to the Hugging Face read token.
   - Keep `MODEL_PATH` as `/models/acdc-yolov11n-best.pt`.
   Save and redeploy. On the first prediction, the service downloads the
   checkpoint to its persistent disk.
4. In Vercel, import this repository as a project and set its **Root
   Directory** to `web`. Add the environment variable `DETECTION_API_URL` with
   the Render API's service URL (for example, `https://your-api.onrender.com`),
   then deploy or redeploy.
5. Open the Vercel deployment URL, check that the API indicator is online, and
   run a prediction. The first request may take longer while the model loads.
   Vercel Functions limit request bodies to 4.5 MB, even though the API itself
   accepts images up to 10 MiB. To process larger uploads, host the Next.js app
   on a Node service (for example, Render) instead of routing uploads through
   Vercel Functions.

The ACDC dataset and trained weights are licensed for non-commercial use only.
Ensure your deployment and use comply with [License.pdf](License.pdf).

## Project structure

```
api/                  FastAPI inference service
  main.py             /health and /predict endpoints
  inference.py        Lazy-loading, thread-safe model wrapper
  tta.py              Test-time augmentation (multi-scale + flip)
dataset/              ACDC conversion and training scripts
  convert_coco_to_yolo.py
  yolo_train.py
  run_conversion.py
docs/                 Project documentation
images/               Example predictions and visualizations
models/               Trained checkpoints (local, gitignored)
  acdc-yolov8n-best.pt   Baseline YOLOv8n (mAP@0.5 = 0.2664)
  acdc-yolov11n-best.pt  Improved YOLO11n (mAP@0.5 = 0.2906)
notebooks/            Colab training notebooks
reports/              Training metrics and evaluation results
scripts/              Evaluation and comparison tools
tests/                pytest test suite
web/                  Next.js web interface
main.py               CustomTkinter desktop client
compose.yaml          Docker Compose configuration
Dockerfile            CPU-only inference container
```

## Model performance

| Model | mAP@0.5 | mAP@0.5:0.95 | Precision | Recall |
|---|---|---|---|---|
| YOLOv8n (baseline) | 0.2664 | 0.1538 | 0.5737 | 0.2561 |
| YOLO11n (improved) | 0.2906 | 0.1611 | 0.4701 | 0.2998 |

Both models are trained on the full ACDC dataset (fog, night, rain, snow) at
512px resolution. The YOLO11n checkpoint was trained for 50 epochs with AdamW,
cosine LR, mixup, and copy-paste augmentation.

## Training

### With Google Colab (recommended)

Open [`notebooks/train_acdc_yolov11n_colab.ipynb`](notebooks/train_acdc_yolov11n_colab.ipynb)
in Colab with a T4 GPU runtime. Training takes ~1 hour and produces a
checkpoint with ~3 point mAP improvement over the baseline.

### Local training

```powershell
python dataset/run_conversion.py --acdc-root "D:\datasets\ACDC"
python dataset/yolo_train.py --model yolo11n.pt --epochs 50 --imgsz 512 --batch 32
```

### Evaluate

```powershell
python scripts/evaluate_model.py --model models/acdc-yolov11n-best.pt --data dataset/processed/data.yaml
```

## API usage

```powershell
curl.exe -X POST "http://localhost:8000/predict?confidence=0.05&image_size=512" `
  -F "image=@D:\path\to\scene.png"
```

| Parameter | Default | Description |
|---|---|---|
| `confidence` | 0.05 | Confidence threshold (0-1) |
| `image_size` | 512 | Inference resolution (32-1280) |
| `use_tta` | false | Enable test-time augmentation |

## Testing

```powershell
python -m pip install -r requirements-test.txt
python -m pytest -q
```

30 tests covering the API, inference service, dataset conversion, and UI.

## License

The ACDC dataset and trained model weights are subject to the
[ACDC License](License.pdf) (non-commercial use). The source code is provided
for research and educational purposes.
