# ETH AI Object Detection

An early-stage Python project for exploring object detection in adverse weather
conditions using the ACDC dataset and YOLOv8.

## Project status

- `main.py` currently opens a CustomTkinter window; image selection and object
  detection are not implemented yet.
- `dataset/` contains initial COCO-to-YOLO conversion and YOLO training scripts.
- ACDC images and annotations, pretrained weights, and training outputs are
  local assets and are not committed to this repository.

## Setup

Use Python 3.10 or newer and install the project dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Start the current UI prototype with:

```powershell
python main.py
```

## Dataset and training

ACDC is distributed separately and requires registration. Download it from
the [official ACDC website](https://acdc.vision.ee.ethz.ch) and follow its
license and citation requirements. The source dataset documentation and
license are kept in [`dataset/`](dataset/).

The local data layout and class mapping still need to be finalized before
training is reproducible. `dataset/data.yaml` currently expects
`dataset/images/train` and `dataset/images/val`; those folders are intentionally
not included in Git. Do not commit downloaded data or generated training runs.

## Next development milestone

Define the intended detection classes and a reproducible ACDC-to-YOLO dataset
layout, then validate conversion and training against a small sample. Once that
pipeline is verified, connect the UI to a trained model for image inference.
