# ETH AI Object Detection

Train an object detector to recognize road users in adverse-weather images
using the ACDC dataset and YOLOv8. The target is to detect objects such as
people, cars, and other road users in fog, night, rain, and snow—not to classify
the weather itself.

## Project status

- The ACDC COCO-to-YOLO conversion and YOLO training steps are implemented.
- `main.py` is still a UI prototype; image selection and inference are not
  implemented yet.
- ACDC data, converted images, model weights, and training runs are local and
  are not committed to Git.

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
then saves `best.pt`, the training metrics, and the generated class config to
`My Drive/datasets/ACDC/training_output/`. The large dataset archives do not
need to be copied into this Git repository.

Training output is streamed into the notebook. At each completed epoch, the
latest and best checkpoints plus metrics are synchronized to
`training_output/checkpoints_512px_batch32_30epochs_freeze10/`. This
configuration-specific folder avoids accidentally resuming checkpoints created
with the previous, slower settings. If the Colab runtime disconnects mid-training,
rerun the notebook; after dataset conversion, its training cell resumes from
the last checkpoint saved to Drive.

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

## Next development step

Run conversion and training against the locally downloaded ACDC data, review
validation metrics and predictions, then use the resulting best checkpoint to
implement image inference in the UI.
